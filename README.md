WebSocket Wrapper for JavaScript
================================

This project provides a wrapper class of WebSocket for JavaScript and defines subprotocols for WebSocket.

Subprotocols
------------

WebSocket wrapper defines two subprotocols -- _wswrapper_json_ and _wswrapper_msgpack_. JSON is used as sending data format in _wswrapper_json_, and MessagePack is used in _wswrapper_msgpack_. WebSocket servers have to support at least one of these subprotocols, but adopting no subprotocols is allowed for the servers that don't support subprotocols at all.

Data Format
-----------

	[eventName: String, payload: Object]

The sending data consists of a tuple of the event name and the payload, and its format is JSON or MessagePack. The payload can include raw binary data in MessagePack, but in JSON, the binary data is converted to text such as base64.


Documentation
-------------

### Connection

```javascript
url = "ws://localhost/ws";
// JSON.
ws = new WebSocketWrapper(url);
// msgpack. window.msgpack is the object that has `pack` and `unpack` methods in properties.
ws = new WebSocketWrapper(url, {msgpack: window.msgpack});
// not use subprotocols of wswrapper
ws = new WebSocketWrapper(url, {protocol: false});
```

Some hooks are also available. (Currently, only "onmessage" hook is available.)

```javascript
ws = new WebSocketWrapper(url, {
  msgpack: window.msgpack,
  hooks: {
    onmessage: function(d) {
      if (typeof(d) === "string") {
      	console.log(d.toUpperCase());
      	return null; // The data isn't be passed to handlers.
      }
      return d; // This return data is passed to handlers
    }
  }
});
```

### Built-in events

'open', 'close', and 'error' are special event names. Each event has only one handler.

```javascript
ws.on("open", function(e) { console.log(e); });
ws.on("close", function(e) { console.log(e); });
ws.on("error", function(e) { console.log(e); });
// override event handler
ws.on("open", function(e) { ws.emit("hello", "world"); });
// destroy event
ws.off("open");
```

### Custom events

Any event names without 'open', 'close', and 'error' can be used for custom events.

```javascript
// custom events
ws.on("hello", function(payload) { console.log(payload); });
// destroy events
ws.off("hello");
```

### Send data

Any data not limited by the data format (JSON or MessagePack) can be sent to the remote by `ws.emit(eventName, data=null)`.

```javascript
ws.on("open", function(e) {
  ws.on("do something", function(data) {
    // In the case of JSON
    var raw_data = window.btoa(data);
    var result = window.atob(raw_data);
  	ws.emit("something done", {
  	  foo: "bar",
  	  data: result
  	});
  });
  ws.emit("setup finished", {information: "for initialize"});
});
```

License
-------

The MIT License

