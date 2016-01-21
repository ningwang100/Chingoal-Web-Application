
function populateList() {
    $.get("get_posts")
        .done(function(data) {
            var postDiv = $('#post_table');
            postDiv.html('');
            for (var i = 0; i < data.posts.length; i ++) {
                var post = data.posts[i];
                var post_html = $(post.html);
                postDiv.append(post_html);
                for (var j = 0; j < post.replies.length; j ++) {
                    var reply = post.replies[j];
                    var reply_html = $(reply.html);
                    postDiv.append(reply_html);
                }
            }
        });
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
            postDiv.prepend(post_html);
    });

    $('#myModal').modal('hide');
}


function populateReply() {
    var post_id = $('#hidden_post_id').html();
    var max_reply_id = $('#hidden_max_reply_id').html();
    $.get('get_postreply/' + post_id + '/' + max_reply_id)
        .done(function(data) {
            var replyDiv = $('#replyDiv');
            for (var i = 0; i < data.replies.length; i ++) {
                var replyTemp = data.replies[i];
                var replyHtml = $(replyTemp.html);
                replyDiv.append(replyHtml);
            }
        });
}

function new_reply_clicked(e) {
    e.preventDefault();

    var dt = new Date();
    var date_str = dt.toLocaleDateString();
    var time_str = dt.toLocaleTimeString('en-US', { hour12: false });
    var post_time = date_str + ' ' + time_str;

    var reply_text = $('#replyText').val();
    var post_id = $('#hidden_post_id').html();

    var photo_url = ''

    $.post('post_reply', {'text' : reply_text, 'post_time' : post_time, 'post_id' : post_id})
        .done(function(data) {
            var replyDiv = $('#replyDiv');
            var replyHtml = $(data.html);
            replyDiv.append(replyHtml);
            // photo_url = data.user_photo_url;
            // $(replyHtml).find('#reply_user_profile_img').attr('src', photo_url);
            
        });
    

    $('#myModal').modal('hide');
}


function delete_reply_clicked() {
    var bigDiv = $(event.target).parent().parent().parent();
    console.log(bigDiv);
    var first = bigDiv.find('#hidden_reply_id')
    console.log(first);
    var reply_id = $(first).html();
    console.log(reply_id);
    $.ajax ({
        type:"POST",
        url:"delete_reply/" + reply_id,
        success: function(data) {
            bigDiv.remove(); 
        },
        error: function(data) {
            console.log('Error deleteing reply');
        }
        });
    // $.post('delete_reply/' + reply_id)
    //     .done(function(data) {
                       
    //     });    
}



$(document).ready(function() {

    populateReply();
    $('#replyBtn').on('click', new_reply_clicked);
    $('#replyDiv').on('click', '.fa', delete_reply_clicked)

    window.setInterval(populateReply, 30000);

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