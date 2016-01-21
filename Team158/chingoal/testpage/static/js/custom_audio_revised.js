

// user file format
// audio_{% current_level %}_{% current_lesson %}_{% current_chapter %}
// userupload_username_{% current_level %}_{% current_lesson %}_{% current_chapter %}_{% user attempt %}


// variables
var leftchannel = [];
var rightchannel = [];
var recorder = null;
var recording = false;
var recordingLength = 0;
var volume = null;
var analyserNode = null;
var audioInput = null;
var sampleRate = null;
var audioContext = null;
var context = null;
var outputElement = document.getElementById('output');
var outputString;

var canvasHeight, canvasWidth;
var visualizerContext = null;

var blob = null;

var audio = null;
var userAudio = null;


function initRecoding() {
    // set recording flag
    recoding = true;

    // reset buffers and length
    leftchannel = [];
    rightchannel = [];
    recodigLength = 0;
}

function finishRecoding() {
    // set recoding flag
    recoding = false;
    
    // merge buffers
    var leftBuffer = mergeBuffers ( leftchannel, recordingLength );
    var rightBuffer = mergeBuffers ( rightchannel, recordingLength );
    // interleave channels
    var interleaved = interleave(leftBuffer, rightBuffer);

    // we create our wav file
    var buffer = new ArrayBuffer(44 + interleaved.length * 2);
    var view = new DataView(buffer);        
    // RIFF chunk descriptor
    writeUTFBytes(view, 0, 'RIFF');
    view.setUint32(4, 44 + interleaved.length * 2, true);
    writeUTFBytes(view, 8, 'WAVE');
    // FMT sub-chunk
    writeUTFBytes(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    // stereo (2 channels)
    view.setUint16(22, 2, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 4, true);
    view.setUint16(32, 4, true);
    view.setUint16(34, 16, true);
    // data sub-chunk
    writeUTFBytes(view, 36, 'data');
    view.setUint32(40, interleaved.length * 2, true);        
    // write the PCM samples
    var lng = interleaved.length;
    var index = 44;
    var volume = 1;
    for (var i = 0; i < lng; i++){
        view.setInt16(index, interleaved[i] * (0x7FFF * volume), true);
        index += 2;
    }        
    // our final binary blob
    blob = new Blob ( [ view ], { type : 'audio/wav' } );        


    visualizeUserWave(leftBuffer);
    
    uploadUserAudio();
    
}

function visualizeUserWave(buffer) {
    var canvasUser = $('#wave_user').get(0);
    drawBuffer( 
        canvasUser.width, 
        canvasUser.height, 
        canvasUser.getContext('2d'), 
        buffer );
}



function uploadUserAudio() {
    console.log('Saving to s3...');

    // TODO change file name and url for matching user level and lesson
    var currLevel = $('#hidden_curr_level').html();
    var currLesson = $('#hidden_curr_lesson').html();
    var username = $('#hidden_username').html();
    var fileName = 'audio/userupload_' + username + '_' + currLevel + '_' + currLesson + '.wav'

    var formData = new FormData();
    formData.append('key', fileName);
    formData.append('AWSAccessKeyId', 'AKIAI5ZDLT2RNFUJ4KMQ');
    formData.append('acl', 'public-read');
    formData.append('policy', 'CnsiZXhwaXJhdGlvbiI6ICIyMDE2LTAxLTAxVDAwOjAwOjAwWiIsImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAiY2hpbmdvYWwifSwgWyJzdGFydHMtd2l0aCIsICIka2V5IiwgImF1ZGlvLyJdLHsiYWNsIjogInB1YmxpYy1yZWFkIn0sWyJzdGFydHMtd2l0aCIsICIkQ29udGVudC1UeXBlIiwgIiJdLFsiY29udGVudC1sZW5ndGgtcmFuZ2UiLCAwLCAxMDQ4NTc2MDBdXX0=');
    formData.append('signature', '2qKR3sLhsLD0lwjK7+QEVOaMWAM=');
    formData.append('Content-Type', 'multipart/form-data');
    formData.append('file', blob);

    $.ajax({
        url: 'https://s3.amazonaws.com/chingoal',
        type: "POST",
        data: formData,
        cache: false,
        contentType: false,        
        processData: false,
        }).done(function() {
            alert('Audio saved....')
        });
}



function interleave(leftChannel, rightChannel){
    var length = leftChannel.length + rightChannel.length;
    var result = new Float32Array(length);
    
    var inputIndex = 0;
    
    for (var index = 0; index < length; ){
        result[index++] = leftChannel[inputIndex];
        result[index++] = rightChannel[inputIndex];
        inputIndex++;
    }
    return result;
}

function mergeBuffers(channelBuffer, recordingLength){
    var result = new Float32Array(recordingLength);
    var offset = 0;
    var lng = channelBuffer.length;
    for (var i = 0; i < lng; i++){
        var buffer = channelBuffer[i];
        result.set(buffer, offset);
        offset += buffer.length;
    }
    return result;
}

function writeUTFBytes(view, offset, string){ 
    var lng = string.length;
    for (var i = 0; i < lng; i++){
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}


function updateVisualizer(time) {

    if (!visualizerContext) {

        var visualizerCanvas = $('#visualizer').get(0);
        canvasHeight = visualizerCanvas.height;
        canvasWidth = visualizerCanvas.width;
        visualizerContext = visualizerCanvas.getContext('2d');
    }

    var SPACING = 3;
    var BAR_WIDTH = 1;
    var numBars = Math.round(canvasWidth / SPACING);
    var freqByteData = new Uint8Array(analyserNode.frequencyBinCount);

    analyserNode.getByteFrequencyData(freqByteData); 

    visualizerContext.clearRect(0, 0, canvasWidth, canvasHeight);
    visualizerContext.fillStyle = '#F6D565';
    visualizerContext.lineCap = 'round';
    var multiplier = analyserNode.frequencyBinCount / numBars;
    // Draw rectangle for each frequency bin.
    for (var i = 0; i < numBars; ++i) {
        var magnitude = 0;
        var offset = Math.floor( i * multiplier );
        // gotta sum/average the block, or we miss narrow-bandwidth spikes
        for (var j = 0; j< multiplier; j++)
            magnitude += freqByteData[offset + j];
        magnitude = magnitude / multiplier / 2;
        // magnitude = magnitude / multiplier;
        var magnitude2 = freqByteData[i * multiplier];
        visualizerContext.fillStyle = "hsl( " + Math.round((i*360)/numBars) + ", 100%, 50%)";
        visualizerContext.fillRect(i * SPACING, canvasHeight, BAR_WIDTH, -magnitude);
    }

    window.requestAnimationFrame(updateVisualizer);
}

function success(e){
    // creates the audio context
    // audioContext = window.AudioContext || window.webkitAudioContext;
    // context = new audioContext();

    // we query the context sample rate (varies depending on platforms)
    sampleRate = context.sampleRate;

    console.log('succcess');
    
    // creates a gain node
    volume = context.createGain();

    analyserNode = context.createAnalyser();
    analyserNode.fftSize = 2048;
    volume.connect(analyserNode);

    // creates an audio node from the microphone incoming stream
    audioInput = context.createMediaStreamSource(e);

    // connect the stream to the gain node
    audioInput.connect(volume);

    // on audio process
    var bufferSize = 2048;
    recorder = context.createScriptProcessor(bufferSize, 2, 2);

    recorder.onaudioprocess = function(e){
        if (!recording) return;
        var left = e.inputBuffer.getChannelData (0);
        var right = e.inputBuffer.getChannelData (1);
        // we clone the samples
        leftchannel.push (new Float32Array (left));
        rightchannel.push (new Float32Array (right));
        recordingLength += bufferSize;
        console.log('recording');
    }

    // we connect the recorder
    volume.connect (recorder);
    recorder.connect (context.destination); 

    // update visualizer
    updateVisualizer();
}



function playButtonClicked() {    
    if (audio.paused) {
        audio.play();
        $('#playButton').removeClass('fa-play');
        $('#playButton').addClass('fa-pause');
    } else {
        audio.pause();
        $('#playButton').removeClass('fa-pause');
        $('#playButton').addClass('fa-play');
    }

}

function playUserAudioClicked() {

    // var username = $('#hidden_username').html();
    
    // var fileNameUser = 'audio/userupload_' + username + '_' + currLevel + '_' + currLesson + '.wav'

    // var userAudioUrl = "https://s3.amazonaws.com/chingoal/" + fileNameUser;
    if (blob != null) {
        var blobUrl = window.URL.createObjectURL(blob)
    }
    
    userAudio = new Audio();
    userAudio.src = blobUrl;

    if (userAudio.paused) {
        userAudio.play();
        $('#playUserAudioButton').removeClass('fa-play');
        $('#playUserAudioButton').addClass('fa-pause');        
    } else {
        userAudio.pause();
        $('#playUserAudioButton').removeClass('fa-pause');
        $('#playUserAudioButton').addClass('fa-play');
    }

    $(userAudio).on('ended', function() {
        $('#playUserAudioButton').removeClass('fa-pause');
        $('#playUserAudioButton').addClass('fa-play');
    })
}

function drawLearnAudio(audioUrl) {
    // audioContext = window.AudioContext || window.webkitAudioContext;
    // context = new audioContext();

    var xmlReq = new XMLHttpRequest();
    var learnBuffers = [];
    xmlReq.open("GET", audioUrl, true);
    xmlReq.responseType = "arraybuffer";
    xmlReq.onreadystatechange = function() {        
        context.decodeAudioData(xmlReq.response, function (buffer) {
            drawBuffer(
                $('#wave_learn').get(0).width, 
                $('#wave_learn').get(0).height, 
                $('#wave_learn').get(0).getContext('2d'), 
                buffer.getChannelData(0));
        });
    };
    xmlReq.send();

}

$(document).ready(function() {

    audioContext = window.AudioContext || window.webkitAudioContext;
    context = new audioContext();

    if (!navigator.getUserMedia)
        navigator.getUserMedia = navigator.getUserMedia || 
                navigator.webkitGetUserMedia ||
                navigator.mozGetUserMedia || 
                navigator.msGetUserMedia;

    navigator.getUserMedia(
        {audio:true}, 
        success, 
        function(e) {
            alert('Error capturing audio.');
        });

    $('#startButton').on('click', function() {
        if (recording) {
            recording = false;
            $('#startButton').removeClass('fa-stop')
                .addClass('fa-microphone');
            finishRecoding();            
        } else {
            recording = true;
            $('#startButton').removeClass('fa-microphone')
                .addClass('fa-stop');
            initRecoding();
        }
    })

    // $('#uploadUserAudioButton').on('click', uploadUserAudio);
    var currLevel = $('#hidden_curr_level').html();
    var currLesson = $('#hidden_curr_lesson').html();
    var fileName = 'audio_' + currLevel + '_' + currLesson + '.wav';

    var audioUrl = "https://s3.amazonaws.com/chingoal/audio/" + fileName;

    audio = new Audio();
    audio.src = audioUrl;

    drawLearnAudio(audioUrl);

    $('#playButton').on('click', playButtonClicked);
    
    $(audio).on('ended', function() {
        $('#playButton').removeClass('fa-pause');
        $('#playButton').addClass('fa-play');
    });

    $('#playUserAudioButton').on('click', playUserAudioClicked);

    // $(userAudio).on('ended', function() {
    //     $('#playUserAudioButton').removeClass('fa-pause');
    //     $('#playUserAudioButton').addClass('fa-play');
    // })
    

})
