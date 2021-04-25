window.AudioContext = window.AudioContext || window.webkitAudioContext;
window.ducts.audio = window.ducts.audio || {};

let duct = new ducts.Duct();
duct.event_error_handler =
    (rid, eid, data, error) => {
	console.error(error);
    };
duct.open("/ducts/wsd").then( (duct) => {
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
	    var buffer = ducts.audio.context.createBuffer(1, f_data.length, framerate);
	    buffer.getChannelData(0).set(f_data);
	    
	    let source = ducts.audio.context.createBufferSource();
	    source.buffer = buffer;
	    source.connect(ducts.audio.context.destination);
	    
	    let current_time = ducts.audio.context.currentTime;
	    if (current_time < ducts.audio.scheduled_time) {
		source.start(ducts.audio.scheduled_time);
		ducts.audio.scheduled_time += buffer.duration;
	    } else {
		source.start(current_time);
		ducts.audio.scheduled_time = current_time + buffer.duration + ducts.audio.initial_delay_sec + 1;
	    }
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
	    duct.EVENT.ECHO_BACK_PCM,
	    buf
	);
    });



function start_recording(evt) {
    if (ducts.audio.context == null) {
	ducts.audio.context = new AudioContext();
	ducts.audio.scheduled_time = 0;
	ducts.audio.initial_delay_sec = 0;
    }
    recorder.start_recording();
}

function stop_recording(evt) {
    recorder.stop_recording();
}

