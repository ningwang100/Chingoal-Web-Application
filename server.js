var express = require('express');
var app = express();
var fs = require('fs');
var options = {
  key: fs.readFileSync('/etc/apache2/ssl/apache.key'),
  cert: fs.readFileSync('/etc/apache2/ssl/apache.crt')
};
var server = require('https').createServer(options,app);
var SkyRTC = require('skyrtc').listen(server);
var path = require("path");

var port = process.env.PORT || 3000;
server.listen(port);

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', function(req, res) {
	res.sendfile(__dirname + '/chingoal/discussion/templates/discussion/video_room.html');
});

SkyRTC.rtc.on('new_connect', function(socket) {
	console.log('Create new connection');
});

SkyRTC.rtc.on('remove_peer', function(socketId) {
	console.log(socketId + "user leaves");
});

SkyRTC.rtc.on('new_peer', function(socket, room) {
	console.log("new user " + socket.id + "enter " + room);
});


SkyRTC.rtc.on('ice_candidate', function(socket, ice_candidate) {
	console.log("receive user " + socket.id + " ICE Candidate");
});

SkyRTC.rtc.on('offer', function(socket, offer) {
	console.log("receive user " + socket.id + "Offer");
});

SkyRTC.rtc.on('answer', function(socket, answer) {
	console.log("receive user " + socket.id + "Answer");
});

SkyRTC.rtc.on('error', function(error) {
	console.log("error: " + error.message);
});