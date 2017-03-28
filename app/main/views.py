#-*- coding:utf-8 -*-

from flask import render_template, abort, flash, redirect, url_for, request, current_app, make_response, g
from . import main
from ..models import Role, User, Permission, Post, Follow, Comment, Category
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from flask_login import current_user, login_required
from .. import db
from ..decorators import admin_required, permission_required
from flask_sqlalchemy import get_debug_queries


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(title=form.title.data, 
                    category=Category.query.get(form.category.data),
                    body=form.body.data,
                    summury=form.summury.data,
                    author=current_user._get_current_object()) 
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, 
                            pagination=pagination)


@main.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page',1,type=int)
    pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('category.html',category=category,posts=posts,pagination=pagination)
                            
                            
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, 
                            pagination=pagination)

                            
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'你的资料已更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

    
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(u'资料已更新')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

    
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                            post=post,
                            author=current_user._get_current_object())
        db.session.add(comment)
        flash(u'留言成功')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() -1) / \
                current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], 
        error_out=False)
    comments = pagination.items
    return render_template('post.html', post=post, form=form,
                            comments=comments, pagination=pagination)

    
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.body=form.body.data
        post.summury=form.summury.data
        post.category=Category.query.get(form.category.data)
        db.session.add(post)
        flash(u'文章已更新')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.summury.data = post.summury
    form.category.data = post.category_id
    return render_template('edit_post.html', form=form)
    
  
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注过此用户')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'成功关注 %s.' % username)
    return redirect(url_for('.user', username=username))  

    
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'你还没关注此用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'你取消了关注 %s' % username)
    return redirect(url_for('.user', username=username))

    
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
                for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of", 
                            endpoint='.followers', follows=follows, 
                            pagination=pagination)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
                for item in pagination.items]
    return render_template('followers.html', user=user, title="Following ", 
                            endpoint='.followers', follows=follows, 
                            pagination=pagination)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                            pagination=pagination, page=page)
                            
                            
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate', 
                            page=request.args.get('page', 1, type=int)))

                            
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

    
@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeng.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'shutting down...'


@main.route('/about',methods=['GET'])
def about_me():
	return render_template('about_me.html')
    
    
@main.before_app_request
def before_request(): 
    g.categories=Category.query.all()
    
    
@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %s\nContext: %s\n'
                %(query.statement, query.parameters, query.duration, 
                    query.context))
    return response
    