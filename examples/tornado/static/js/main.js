(function(root) {
  
  var canvas = document.getElementsByTagName("canvas")[0];
  var ws = new WebSocketWrapper("ws://localhost:3000/ws", {msgpack: window.msgpack});
  
  ws.on("open", function(e) {
    ws.on("print", function(data) { console.log(data); });
    ws.emit("setup");
  });
  ws.on("close", function(e) { console.log(e); });
  ws.on("error", function(e) { console.log(e); });

})(window);
