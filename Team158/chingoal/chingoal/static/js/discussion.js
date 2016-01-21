
function populateList() {
    $.get("get_posts")
        .done(function(data) {
            var postDiv = $('#post_table > tbody');
            postDiv.html('');
            for (var i = 0; i < data.posts.length; i ++) {
                var post = data.posts[i];
                var post_html = $(post.html);
                $('.list_number_col').html(post.id);
                $('.number_replies_col').html(post.number_replies);
                postDiv.append(post_html);
            }
        });
}


function new_reply_clicked(e) {
    e.preventDefault();
    var dt = new Date();
    var date_str = dt.toLocaleDateString();
    var time_str = dt.toLocaleTimeString('en-US', { hour12: false });
    var post_time = date_str + ' ' + time_str;

    var reply_text = $('#replyText')

    $.post('post_reply', {'reply_text': reply_text})
        .done(function(data) {
            var replyDiv = $('#replyDiv');
            var reply_html = $(data.reply.html);
            console.log(data.reply.html);
            replyDiv.append(reply_html);
    });

    $('#myModal').modal('hide');
}


function new_post_clicked(e) {
    e.preventDefault();
    
    var dt = new Date();
    var date_str = dt.toLocaleDateString();
    var time_str = dt.toLocaleTimeString('en-US', { hour12: false });
    var post_time = date_str + ' ' + time_str;

    var post_title = $('#postTitle').val();
    var post_text = $('#postText').val();

    $.post('post_post', {'title': post_title, 'text': post_text, 'post_time':post_time})
        .done(function(data) {
            var postDiv = $('#post_table');
            var post_html = $(data.html);
            var listLen = $('#post_table > tbody').children().length
            postDiv.prepend(post_html);
            $('#post_table > tbody').find('td:first').html(listLen + 1)
            $('#post_table > tbody').find('tr:first').find('td:last').html(0)
    });

    $('#myModal').modal('hide');
}


$(document).ready(function() {
    populateList();

    // $('#myModalLabel').on('click', new_post_clicked)                            //TODO -- add listener
    $('#postBtn').on('click', new_post_clicked);
    $('#replyBtn').on('click', new_reply_clicked);

    window.setInterval(populateList, 30000);

    function getCookie(name) {  
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });
});