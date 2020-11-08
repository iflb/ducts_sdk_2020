var vm = new Vue({
    el: '#app',
    data: {
	title: 'Ducts Tutorial',
	chapters: [],
	lang: [],
    },
    methods: {
    },
    mounted: function() {
	axios.get("./main.json")
	    .then(response => {
		console.log(typeof response.data);
		this.$set(this, 'lang',  Object.keys(response.data));
		let lang = 'ja'
		let query = window.location.search.slice(1);
		if (query) {
		    query.split('&').forEach(function(q) {
			if (q.startsWith('lang=')) {
			    lang = q.slice('lang='.length);
			}
		    });
		}
		console.log(lang);
		if (lang in response.data) {
		    this.$set(this, 'chapters',  response.data[lang]);
		} else {
		    this.$set(this, 'chapters',  response.data['ja']);
		}
		
	    })
	    .catch(function (error) {
		console.log(error);
	    })
	    .finally(function () {
	    });
    },
})
