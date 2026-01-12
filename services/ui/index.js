
const http = require("http");

http.createServer((req, res) => {
  res.end("Incident Management UI is running");
}).listen(3000);
