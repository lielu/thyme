/**
 * Main Process Entry Point
 * Thyme Kiosk Clock - Electron Edition
 */

const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const Config = require('./config');
const AlarmManager = require('./managers/AlarmManager');
const AudioManager = require('./managers/AudioManager');
const BackgroundManager = require('./managers/BackgroundManager');
const CalendarManager = require('./managers/CalendarManager');
const DiscordManager = require('./managers/DiscordManager');
const WeatherManager = require('./managers/WeatherManager');
const { formatDate, formatTime } = require('./utils');

class ThymeApp {
  constructor() {
    this.mainWindow = null;
    this.config = new Config();
    this.managers = {};
    this.updateIntervals = {};
    
    // Handle app lifecycle
    app.whenReady().then(() => this.onReady());
    
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        this.cleanup();
        app.quit();
      }
    });
    
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createWindow();
      }
    });
    
    app.on('before-quit', () => {
      this.cleanup();
    });
  }
  
  async onReady() {
    console.log('Thyme Kiosk Clock starting...');
    
    // Wait for config to load
    await this.config.load();
    
    this.createWindow();
    this.initializeManagers();
    this.setupIpcHandlers();
    this.startPeriodicUpdates();
    
    console.log('Thyme Kiosk Clock ready');
  }
  
  createWindow() {
    const display = screen.getPrimaryDisplay();
    const { width, height } = display.workAreaSize;
    
    const windowOptions = {
      width,
      height,
      backgroundColor: '#000000',
      show: false, // Don't show until ready
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, '..', 'preload.js')
      }
    };
    
    // Apply fullscreen if configured
    if (this.config.get('fullscreen')) {
      windowOptions.fullscreen = true;
      windowOptions.frame = false;
    }
    
    this.mainWindow = new BrowserWindow(windowOptions);
    
    // Load the app
    this.mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
    
    // Show when ready
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
      
      // Hide cursor if configured
      if (this.config.get('hideCursor')) {
        this.mainWindow.webContents.insertCSS('* { cursor: none !important; }');
      }
    });
    
    // Development mode
    if (process.argv.includes('--dev')) {
      this.mainWindow.webContents.openDevTools();
    }
    
    console.log(`Window created: ${width}x${height}`);
  }
  
  initializeManagers() {
    console.log('Initializing managers...');
    
    try {
      this.managers.alarm = new AlarmManager(this.config);
      this.managers.audio = new AudioManager(this.config);
      this.managers.background = new BackgroundManager(this.config);
      this.managers.calendar = new CalendarManager(this.config);
      this.managers.discord = new DiscordManager(this.config);
      this.managers.weather = new WeatherManager(this.config);
      
      // Listen for alarm events
      this.managers.alarm.on('alarm', (alarmTime) => {
        this.handleAlarm(alarmTime);
      });
      
      console.log('All managers initialized');
    } catch (error) {
      console.error('Error initializing managers:', error);
    }
  }
  
  setupIpcHandlers() {
    // Time and date
    ipcMain.handle('get-time', () => {
      const now = new Date();
      return {
        time: formatTime(now, true),
        date: formatDate(now)
      };
    });
    
    // Calendar events
    ipcMain.handle('get-calendar-events', async () => {
      try {
        return await this.managers.calendar.fetchTodaysEvents();
      } catch (error) {
        console.error('Error getting calendar events:', error);
        return ['Error loading events'];
      }
    });
    
    // Weather data
    ipcMain.handle('get-weather', async () => {
      try {
        return await this.managers.weather.fetchWeatherData();
      } catch (error) {
        console.error('Error getting weather:', error);
        return this.managers.weather.getFallbackWeather();
      }
    });
    
    // Discord messages
    ipcMain.handle('get-discord-messages', () => {
      try {
        return this.managers.discord.getRecentMessages();
      } catch (error) {
        console.error('Error getting Discord messages:', error);
        return ['Discord unavailable'];
      }
    });
    
    // Alarms
    ipcMain.handle('get-alarms', () => {
      return this.managers.alarm.getAlarmSummary();
    });
    
    ipcMain.handle('get-all-alarm-times', () => {
      return this.managers.alarm.getAllAlarmTimes();
    });
    
    ipcMain.handle('add-alarm', async (event, time) => {
      try {
        await this.managers.alarm.addAlarm(time);
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });
    
    ipcMain.handle('delete-alarm', async (event, time) => {
      try {
        await this.managers.alarm.deleteAlarm(time);
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });
    
    // Background image
    ipcMain.handle('get-background-image', async () => {
      try {
        const bgPath = await this.managers.background.getRandomBackground();
        return bgPath ? `file://${bgPath}` : null;
      } catch (error) {
        console.error('Error getting background:', error);
        return null;
      }
    });
    
    // Settings
    ipcMain.handle('get-settings', () => {
      return this.config.getAll();
    });
    
    ipcMain.handle('save-settings', async (event, settings) => {
      try {
        await this.config.saveSettings(settings);
        
        // Reload managers if necessary
        if (settings.alarms !== undefined) {
          await this.managers.alarm.setAlarms(settings.alarms);
        }
        
        return { success: true };
      } catch (error) {
        console.error('Error saving settings:', error);
        return { success: false, error: error.message };
      }
    });
    
    ipcMain.handle('reset-settings', async () => {
      try {
        await this.config.resetToDefaults();
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });
    
    // Platform info
    ipcMain.handle('get-platform', () => {
      return {
        platform: process.platform,
        arch: process.arch,
        version: app.getVersion()
      };
    });
    
    // App control
    ipcMain.on('app-exit', () => {
      console.log('Exit requested');
      this.cleanup();
      app.quit();
    });
    
    ipcMain.on('reload-config', async () => {
      console.log('Reloading configuration');
      await this.config.reload();
      this.managers.alarm.loadAlarms();
    });
  }
  
  startPeriodicUpdates() {
    // Update time every second
    this.updateIntervals.time = setInterval(() => {
      if (this.mainWindow && !this.mainWindow.isDestroyed()) {
        this.mainWindow.webContents.send('time-update');
      }
    }, 1000);
    
    // Update calendar events
    const eventsInterval = this.config.get('eventsRefreshInterval') || 10000;
    this.updateIntervals.calendar = setInterval(async () => {
      if (this.mainWindow && !this.mainWindow.isDestroyed()) {
        try {
          const events = await this.managers.calendar.fetchTodaysEvents();
          this.mainWindow.webContents.send('calendar-update', events);
        } catch (error) {
          console.error('Error in calendar update:', error);
        }
      }
    }, eventsInterval);
    
    // Update weather
    const weatherInterval = this.config.get('weatherUpdateInterval') || 3600000;
    this.updateIntervals.weather = setInterval(async () => {
      if (this.mainWindow && !this.mainWindow.isDestroyed()) {
        try {
          const weather = await this.managers.weather.fetchWeatherData();
          this.mainWindow.webContents.send('weather-update', weather);
        } catch (error) {
          console.error('Error in weather update:', error);
        }
      }
    }, weatherInterval);
    
    // Update Discord messages
    const discordInterval = this.config.get('discordUpdateInterval') || 10000;
    this.updateIntervals.discord = setInterval(async () => {
      if (this.mainWindow && !this.mainWindow.isDestroyed()) {
        try {
          await this.managers.discord.fetchRecentMessages();
          const messages = this.managers.discord.getRecentMessages();
          this.mainWindow.webContents.send('discord-update', messages);
        } catch (error) {
          console.error('Error in Discord update:', error);
        }
      }
    }, discordInterval);
    
    // Change background
    const bgInterval = this.config.get('backgroundChangeInterval') || 30000;
    this.updateIntervals.background = setInterval(async () => {
      if (this.mainWindow && !this.mainWindow.isDestroyed()) {
        try {
          const bgPath = await this.managers.background.getRandomBackground();
          if (bgPath) {
            this.mainWindow.webContents.send('background-update', `file://${bgPath}`);
          }
        } catch (error) {
          console.error('Error in background update:', error);
        }
      }
    }, bgInterval);
    
    console.log('Periodic updates started');
  }
  
  async handleAlarm(alarmTime) {
    console.log(`Alarm triggered: ${alarmTime}`);
    
    try {
      // Play alarm sound
      await this.managers.audio.playAlarm();
      
      // Send visual notification to renderer
      if (this.mainWindow && !this.mainWindow.isDestroyed()) {
        this.mainWindow.webContents.send('alarm-trigger', { time: alarmTime });
      }
      
      // Announce events via TTS after 2 second delay
      setTimeout(async () => {
        try {
          const speechText = await this.managers.calendar.getUpcomingEventsForSpeech();
          await this.managers.audio.speak(speechText);
        } catch (error) {
          console.error('Error in TTS announcement:', error);
        }
      }, 2000);
      
    } catch (error) {
      console.error('Error handling alarm:', error);
    }
  }
  
  cleanup() {
    console.log('Cleaning up application...');
    
    // Clear intervals
    Object.values(this.updateIntervals).forEach(interval => {
      if (interval) clearInterval(interval);
    });
    this.updateIntervals = {};
    
    // Cleanup managers
    Object.values(this.managers).forEach(manager => {
      if (manager && typeof manager.cleanup === 'function') {
        try {
          manager.cleanup();
        } catch (error) {
          console.error('Error cleaning up manager:', error);
        }
      }
    });
    
    console.log('Cleanup completed');
  }
}

// Start the application
new ThymeApp();

