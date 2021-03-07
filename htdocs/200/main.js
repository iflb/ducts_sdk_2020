let duct = new ducts.Duct();
duct.open("/ducts/wsd").then( (duct) => {
    console.log('opened');
    duct.setEventHandler(
	duct.EVENT.REDIS_GET,
	(rid, eid, data) => {
	    vm.$set(vm, data['key'], data['value']);
	});
}).catch( (error) => {
    console.error(error);
});

var vm = new Vue({
    el: '#app',
    data: {
	title: 'This title will be updated by Redis',
    },
    methods: {
	redis_get: function(event) {
	    duct.send(
		duct.next_rid(), 
		duct.EVENT.REDIS_GET,
		['SAMPLE/TITLE', 'title']
	    );
	}
    },
    mounted: function() {
    },
})
