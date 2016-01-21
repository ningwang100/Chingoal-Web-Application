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

function getUpdates() {
    var frm = $("#storedata")
    var pb = $("#pbody")
    var max = $("#maxentry").val();
    var qnum = $("#qnum").val();
       $.ajax({
      type: "POST",
      url: "/testpage/next-questions",
      data: frm.serialize(),
      success: function (data) {
          var body = $("#pbody");
          var newitem = $(data.html);
          if(data.flag==1 && data.max_entry < data.qnum){
            pb.html(newitem);
            $("#maxentry").val(data.max_entry.toString());
            $("#qnum").val(data.qnum.toString());
            $("#qid").val(data.id.toString());
            var percent = 100;
            $("#processbar").attr("style","width: "+percent+"%;");
            $("#processbar").html(percent+"%");
            var btn = $( ".next-btn" );
            btn.unbind( "click", getUpdates );
            // btn.bind( "click", getResult );
            btn.attr("type","submit");
            btn.addClass( "btn-info" );
            btn.removeClass( "btn-warning" );
            btn.html("Finish");
          }
          else{
            pb.html(newitem);
            $("#maxentry").val(data.max_entry.toString());
            $("#qnum").val(data.qnum.toString());
            $("#qid").val(data.id.toString());
            $(".question-num").html(data.qnum.toString());
            var percent = (data.qnum-1)/data.max_entry*100;
            percent = percent.toPrecision(3);
            $("#processbar").attr("style","width: "+percent+"%;");
            $("#processbar").html(percent+"%");
          }
            },
            error: function(data) {
                alert("Something went wrong!");
            }
        });
}


function getResult() {

}

function blockdefault(e) {
    e.which = e.which || e.keyCode;
    if(e.which == 13) {
      e.preventDefault();
      return false;
        // submit
    }
}


$(document).ready(function () {
  $( ".next-btn" ).bind( "click", getUpdates );
  $(window).on('keydown',blockdefault);
  getUpdates();
  var csrftoken = getCookie('csrftoken');
  $(".needcsrf").val(csrftoken);
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  });
});
