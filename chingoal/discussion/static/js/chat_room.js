        $(document).ready(function(){
        	var roomid=$("#room_id").val();
        	var data = {roomid: roomid};
        	syncrequest('/discussion/chatting/',data,'get',updatechatting);
            $("#btn-expression").click(function(){
                $("#expression-box").toggle();
            });
        });
		function getCookie(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie != '') {
				var cookies = document.cookie.split(';');
				for (var i = 0; i < cookies.length; i++) {
					var cookie = jQuery.trim(cookies[i]);
					// Does this cookie string begin with the name we want?
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
						break;
					}
				}
			}
			return cookieValue;
		}
		var csrftoken = getCookie('csrftoken');

		function csrfSafeMethod(method) {
			// these HTTP methods do not require CSRF protection
			return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
		}
		$.ajaxSetup({
			beforeSend: function(xhr, settings) {
				if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
					xhr.setRequestHeader("X-CSRFToken", csrftoken);
				}
			}
		});

		// 时间格式
		Date.prototype.Format = function (fmt) { //author: meizz
			var o = {
				"M+": this.getMonth() + 1, //月份
				"d+": this.getDate(), //日
				"h+": this.getHours(), //小时
				"m+": this.getMinutes(), //分
				"s+": this.getSeconds(), //秒
				"q+": Math.floor((this.getMonth() + 3) / 3), //季度
				"S": this.getMilliseconds() //毫秒
			};
			if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
			for (var k in o)
			if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
			return fmt;
		};

		function sendmsg(roomid, uname){
			var msg = $('#msg').val();
			$('#msg').val("");
            var data={text:msg, username:uname};
			syncrequest('/discussion/send-message/'+roomid, data, 'POST', null);
		}
		function sendimage(expression){
			var text = $('#msg').val();
			text = text + '[' +expression+']';
			$('#msg').val(text);
			console.log(name);
		}
		$("#msg").keyup(function(event){
			if(event.keyCode == 13){
			    var roomid=$("#room_id").val();
			    var uname=$("#user_name").val();
				sendmsg(roomid, uname);
			}
		});

		function syncrequest(url,data,type,func){
				$.ajax({
					url:url,
					data:data,
					type:type,
					success:func
				})
			}

 		function updatechatting(arg){
 			var data = $.parseJSON(arg);
 			$("#chatting").empty();
 			$.each(data, function(k,v){
 				var message = v.msg;
 				message = message.replace(/\]/gi, ".jpg\" alt=\"Smiley face\" height=\"22\" width=\"22\"\\>");
        		message = message.replace(/\[/gi, "\<img src=\"\/static\/img\/");
 				var content = '<span style="color: green">'+ v.sender + '&nbsp' + v.time + '</span><br> <span> &nbsp'+ message + '</span></br>'
 				$("#chatting").append(content);
 			})
 		}

		setInterval(function () {
			var roomid=$("#room_id").val();
			var userid=$("#user_id").val();
			var data = {roomid: roomid, userid: userid};
			syncrequest('/discussion/onlinelist/',data,'get',updateonlinelist);
		},1000);


		function onbeforeunload_handler(){
			var roomid=$("#room_id").val();
			var userid=$("#user_id").val();
            var data = {roomid: roomid, userid: userid};
            console.log('success');
            window.location.href = "/";
            syncrequest('/discussion/exitchat/', data,'post',null);
            
		}

		function updateonlinelist(arg){
			var data = $.parseJSON(arg);
            console.log(data)
			$("#onlinelist").empty();
			$.each(data, function(k,v){
				var content = '<li class="list-group-item">'+ v + '</li>';//k is userid, v is username
				$("#onlinelist").append(content);
			});
		}

