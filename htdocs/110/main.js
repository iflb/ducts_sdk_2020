let duct = new ducts.Duct();
duct.open("/ducts/wsd").then( (duct) => {
    console.log('opened');
    duct.setEventHandler(
	duct.EVENT.HELLO_DUCTS_LOOP,
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

function say_hello(evt) {
    duct.send(
	duct.next_rid(), 
	duct.EVENT.HELLO_DUCTS_LOOP,
	null
    );
}
