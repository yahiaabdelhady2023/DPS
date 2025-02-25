console.warn("Electron is working!");

const { app, BrowserWindow } = require('electron');

function CreateWindow() {
    const win=new BrowserWindow({
        width:500,
        height:500,
    });

    /*using module PATH which is a module used in Node.js since electron is built on top of Node.js it inheritates
    it's modules. 
    Path allows us to get for example python file name path in a way that it would work in any platform
    without having us to write forward slash which is for windows or backward slash which is for MacOs
    */

   path = require('path');
//    filepath= path.join(__dirname, '..', '..', 'app', 'templates', 'routes.py');
//    filepath= path.join(__dirname, '..', '..','app',  'routes.py');
   win.loadURL('http://127.0.0.1:5000/');

//    console.log(filepath);
//    win.loadFile(path.join(filepath));

}

app.whenReady().then(CreateWindow);

/*
The Below code will execute on every platform except MacOS [Darwin] because in other platforms such
as Windows and Linux closing the window of an application indicates that user wants to close the application
However in MacOS that is not the case, it can still be running even after window is closed that is the default behaviour

it is a convention
 */
app.on('window-all-closed' ,() =>{
    if (process.platform !=='darwin') {
        app.quit();
    };
});