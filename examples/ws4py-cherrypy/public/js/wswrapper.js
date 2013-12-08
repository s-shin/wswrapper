// (C) 2013 Shintaro Seki <s2pch.luck@gmail.com>
// License: The MIT License
(function(root) {
  
  function WebSocketWrapper(url, opts) {
    if (arguments.length == 1)
      return new WebSocketWrapper(url, {});
    
    var DEFAULT_OPTS = {
      // If subprotocols of wswrapper are used, set true.
      protocol: true,
      // If msgpack is used, set msgpack object that has `pack` and `unpack`
      // methods in properties.
      msgpack: null,
      // Set some hooks.
      hooks: {
        onmessage: function(d) { return d; }
      }
    };
    
    function getPropSetter(dst, src) {
      return function(prop) {
        if (!(prop in dst))
          dst[prop] = src[prop];
      };
    };
    
    var set1 = getPropSetter(opts, DEFAULT_OPTS);
    set1("protocol");
    set1("msgpack");
    if ("hooks" in opts) {
      var set2 = getPropSetter(opts.hooks, DEFAULT_OPTS.hooks);
      set2("onmessage");
    } else {
      set1("hooks");
    }
    
    var protocols = [];
    if (opts.protocol) {
      if (opts.msgpack)
        protocols.push("wswrapper_msgpack");
      else
        protocols.push("wswrapper_json");
    }
    var ws = new WebSocket(url, protocols);
    ws.binaryType = "arraybuffer";
    var handlers = {};
    
    // built-in handlers
    ["open", "close", "error"].forEach(function(name) {
      ws.addEventListener(name, function() {
        if (name in handlers) {
          var fn = handlers[name];
          if (fn instanceof Function)
            fn.apply(fn, arguments);
        }
      });
    });
    
    // custom handlers
    ws.addEventListener("message", function(e) {
      var data = e.data;
      // The process stop if the hook return null.
      data = opts.hooks.onmessage(data);
      if (!data) return;
      // unpack
      data = (typeof(data) !== "string" && opts.msgpack)
        ? opts.msgpack.unpack(new Uint8Array(data))
        : JSON.parse(data);
      var name = data[0], payload = data[1];
      if (name in handlers)
        handlers[name](payload);
    });
    
    this.ws_ = ws;
    this.handlers_ = handlers;
    this.opts_ = opts;
  }
  
  WebSocketWrapper.prototype = {
    on: function(name, callback) {
      this.handlers_[name] = callback;
    },
    off: function(name) {
      delete this.handlers_[name];
    },
    emit: function(name, payload, forceJSON) {
      var data = [name, payload];
      if (!forceJSON && this.opts_.msgpack) {
        data = this.opts_.msgpack.pack(data);
        data = new Uint8Array(data);
        data = data.buffer;
      } else {
        data = JSON.stringify(data);
      }
      this.ws_.send(data);
    },
    close: function() {
      this.ws_.close();
    }
  };
  
  root.WebSocketWrapper = WebSocketWrapper;

})(this);
