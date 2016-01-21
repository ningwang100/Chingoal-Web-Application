/*License (MIT)
Copyright © 2013 Matt Diamond
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and 
to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of 
the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.
*/



(function(window){

    // var WORKER_PATH = 'js/recorderjs/recorderWorker.js';

    // var WORKER_PATH = 'recorderWorker.js';

    var recLength = 0;
    var recBuffersL = [];
    var recBuffersR = [];
    var sampleRate;

    function mergeBuffers(recBuffers, recLength){
        var result = new Float32Array(recLength);
        var offset = 0;
        for (var i = 0; i < recBuffers.length; i++){
            result.set(recBuffers[i], offset);
            offset += recBuffers[i].length;
        }
        return result;
    }
    
    function interleave(inputL, inputR){
        var length = inputL.length + inputR.length;
        var result = new Float32Array(length);
        
        var index = 0,
            inputIndex = 0;
        
        while (index < length){
            result[index++] = inputL[inputIndex];
            result[index++] = inputR[inputIndex];
            inputIndex++;
        }
        return result;
    }
    
    function floatTo16BitPCM(output, offset, input){
        for (var i = 0; i < input.length; i++, offset+=2){
            var s = Math.max(-1, Math.min(1, input[i]));
            output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }
    }
    
    function writeString(view, offset, string){
        for (var i = 0; i < string.length; i++){
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }

    function encodeWAV(samples, mono){
        var buffer = new ArrayBuffer(44 + samples.length * 2);
        var view = new DataView(buffer);
        
        /* RIFF identifier */
        writeString(view, 0, 'RIFF');
        /* file length */
        view.setUint32(4, 32 + samples.length * 2, true);
        // view.setUint32(4, 44 + samples.length * 2, true);
        /* RIFF type */
        writeString(view, 8, 'WAVE');
        /* format chunk identifier */
        writeString(view, 12, 'fmt ');
        /* format chunk length */
        view.setUint32(16, 16, true);
        /* sample format (raw) */
        view.setUint16(20, 1, true);
        /* channel count */
        view.setUint16(22, mono?1:2, true);
        /* sample rate */
        view.setUint32(24, sampleRate, true);
        /* byte rate (sample rate * block align) */
        view.setUint32(28, sampleRate * 4, true);
        /* block align (channel count * bytes per sample) */
        view.setUint16(32, 4, true);
        /* bits per sample */
        view.setUint16(34, 16, true);
        /* data chunk identifier */
        writeString(view, 36, 'data');
        /* data chunk length */
        view.setUint32(40, samples.length * 2, true);
        
        floatTo16BitPCM(view, 44, samples);
        
        return view;
    }


    var Recorder = function(source, cfg){
        var config = cfg || {};
        var bufferLen = config.bufferLen || 4096;
        this.context = source.context;
        if(!this.context.createScriptProcessor){
           this.node = this.context.createJavaScriptNode(bufferLen, 2, 2);
        } else {
           this.node = this.context.createScriptProcessor(bufferLen, 2, 2);
        }
       
        // var worker = new Worker(config.workerPath || WORKER_PATH);
        // var worker = new Worker('recorderWorker.js');
        // worker.postMessage({
        //   command: 'init',
        //   config: {
        //     sampleRate: this.context.sampleRate
        //   }
        // });

        // ************** Init
        sampleRate = this.context.sampleRate;


        var recording = false,
          currCallback;

        this.node.onaudioprocess = function(e){
            if (!recording) return;      
            // worker.postMessage({
            //   command: 'record',
            //   buffer: [
            //     e.inputBuffer.getChannelData(0),
            //     e.inputBuffer.getChannelData(1)
            //   ]
            // });

            // ************** Recording
            var inputBuffer = [
                e.inputBuffer.getChannelData(0),
                e.inputBuffer.getChannelData(1)
            ];
            recBuffersL.push(inputBuffer[0]);
            recBuffersR.push(inputBuffer[1]);
            recLength += inputBuffer[0].length;
        }

        this.configure = function(cfg){
          for (var prop in cfg){
            if (cfg.hasOwnProperty(prop)){
              config[prop] = cfg[prop];
            }
          }
        }

        this.record = function(){
          recording = true;
        }

        this.stop = function(){
          recording = false;
        }

        this.clear = function(){
            // worker.postMessage({ command: 'clear' });
            
            // ************** Clear
            recLength = 0;
            recBuffersL = [];
            recBuffersR = [];
        }

        this.getBuffers = function(cb) {            
            currCallback = cb || config.callback;
            // worker.postMessage({ command: 'getBuffers' })

            // ************** Get buffers
            var buffers = [];
            buffers.push( mergeBuffers(recBuffersL, recLength) );
            buffers.push( mergeBuffers(recBuffersR, recLength) );

            // Worker post message    
            currCallback(buffers);
        }

        this.exportWAV = function(cb, type){
            currCallback = cb || config.callback;
            type = type || config.type || 'audio/wav';
            if (!currCallback) throw new Error('Callback not set');          
            // worker.postMessage({
            //     command: 'exportWAV',
            //     type: type
            // });

            // ************** Export WAV
            var bufferL = mergeBuffers(recBuffersL, recLength);
            var bufferR = mergeBuffers(recBuffersR, recLength);
            var interleaved = interleave(bufferL, bufferR);
            var dataview = encodeWAV(interleaved);
            // TODO check interleaved data!!!
            var oneLen = recBuffersL[0].length;
            
            var audioBlob = new Blob([dataview], { type: type });
            // Worker post message        
            currCallback(audioBlob);
        }

        this.exportMonoWAV = function(cb, type){
            currCallback = cb || config.callback;
            type = type || config.type || 'audio/wav';
            if (!currCallback) throw new Error('Callback not set');          
            // worker.postMessage({
            //   command: 'exportMonoWAV',
            //   type: type
            // });
    
            // ************** Export Mono WAV 
            var bufferL = mergeBuffers(recBuffersL, recLength);
            var dataview = encodeWAV(bufferL, true);
            var audioBlob = new Blob([dataview], { type: type });
            // TODO: worker post message
            e = audioBlob;
            var blob = e.data;
            currCallback(blob);
        }

        source.connect(this.node);
        this.node.connect(this.context.destination);   // if the script node is not connected to an output the "onaudioprocess" event is not triggered in chrome.
    };

    Recorder.setupDownload = function(blob, filename){
        var url = (window.URL || window.webkitURL).createObjectURL(blob);
        var link = $('#saveButton').get(0);
        link.href = url;
        link.download = filename || 'output.wav';
    }

    window.Recorder = Recorder;

})(window);



