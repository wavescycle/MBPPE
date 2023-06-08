const { ipcRenderer } = require("electron");

function runServer() {
  var python = require("child_process").spawn("python", ["./python/app.py"]);
  // var python = require("child_process").execFile(
  //   path.join(__dirname, "./server/server.exe")
  // );
  ipcRenderer.send("child_pid", python.pid);

  python.stdout.on("data", function (data) {
    console.log(`child：${data}`);
  });

  python.on("close", (code) => {
    console.log(`child process exited with code ${code}`);
  });
}

runServer();
