$(document).ready(function(){
        var the_width=Number($(window).width());
        if(the_width<970){
            $(".share").css("display","none");
        }
        $(".article").fadeIn(1100);
        $(".article img").addClass("img-responsive");
        
        $(".article").mouseover(function(){
            $(this).css({"box-shadow":'5px 5px 20px #6C6969'});
        });
        $(".article").mouseout(function(){
            $(this).css({'box-shadow':"5px 5px 20px #A7A3A3"});
        });
        
        $(".form-btn").click(function(){
            $("#category").val($(this).text());
            $(".form-btn").addClass("btn-info");
            $(".form-add").addClass("btn-info");
            $(".form-add").removeClass("btn-inverse");
            $(".form-btn").removeClass("btn-inverse");
            $(this).removeClass("btn-info");
            $(this).addClass('btn-inverse');
            $("#form_category").css("display","none");
            
        });
        $(".form-add").click(function(){
            $("#form_category").css("display","block");
            $(".form-btn").addClass("btn-info");
            $(".form-add").addClass("btn-info");
            $(".form-add").removeClass("btn-inverse");
            $(".form-btn").removeClass("btn-inverse");
            $(this).removeClass("btn-info");
            $(this).addClass('btn-inverse');
        });
        $(".button-rounded").click(function(){
            $("#category_alert").css("display","block");
        });
        
        $(".label").mouseover(function(){
            $(this).addClass('label-warning');
        });
        $(".label").mouseout(function(){
            $(this).removeClass("label-warning");
        });
    })
