const {app, BrowserWindow} = require("electron");
const {USE_LOCAL_SERVER} = require("./src/config/config.json")
const {spawn, execFile} = require("child_process")
const kill = require("tree-kill")
const path = require("path");
const isDev = process.env.IS_DEV === "true";

let localSever

app.on("ready", () => {
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        useContentSize: true,
        show: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            // preload: path.join(__dirname, "preload.js"),
        },
    });
    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, 'build', 'index.html'))
    }
    mainWindow.setMenuBarVisibility(false)

    // Start a local server
    if (USE_LOCAL_SERVER) {
        localSever = spawn("python", ["./python/app.py"]);
        // localSever = execFile(path.join(__dirname, "./server/server.exe"));

        localSever.stdout.on("data", (data) => {
            console.log(`LOCAL SERVER:\n${data}`);
        });

        localSever.stderr.on("data", (data) => {
            console.error(`LOCAL SERVER:\n${data}`);
        })

    }
});

app.on("window-all-closed", () => {
    if (localSever) {
        kill(localSever.pid)
    }
    app.quit()
});
