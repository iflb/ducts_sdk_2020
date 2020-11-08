ducts.main = function() {
    ducts.app = ducts.app || {};
    ducts.app.duct = new window.ducts.Duct();
    ducts.app.duct.open('/ducts/wsd')
	.then( duct => {
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
	})
	.catch( error => {
	    console.error(error);
	});
}

function send_message(evt) {
    message = document.getElementById("message").value;
    if (message === "") {
	alert('Message is empty.');
	return;
    }
    ducts.app.duct.send(
	ducts.app.duct.next_rid(), 
	ducts.app.duct.EVENT.SEND_TEXT_MESSAGE,
	message
    );
}