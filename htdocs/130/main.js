let duct = new ducts.Duct();
duct.open("/ducts/wsd").then( (duct) => {
    console.log('opened');
    duct.setEventHandler(
	duct.EVENT.DICT_MESSAGE,
	(rid, eid, data) => {
	    let speaker = data['speaker'];
	    let msgs = document.getElementById("messages");
	    let msg = document.createElement("div");
	    msg.className = speaker === 'you' ? 'balloon balloon_right' : 'balloon';
	    msg.appendChild(document.createTextNode(data['message']));
	    msgs.appendChild(msg);
	    msgs.scrollTop = msgs.scrollHeight;
	});
}).catch( (error) => {
    console.error(error);
});

function send_message(evt) {
    name = document.getElementById("name").value;
    message = document.getElementById("message").value;
    if (name === "" || message === "") {
	alert('name and message cannot be empty.');
	return;
    }
    msg = {'name': name, 'message': message};
    duct.send(
	duct.next_rid(), 
	duct.EVENT.DICT_MESSAGE,
	msg
	
    );
}
