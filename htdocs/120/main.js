let duct = new ducts.Duct();
duct.open("/ducts/wsd").then( (duct) => {
    console.log('opened');
    duct.setEventHandler(
	duct.EVENT.SEND_TEXT_MESSAGE,
	(rid, eid, data) => {
	    let msgs = document.getElementById("messages");
	    let msg = document.createElement("div");
	    msg.className = 'balloon';
	    msg.appendChild(document.createTextNode(data));
	    msgs.appendChild(msg);
	    msgs.scrollTop = msgs.scrollHeight;
	});
}).catch( (error) => {
    console.error(error);
});

function send_message(evt) {
    message = document.getElementById("message").value;
    if (message === "") {
	alert('Message is empty.');
	return;
    }
    duct.send(
	duct.next_rid(), 
	duct.EVENT.SEND_TEXT_MESSAGE,
	message
    );
}
