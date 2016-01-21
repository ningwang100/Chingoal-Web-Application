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



function getresult(){
    var len = $("#qmax").val();
    // var frm = $("#storedata");
    var array = $(".answerfb")

    for ( var i = 0; i < array.length; i++ ) {
        var form = $(array[i]).find("form");
        var frm = $(form);
        var datause = frm.serialize();
        $.ajax({
            type: "POST",
            url: "/testpage/question-result",
            data: datause,
              success: function (data) {
              var qb = $("#ul-"+data.id);
              var body = $("#panel-"+data.id);
              body.html(data.html)
              },
              error: function(data) {
                flag = 0;
                console.log("error")
              }
        });                    
        $("#qnum").val(i);
    }
        
    }



$(document).ready(function () {  

  getresult();

  var csrftoken = getCookie('csrftoken');
  $(".needcsrf").val(csrftoken);
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  });
});

