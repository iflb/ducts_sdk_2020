
function handle_opened(duct) {
    console.log('opened');
    ssid = duct.WSD['websocket_url'].split('/');
    ssid = ssid[ssid.length - 1];
    ssid = ssid.split('.')[1];
    vm.$set(vm, 'name', ssid);
    duct.setEventHandler(
	duct.EVENT.MODEL_MESSAGES, 
	(rid, eid, data) => {
	    console.log(data);
	    msg = data;
	    msg['balloon_right'] = (msg['name'] == vm.name);
	    vm.messages.push(msg);
	    vm.$nextTick(function() {
		var container = vm.$el.querySelector("#messages");
		container.scrollTop = container.scrollHeight;
	    });
	});
    duct.send(
	duct.next_rid(), 
	duct.EVENT.MODEL_MESSAGES,
	null
    );
}

let duct = new ducts.Duct();
duct.open("/ducts/wsd")
    .then(handle_opened)
    .catch( (error) => {
	alert(error);
    });

let vm = new Vue({
    el: '#app',
    data: {
	title: 'This title will be updated by Redis',
	name: Math.random().toString(36).slice(-8),
	message: '',
	messages: [
	],
    },
    methods: {
	send_message: function (event) {
	    duct.send(
		duct.next_rid(), 
		duct.EVENT.CTRL_MESSAGES,
		{'name': this.name, 'message': this.message}
	    );
	},
	close: function (event) {
	    duct.close();
	},
	connect: function (event) {
	    if (duct.state < 0) {
		duct.open('/ducts/wsd')
		    .then(handle_opened)
		    .catch( error => {
			console.error(error);
		    });
	    } else {
		alert('connection is not closed.');
	    }
	},
	reconnect: function (event) {
	    duct.reconnect();
	},
    },
    mounted: function() {
    },
})

Vue.config.errorHandler = (err, vm, info) => {
    alert(`ERROR: ${info}`, err);
};
