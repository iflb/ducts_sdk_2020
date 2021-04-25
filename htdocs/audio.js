window.ducts = window.ducts || {};
window.ducts.AudioRecorder = class {

    constructor() {
	this.desiredSampRate = 16000;
	this.timeSlice = 1000;
	this.bufferSize = 16384;

	this._isEdge = navigator.userAgent.indexOf('Edge') !== -1 && (!!navigator.msSaveOrOpenBlob || !!navigator.msSaveBlob);
	this._isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
	this._recorder; // globally accessible
	this._microphone;

	this.get_user_media =
	    (callback) => {this._get_user_media(this, callback)};
	    
	this.start_recording =
	    () => {this._start_recording(this, null)};
	    
	this.stop_recording =
	    () => {this._stop_recording(this)};

	this._ondata_event_handler = null;
	this.set_ondata_event_handler = 
	    (handler) => {this._ondata_event_handler = handler;};

	this._recorder_event_handler = null;
	this.set_recorder_event_handler = 
	    (handler) => {this._recorder_event_handler = handler;};

	this._recorder_error_handler = null;
	this.set_recorder_error_handler = 
	    (handler) => {this._recorder_error_handler = handler;};

    }

    _get_user_media(self, callback) {
	console.log('get_user_media');
	if(self._microphone) {
	    callback(self._microphone);
	    return;
	}
	if(typeof navigator.mediaDevices === 'undefined' || !navigator.mediaDevices.getUserMedia) {
	    alert('This browser does not supports WebRTC getUserMedia API.');
	    if(!!navigator.getUserMedia) {
		alert('This browser seems supporting deprecated getUserMedia API.');
	    }
	}
	navigator.mediaDevices.getUserMedia({
	    audio: self.isEdge ? true : {
		echoCancellation: false
	    }
	}).then(function(mic) {
	    callback(mic);
	}).catch(function(error) {
	    alert('Unable to capture your microphone. Please check console logs.');
	    console.error(error);
	});
    }

    _start_recording(self, microphone) {

	console.log('start_recording:mic='+microphone)
	
	if (!self._microphone) {
	    if (!microphone) {
		self.get_user_media(function(stream) {
		    self._start_recording(self, stream);
		});
	    } else {
		self._microphone = microphone;
		if(self._isSafari) {
		    alert('Please click startRecording button again. First time we tried to access your microphone. Now we will record it.');
		    return;
		}
		self._start_recording(self, microphone);
	    }
	    return;
	}
	var options = {
	    type: 'audio',
	    recorderType: RecordRTC.StereoAudioRecorder,
	    mimeType: 'audio/wav',
	    desiredSampRate: self.desiredSampRate,
	    numberOfAudioChannels: 1,
	    checkForInactiveTracks: true,
	    bufferSize: self.bufferSize,
	    timeSlice: self.timeSlice
	};
	if(self._recorder) {
	    self._recorder.destroy();
	    self._recorder = null;
	}
	
	options.ondataavailable = (blob) => {
	    if (this._ondata_event_handler) {
		let fileReader = new FileReader();
		fileReader.onload = (event) => {self._ondata_event_handler(self, event.target.result);};
		fileReader.readAsArrayBuffer(blob);
	    } else {
		console.log('dataavailable:e='+blob);
	    }
	}
	
	self._recorder = RecordRTC(self._microphone, options);
	self._recorder.startRecording();

    }

    _stop_recording(self) {
	if (self._recorder) {
	    self._recorder.stopRecording(self._stopRecordingCallback);
	}
    }

    _stopRecordingCallback() {

    }

    _release_microphone(self) {
	if(self._microphone) {
	    self._microphone.stop();
	    self._microphone = null;
	}
	if(self._recorder) {
	    // click(btnStopRecording);
	}
    }

}
