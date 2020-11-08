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
		duct.EVENT.REDIS_GET,
		(rid, eid, data) => {
		    vm.$set(vm, data['key'], data['value']);
		});
	})
	.catch( error => {
	    console.error(error);
	});
}
    
var vm = new Vue({
    el: '#app',
    data: {
	title: 'This title will be updated by Redis',
    },
    methods: {
	redis_get: function(event) {
	    ducts.app.duct.send(
		ducts.app.duct.next_rid(), 
		ducts.app.duct.EVENT.REDIS_GET,
		['SAMPLE/TITLE', 'title']
	    );
	}
    },
    mounted: function() {
    },
})
