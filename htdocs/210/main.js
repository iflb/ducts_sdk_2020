let duct = new ducts.Duct();
duct.open("/ducts/wsd").then( (duct) => {
    console.log('opened');
    duct.setEventHandler(
	duct.EVENT.REDIS_GET,
	(rid, eid, data) => {
	    vm.$set(vm, data['key'], data['value']);
	});
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
	duct.EVENT.REDIS_GET,
	['SAMPLE/TITLE', 'title']
    );
    duct.send(
	duct.next_rid(), 
	duct.EVENT.MODEL_MESSAGES,
	null
    );
    
}).catch( (error) => {
    console.error(error);
});


var vm = new Vue({
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
    },
    mounted: function() {
    },
})

Vue.config.errorHandler = (err, vm, info) => {
    console.log(`Captured in Vue.config.errorHandler: ${info}`, err);
};
