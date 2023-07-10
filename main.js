const {app, BrowserWindow} = require("electron");

const process = require("process");
const path = require("path");
const isDev = process.env.IS_DEV === "true";

app.on("ready", () => {
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        useContentSize: true,
        show: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            preload: path.join(__dirname, "preload.js"),
        },
    });
    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, 'build', 'index.html'));
    }
    mainWindow.setMenuBarVisibility(false)
});

