#-*- coding:utf-8 -*-

import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import create_app, db
from app.models import User, Follow, Role, Permission, Post, Comment, Category
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Follow = Follow,
                Permission=Permission, Post=Post, Comment=Comment, Category=Category)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler"""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], 
                                        profile_dir=profile_dir)
    app.run()
    
    
@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Role, User
    upgrade()
    Role.insert_roles()
    User.add_self_follows()
    Category.insert_categories()

    
    
if __name__ == '__main__':
    manager.run()