const {app, BrowserWindow} = require("electron");
const {USE_LOCAL_SERVER} = require("./src/config/config.json")
const {spawn, execFile, exec} = require("child_process")
const treeKill = require("tree-kill")
const path = require("path");
const isDev = process.env.IS_DEV === "true";
/**
 * For loading clients in local mode
 * */

let localSever

// loading web ui
app.on("ready", () => {
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        useContentSize: true,
        show: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
    });
    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
        // mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, 'build', 'index.html'))
    }
    mainWindow.setMenuBarVisibility(false)

    // Start a local python server
    if (USE_LOCAL_SERVER) {
        localSever = spawn("python", ["-m", "pyserver.app"]);
        // localSever = execFile(path.join(__dirname, "./server/server.exe"));

        localSever.stdout.on("data", (data) => {
            console.log(`LOCAL SERVER:\n${data}`);
        });

        localSever.stderr.on("data", (data) => {
            console.error(`LOCAL SERVER:\n${data}`);
        })

    }
});

// kill the python process when closing the client
app.on("window-all-closed", () => {
    if (localSever) {
        treeKill(localSever.pid, 'SIGKILL', (err) => {
            if (err) {
                console.error('Failed to kill process tree:', err);
            } else {
                console.log('Process tree has been killed successfully.');
            }
            app.quit()
        })
    }
});
