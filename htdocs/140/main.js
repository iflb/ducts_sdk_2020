window.AudioContext = window.AudioContext || window.webkitAudioContext;
window.ducts.audio = window.ducts.audio || {};

let duct = new ducts.Duct();
duct.open("/ducts/wsd").then( (duct) => {
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
	    
	    window.ducts.audio.context.decodeAudioData(array_buffer)
		.then(buffer => {
		    let source = window.ducts.audio.context.createBufferSource();
		    source.buffer = buffer;
		    source.connect(window.ducts.audio.context.destination);
		    let current_time = window.ducts.audio.context.currentTime;
		    if (current_time < window.ducts.audio.scheduled_time) {
			source.start(window.ducts.audio.scheduled_time);
			window.ducts.audio.scheduled_time += buffer.duration;
		    } else {
			source.start(current_time);
			window.ducts.audio.scheduled_time = current_time + buffer.duration + window.ducts.audio.initial_delay_sec + 1;
		    }
		})
		.catch(e => { console.error(e); });
	});
   
}).catch( (error) => {
    console.error(error);
});

let recorder = new window.ducts.AudioRecorder();
recorder.timeSlice = 500;
recorder.desiredSampRate = 22050;
recorder.set_ondata_event_handler(
    (recorder, buf) => {
	let msgs = document.getElementById("messages");
	let msg = document.createElement("div");
	msg.className = 'balloon balloon_right';
	msg.appendChild(document.createTextNode('sending the data as wav format. size = ' + buf.byteLength + ' ' + toString.call(buf)));
	msgs.appendChild(msg);
	msgs.scrollTop = msgs.scrollHeight;
	duct.send(
	    duct.next_rid(), 
	    duct.EVENT.ECHO_BACK,
	    buf
	);
    });



function start_recording(evt) {
    if (window.ducts.audio.context == null) {
	window.ducts.audio.context = new AudioContext();
	window.ducts.audio.scheduled_time = 0;
	window.ducts.audio.initial_delay_sec = 0;
    }
    recorder.start_recording();
}

function stop_recording(evt) {
    recorder.stop_recording();
}

