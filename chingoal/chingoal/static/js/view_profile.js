jQuery.browser = {};
(function () {
 jQuery.browser.msie = false;
 jQuery.browser.version = 0;
 if (navigator.userAgent.match(/MSIE ([0-9]+)\./)) {
 jQuery.browser.msie = true;
 jQuery.browser.version = RegExp.$1;
 }
 })();

$(document).ready(function() {	
	
$(".btn-pref .btn").click(function () {
    $(".btn-pref .btn").removeClass("btn-primary").addClass("btn-default");
    // $(".tab").addClass("active"); // instead of this do the below 
    $(this).removeClass("btn-default").addClass("btn-primary");   
});

if (!isie6()) {
                  var rollStart = $('.aa'),
                  rollSet = $('.aa');
                  var offset = rollStart.offset(),
                  objWindow = $(window),
                  rollBox = rollStart.prev();
                  if (objWindow.width() > 960) {
                  objWindow.scroll(function() {
                                   if (objWindow.scrollTop() > offset.top) {
                                   rollStart.css('position','fixed');
                                   rollStart.stop().animate({
                                                            top: 0
                                                            },
                                                            400)
                                   } else {
                                   rollStart.css('position','static');
                                   rollStart.stop().animate({ 
                                                            top: 0 
                                                            }, 
                                                            400) 
                                   } 
                                   }) 
                  } 
                  } 
                  function isie6() { 
                  if ($.browser.msie) { 
                  if ($.browser.version == "6.0") return true; 
                  } 
                  return false; 
                  } 
});