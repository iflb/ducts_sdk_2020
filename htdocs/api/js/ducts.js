(function( ducts ) {
    ducts.context_url = ducts.context_url || "/ducts";
    ducts.libs_plugin = ducts.libs_plugin || [];
    ducts._local = {};
    ducts._local.libs = [
	'https://unpkg.com/what-the-pack/dist/MessagePack.min.js'
	,'https://www.WebRTC-Experiment.com/RecordRTC.js'
	, ...ducts.libs_plugin
    ];
    ducts._local.libs_index = 0;
    ducts._local.append_next_lib = function() {
	if (ducts._local.libs_index < ducts._local.libs.length) {
	    var lib_script = document.createElement('script');
	    lib_script.src = ducts._local.libs[ducts._local.libs_index];
	    document.body.appendChild(lib_script);
	    ducts._local.libs_index++;
	}
	if (ducts._local.libs_index < ducts._local.libs.length) {
	    lib_script.onload = ducts._local.append_next_lib;
	} else {
	    lib_script.onload = function() { ducts._local.main(); };
	}
    }
    ducts._local.append_next_lib();

    ducts._local.main = function() {
	ducts.msgpack = MessagePack.initialize(2**22);
	ducts.main();
    };

    ducts.main = ducts.main || function() {console.warn('ducts.main is not set.');};

    ducts._local.last_rid = 0;
    ducts._local.next_rid = function() {
	let next_id = new Date().getTime();
	if (next_id <= ducts._local.last_rid) {
	    next_id = ducts._local.last_rid + 1;
	}
	ducts._local.last_rid = next_id;
	return next_id;
    };

}( window.ducts = window.ducts || {}));


//https://github.com/necojackarc/extensible-custom-error/blob/master/src/index.js
window.ducts.DuctError = class extends Error {
    
    constructor(message, error=null, ...args) {
	super(message, error, ...args);

	// Align with Object.getOwnPropertyDescriptor(Error.prototype, 'name')
	Object.defineProperty(this, 'name', {
	    configurable: true,
	    enumerable: false,
	    value: this.constructor.name,
	    writable: true,
	});

	// Helper function to merge stack traces
	const merge =
	      (stackTraceToMerge, baseStackTrace) => {
		  const entriesToMerge = stackTraceToMerge.split('\n');
		  const baseEntries = baseStackTrace.split('\n');
		  const newEntries = [];
		  entriesToMerge.forEach((entry) => {
		      if (baseEntries.includes(entry)) {
			  return;
		      }
		      newEntries.push(entry);
		  });
		  return [...newEntries, ...baseEntries].join('\n');
	      };
	if (Error.captureStackTrace) {
	    Error.captureStackTrace(this, this.constructor);
	    this.stack = error ? merge(this.stack, error.stack) : this.stack;
	}
	
    }
    
}

window.ducts.DuctEvent = class {
    constructor() {
    }
}

window.ducts.DuctConnectionEvent = class extends window.ducts.DuctEvent {

    constructor(state, source) {
	super();
	this.state = state;
	this.source = source;
    }

}

window.ducts.DuctMessageEvent = class extends window.ducts.DuctEvent {

    constructor(rid, eid, data) {
	super();
	this.rid = rid;
	this.eid = eid;
	this.data = data;
    }

}

window.ducts.State = Object.freeze({
    CLOSE : -1
    , OPEN_CONNECTING : WebSocket.CONNECTING 
    , OPEN_CONNECTED : WebSocket.OPEN 
    , OPEN_CLOSING : WebSocket.CONNECTING 
    , OPEN_CLOSED : WebSocket.CLOSED 
});

window.ducts.DuctEventListener = class {
    
    constructor() {
	this.on =
	    (names, func) => {
		for(let name of (names instanceof Array) ? names : [names]) {
		    if (!(name in this)) {
			throw new ReferenceError('['+name+'] in '+this.constructor.name);
		    } 
		    this[name] = func;
		}
		
	    };
	
    }
};

window.ducts.ConnectionEventListener = class extends window.ducts.DuctEventListener {
    onopen(event){}
    onclose(event){}
    onerror(event){}
    onmessage(event){}
    
};

window.ducts.Duct = class {
    
    constructor() {
	this.WSD = null;
	this.EVENT = null;
	this.encode = null;
	this.decode = null;
	
	this.next_rid =
	    () => {return ducts._local.next_rid();};
	this.open =
	    (wsd_url, uuid = null, params = {}) => {return this._open(this, wsd_url, uuid, params);};
	this.reconnect =
	    () => {return this._reconnect(this);};
	this.send = 
	    (request_id, event_id, data) => {return this._send(this, request_id, event_id, data)};
	this.close =
	    () => {return this._close(this);};

	this._connection_listener = new window.ducts.ConnectionEventListener();
	
	this._event_handler = {};
	this.setEventHandler = 
	    (event_id, handler) => {this._event_handler[event_id] = handler;};
	this.catchall_event_handler = (rid, eid, data) => {};
	this.uncaught_event_handler = (rid, eid, data) => {};
	this.event_error_handler = (rid, eid, data, error) => {};
	
    }

    get state() {
	if (this._ws) {
	    return this._ws.readyState;
	} else {
	    return window.ducts.State.CLOSE;
	}
    }

    _reconnect(self) {
	return new Promise(function(resolve, reject) {
	    if (self._ws) {
		resolve(self);
		return;
	    }
	    let ws = new WebSocket(self.WSD.websocket_url_reconnect);
	    ws.binaryType = 'arraybuffer';
	    ws.onopen = 
		(event) => {
		    ws.onerror =
			(event) => {self._connection_listener.onerror(new window.ducts.DuctConnectionEvent('onerror', event));};
		    ws.onclose =
			(event) => {self._connection_listener.onclose(new window.ducts.DuctConnectionEvent('onclose', event));};
		    ws.onmessage = 
			(event) => {self._onmessage(self, new window.ducts.DuctConnectionEvent('onmessage', event));};
		    self._ws = ws;
		    self._onreconnect(self, event);
		    self._connection_listener.onopen(new window.ducts.DuctConnectionEvent('onopen', event));
		    resolve(self);
		};
	    ws.onerror =
		(event) => {
		    self._connection_listener.onerror(new window.ducts.DuctConnectionEvent('onerror', event));
		    reject(event);
		};
	});
    }
    
    _open(self, wsd_url, uuid, params) {
	return new Promise(function(resolve, reject) {
	    if (self._ws) {
		resolve(self);
		return;
	    }
	    window.ducts.wsd_url = wsd_url;
	    window.ducts.query = uuid != null ? uuid : '?uuid='+([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c => (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16));
	    for (let [key, value] of Object.entries(params)) {
		window.ducts.query += '&'+key+'='+value;
	    }
	    fetch(window.ducts.wsd_url + window.ducts.query)
		.then( response => {
		    return response.json();
		}).then( wsd => {
		    console.log(wsd);
		    self.WSD = wsd;
		    self.EVENT = self.WSD.EVENT;
		    console.log(self.WSD.websocket_url);
		    let ws = new WebSocket(self.WSD.websocket_url);
		    ws.binaryType = 'arraybuffer';
		    ws.onopen = 
			(event) => {
			    ws.onerror =
				(event) => {self._connection_listener.onerror(new window.ducts.DuctConnectionEvent('onerror', event));};
			    ws.onclose =
				(event) => {self._connection_listener.onclose(new window.ducts.DuctConnectionEvent('onclose', event));};
			    ws.onmessage = 
				(event) => {self._onmessage(self, new window.ducts.DuctConnectionEvent('onmessage', event));};
			    self._ws = ws;
			    self._onopen(self, event);
			    self._connection_listener.onopen(new window.ducts.DuctConnectionEvent('onopen', event));
			    resolve(self);
			};
		    ws.onerror =
			(event) => {
			    self._connection_listener.onerror(new window.ducts.DuctConnectionEvent('onerror', event));
			    reject(event);
			};
		}).catch( (error) => {
		    console.error(error);
		    self._connection_listener.onerror(new window.ducts.DuctConnectionEvent('onerror', error));
		    reject(error);
		});
	});
    }
    
    _onopen(self, event) {
	self.encode = ducts.msgpack.encode;
	self.decode = ducts.msgpack.decode;
	self._send_timestamp = new Date().getTime() / 1000;
	self.time_offset = 0;
	self.time_latency = 0;
	self._time_count = 0;
	self.setEventHandler(this.EVENT.ALIVE_MONITORING, (rid, eid, data) => {
	    let client_received = new Date().getTime() / 1000;
	    let server_sent = data[0];
	    let server_received = data[1];
	    let client_sent = this._send_timestamp;
	    //console.log('t0='+client_sent+', t1='+server_received+', t2='+server_sent+',t3='+client_received);
	    let new_offset = ((server_received - client_sent) - (client_received - server_sent))/2;
	    let new_latency = ((client_received - client_sent) - (server_sent - server_received))/2;
	    this.time_offset = (this.time_offset * this._time_count + new_offset) / (this._time_count + 1);
	    this.time_latency = (this.time_latency * this._time_count + new_latency) / (this._time_count + 1);
	    this._time_count += 1;
	    console.log('offset='+this.time_offset+', latency='+this.time_latency);
	});
	let rid = self.next_rid();
	let eid = self.EVENT.ALIVE_MONITORING;
	let value = self._send_timestamp;
	self.send(rid, eid, value);
    }
    
    _onreconnect(self, event) {
	console.log('reconnected');
    }
    
    _send(self, request_id, event_id, data) {
	const msgpack = self.encode([request_id, event_id, data])
	self._ws.send(msgpack)
	return request_id;
    }
    
    _close(self) {
	try {
	    if (self._ws) {
		self._ws.close();
	    }
	} finally {
	    self._ws = null;
	}
    }
    
    _onmessage(self, event) {
	try {
	    self._connection_listener.onmessage(event);
	    const [rid, eid, data] = self.decode(MessagePack.Buffer.from(event.source.data));
	    try {
		self.catchall_event_handler(rid, eid, data);
		let handle = (eid in self._event_handler) ? self._event_handler[eid] : self.uncaught_event_handler;
		handle(rid, eid, data);
	    } catch(error) {
		self.event_error_handler(rid, eid, data, error);
	    }
	}
	catch (error) {
	    self.event_error_handler(-1, -1, null, error);
	}
    }

};

