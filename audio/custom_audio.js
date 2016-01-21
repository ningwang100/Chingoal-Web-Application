
var audioContext = new (window.AudioContext || window.webkitAudioContext)();

var audioInput = null;
var realAudioInput = null;
var inputPoint = null;
var audioRecorder = null;

var rafID = null;
var analyserContext = null;
var canvasWidth, canvasHeight;
var recIndex = 0;

function saveAudio() {
    audioRecorder.exportWAV( doneEncoding );
}

function gotBuffers( buffers ) {
    var canvas = $('#wave_user').get(0);
    drawBuffer( canvas.width, canvas.height, canvas.getContext('2d'), buffers[0] );

    // the ONLY time gotBuffers is called is right after a new recording is completed - 
    // so here's where we should set up the download.
    audioRecorder.exportWAV( doneEncoding );
}

function doneEncoding( blob ) {
    Recorder.setupDownload( blob, "myRecording" + ((recIndex<10)?"0":"") + recIndex + ".wav" );
    recIndex++;
}

function toggleRecording( e ) {

    if (e.classList.contains("recording")) {
        console.log('Stop Recording...');
        $('#startButton').html('Start');
        $('#saveButton').prop('disabled', false);

        audioRecorder.stop();        
        e.classList.remove("recording");        
        audioRecorder.getBuffers( gotBuffers );
        
    } else {
        console.log('Start Recording...');
        $('#startButton').html('Stop');
        $('#saveButton').prop('disabled', true);

        if (!audioRecorder)
            return;
        e.classList.add("recording");
        audioRecorder.clear();        
        audioRecorder.record();
    }
}

function convertToMono( input ) {
    var splitter = audioContext.createChannelSplitter(2);
    var merger = audioContext.createChannelMerger(2);

    input.connect( splitter );
    splitter.connect( merger, 0, 0 );
    splitter.connect( merger, 0, 1 );
    return merger;
}

function cancelAnalyserUpdates() {
    window.cancelAnimationFrame( rafID );
    rafID = null;
}

function updateAnalysers(time) {
    if (!analyserContext) {
        var canvas = $('#visualizer').get(0);
        canvasWidth = canvas.width;
        canvasHeight = canvas.height;
        analyserContext = canvas.getContext('2d');
    }

    // analyzer draw code here
    {
        var SPACING = 3;
        var BAR_WIDTH = 1;
        var numBars = Math.round(canvasWidth / SPACING);
        var freqByteData = new Uint8Array(analyserNode.frequencyBinCount);

        analyserNode.getByteFrequencyData(freqByteData); 

        analyserContext.clearRect(0, 0, canvasWidth, canvasHeight);
        analyserContext.fillStyle = '#F6D565';
        analyserContext.lineCap = 'round';
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
            analyserContext.fillStyle = "hsl( " + Math.round((i*360)/numBars) + ", 100%, 50%)";
            analyserContext.fillRect(i * SPACING, canvasHeight, BAR_WIDTH, -magnitude);
        }
    }
    
    rafID = window.requestAnimationFrame( updateAnalysers );
}

function toggleMono() {
    if (audioInput != realAudioInput) {
        audioInput.disconnect();
        realAudioInput.disconnect();
        audioInput = realAudioInput;
    } else {
        realAudioInput.disconnect();
        audioInput = convertToMono( realAudioInput );
    }

    audioInput.connect(inputPoint);
}

function gotStream(stream) {
    inputPoint = audioContext.createGain();

    // Create an AudioNode from the stream.
    realAudioInput = audioContext.createMediaStreamSource(stream);
    audioInput = realAudioInput;
    audioInput.connect(inputPoint);

    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 2048;
    inputPoint.connect( analyserNode );

    audioRecorder = new Recorder( inputPoint );

    zeroGain = audioContext.createGain();
    zeroGain.gain.value = 0.0;
    inputPoint.connect( zeroGain );
    zeroGain.connect( audioContext.destination );
    updateAnalysers();
}

function initAudio() {
        if (!navigator.getUserMedia)
            navigator.getUserMedia = (navigator.getUserMedia ||
                          navigator.webkitGetUserMedia ||
                          navigator.mozGetUserMedia ||
                          navigator.msGetUserMedia);
        if (!navigator.cancelAnimationFrame)
            navigator.cancelAnimationFrame = 
                        navigator.webkitCancelAnimationFrame || 
                        navigator.mozCancelAnimationFrame;
        if (!navigator.requestAnimationFrame)
            navigator.requestAnimationFrame = 
                        navigator.webkitRequestAnimationFrame || 
                        navigator.mozRequestAnimationFrame;

    navigator.getUserMedia(
        {
            "audio": {
                "mandatory": {
                    "googEchoCancellation": "false",
                    "googAutoGainControl": "false",
                    "googNoiseSuppression": "false",
                    "googHighpassFilter": "false"
                },
                "optional": []
            },
        }, 
        gotStream,
        function(e) {
            alert('Error getting audio');
            console.log(e);
        });
}

$(document).ready(function () {
    initAudio();
    $('#startButton').on('click', function() {
        toggleRecording(this);
    });
})
// window.addEventListener('load', initAudio);
// startButton.addEventListener('click', initAudio);
// startButton.addEventListener('click', toggleRecording(this));









// var canvasCtx = canvas.getContext("2d");



// console.log(audioCtx.destination);

// var analyser = audioCtx.createAnalyser();
// var distortion = audioCtx.createWaveShaper();
// var gainNode = audioCtx.createGain();

// function startRecording() {
//     navigator.getUserMedia (
//         { audio: true },        
        
//         function(stream) {
//             source = audioCtx.createMediaStreamSource(stream);
//             source.connect(analyser);
//             analyser.connect(distortion);
//             distortion.connect(gainNode);
            
//             gainNode.connect(audioCtx.destination); // connecting the different audio graph nodes together
        
//             visualize(stream);
        
//         },
        
//         function(err) {
//             alert('Error when trying to get user media!')
//         }
//     );
// }


// function visualize(stream) {
//     WIDTH = canvas.width;
//     HEIGHT = canvas.height;
    
//     analyser.fftSize = 2048;
//     var bufferLength = analyser.frequencyBinCount; // half the FFT value
//     var dataArray = new Uint8Array(bufferLength); // create an array to store the data
//     canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);
//     function draw() {
//         drawVisual = requestAnimationFrame(draw);
//         analyser.getByteTimeDomainData(dataArray); // get waveform data and put it into the array created above
//         canvasCtx.fillStyle = 'rgb(200, 200, 100)'; // draw wave with canvas
//         canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
//         canvasCtx.lineWidth = 2;
//         canvasCtx.strokeStyle = 'rgb(200, 0, 0)';
//         canvasCtx.beginPath();
//         var sliceWidth = WIDTH * 1.0 / bufferLength;
//         var x = 0;
//         for(var i = 0; i < bufferLength; i++) {
//         var v = dataArray[i] / 128.0;
//         var y = v * HEIGHT/2;
//         if(i === 0) {
//             canvasCtx.moveTo(x, y);
//         } else {
//             canvasCtx.lineTo(x, y);
//         }
//         x += sliceWidth;
//         }
//         canvasCtx.lineTo(canvas.width, canvas.height/2);
//         canvasCtx.stroke();
//     };
//     draw();
// }

// function writeWAV() {
//     var bufferSize = 2048;
//     recorder = audioCtx.createJavaScriptProcessor(bufferSize, 2, 2);
//     recorder.onaudioprocess = function(e) {
//         console.log('Recorrrrrrding');
//         var left = e.inputBuffer.getChannelData(0);
//         var right = e.inputBuffer.getChannelData(1);
//         leftChannels.push(new Float32Array(left));
//         rightChannels.push(new Float32Array(right));
//         recordingLength += bufferSize;
//     }

// }


// startButton.onclick = function() {
//     startRecording();
// }




