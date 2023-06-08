const { app, ipcMain, BrowserWindow } = require("electron");
// const remoteMain = require("@electron/remote/main");
// remoteMain.initialize();
const process = require("process");
const path = require("path");
// const axios = require("axios");
// const utils = require("./script/utils");
// require("electron-reloader")(module);
const isDev = process.env.IS_DEV == "true" ? true : false;
app.on("ready", () => {
  const mainWindow = new BrowserWindow({
    width: 1024,
    height: 600,
    useContentSize: true,
    show: true,
    // frame: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, "preload.js"),
    },
  });
  // remoteMain.enable(mainWindow.webContents);
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    // mainWindow.removeMenu();
    mainWindow.loadFile(path.join(__dirname, 'build', 'index.html'));
  }
  mainWindow.setMenuBarVisibility(false)
});

// ipcMain.on("child_pid", function (event, arg) {
//   console.log("Main:", arg);
//   pids.push(arg);
// });

// ipcMain.on("mainWindow-close", () => {
//   if (process.platform !== "darwin") app.quit();
// });

// ipcMain.on("mainWindow-min", () => {
//   mainWindow.minimize();
// });
