ducts.main = function() {
    ducts.app = ducts.app || {};
    
    ducts.app.duct = new window.ducts.Duct();
    ducts.app.duct.event_error_handler =
	(rid, eid, data, error) => {
	    console.error(error);
	};

    ducts.app.duct.open('/ducts/wsd')
	.then( duct => {
	    console.log('opened');
	    duct.setEventHandler(
		duct.EVENT.ECHO_BACK_PCM,
		(rid, eid, data) => {
		    let framerate = data['framerate'];
		    let b_data = data['data'];
		    
		    let msgs = document.getElementById("messages");
		    let msg = document.createElement("div");
		    msg.className = 'balloon';
		    msg.appendChild(document.createTextNode('receiving the data as the PCM format. framerate = ' + framerate + ' size = ' + b_data.byteLength + ' ' + toString.call(data)));
		    msgs.appendChild(msg);
		    msgs.scrollTop = msgs.scrollHeight;
		
		    view = new DataView(b_data.buffer, b_data.byteOffset, b_data.length);
		    let f_data = new Float32Array(b_data.length/2);
		    for (let i = 0 ; i < f_data.length ; i++) {
			f_data[i] = view.getInt16(i*2, true) / 32768; // 2^15
		    }
		    var buffer = ducts.app.audio.context.createBuffer(1, f_data.length, framerate);
		    buffer.getChannelData(0).set(f_data);
		    
		    let source = ducts.app.audio.context.createBufferSource();
		    source.buffer = buffer;
		    source.connect(ducts.app.audio.context.destination);
		    
		    let current_time = ducts.app.audio.context.currentTime;
		    if (current_time < ducts.app.audio.scheduled_time) {
			source.start(ducts.app.audio.scheduled_time);
			ducts.app.audio.scheduled_time += buffer.duration;
		    } else {
			source.start(current_time);
			ducts.app.audio.scheduled_time = current_time + buffer.duration + ducts.app.audio.initial_delay_sec + 1;
		    }
		});
	})
	.catch( error => {
	    console.error(error);
	});

    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    ducts.app.audio = {};
    ducts.app.recorder = new ducts.AudioRecorder();
    ducts.app.recorder.timeSlice = 500;
    ducts.app.recorder.desiredSampRate = 22050;
    ducts.app.recorder.set_ondata_event_handler(
	(recorder, buf) => {
	    let msgs = document.getElementById("messages");
	    let msg = document.createElement("div");
	    msg.className = 'balloon balloon_right';
	    msg.appendChild(document.createTextNode('sending the data as wav format. size = ' + buf.byteLength + ' ' + toString.call(buf)));
	    msgs.appendChild(msg);
	    msgs.scrollTop = msgs.scrollHeight;
	    ducts.app.duct.send(
		ducts.app.duct.next_rid(), 
		ducts.app.duct.EVENT.ECHO_BACK_PCM,
		buf
	    );
	});
}

function start_recording(evt) {
    if (ducts.app.audio.context == null) {
	ducts.app.audio.context = new AudioContext();
	ducts.app.audio.scheduled_time = 0;
	ducts.app.audio.initial_delay_sec = 0;
    }
    ducts.app.recorder.start_recording();
}

function stop_recording(evt) {
    ducts.app.recorder.stop_recording();
}

