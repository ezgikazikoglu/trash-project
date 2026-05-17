const { app, BrowserWindow, shell } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const http = require('http')

let mainWindow = null
let backendProcess = null

function getBackendPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'backend', 'server.exe')
  }
  return path.join(__dirname, '..', '..', 'backend', 'dist', 'server', 'server.exe')
}

function getFrontendPath() {
  // Packaged: app.asar/electron/ → app.asar/dist/index.html
  // Dev:      frontend/electron/ → frontend/dist/index.html
  return path.join(__dirname, '..', 'dist', 'index.html')
}

function startBackend() {
  const exePath = getBackendPath()
  console.log('Backend:', exePath)
  backendProcess = spawn(exePath, [], { stdio: 'ignore', detached: false })
  backendProcess.on('error', (err) => console.error('Backend hatası:', err))
}

function waitForBackend(retries = 40, delay = 500) {
  return new Promise((resolve, reject) => {
    const check = (n) => {
      http.get('http://localhost:8000/health', (res) => {
        if (res.statusCode === 200) resolve()
        else retry(n)
      }).on('error', () => retry(n))
    }
    const retry = (n) => {
      if (n <= 0) return reject(new Error('Backend 20 saniyede başlamadı'))
      setTimeout(() => check(n - 1), delay)
    }
    check(retries)
  })
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 720,
    minWidth: 640,
    minHeight: 500,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    title: 'Atık Sınıflandırıcı',
    backgroundColor: '#f0fdf4',
    show: false,
  })

  mainWindow.loadFile(getFrontendPath())
  mainWindow.once('ready-to-show', () => mainWindow.show())

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })
}

app.whenReady().then(async () => {
  startBackend()
  try {
    await waitForBackend()
    createWindow()
  } catch (err) {
    console.error(err.message)
    app.quit()
  }
})

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill()
  app.quit()
})

app.on('before-quit', () => {
  if (backendProcess) backendProcess.kill()
})
