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
		duct.EVENT.ECHO_BACK,
		(rid, eid, data) => {
		    let msgs = document.getElementById("messages");
		    let msg = document.createElement("div");
		    msg.className = 'balloon';
		    msg.appendChild(document.createTextNode('receiving the data as the same format as request. size = ' + data.byteLength + ' ' + toString.call(data)));
		    msgs.appendChild(msg);
		    msgs.scrollTop = msgs.scrollHeight;
		    
		    array_buffer = (data.byteOffset == 0 && data.buffer.byteLength == data.length) ? data.buffer : data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength);
		    
		    ducts.app.audio.context.decodeAudioData(array_buffer)
			.then(buffer => {
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
			})
			.catch(e => { console.error(e); });
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
		ducts.app.duct.EVENT.ECHO_BACK,
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

