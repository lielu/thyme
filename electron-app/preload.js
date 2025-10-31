/**
 * Preload Script - Secure Bridge between Main and Renderer Processes
 * 
 * This script runs in a privileged context and exposes safe APIs to the renderer.
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Time and date
  getTime: () => ipcRenderer.invoke('get-time'),
  onTimeUpdate: (callback) => {
    ipcRenderer.on('time-update', () => callback());
    return () => ipcRenderer.removeAllListeners('time-update');
  },
  
  // Calendar events
  getCalendarEvents: () => ipcRenderer.invoke('get-calendar-events'),
  onCalendarUpdate: (callback) => {
    ipcRenderer.on('calendar-update', (event, data) => callback(data));
    return () => ipcRenderer.removeAllListeners('calendar-update');
  },
  
  // Weather data
  getWeather: () => ipcRenderer.invoke('get-weather'),
  onWeatherUpdate: (callback) => {
    ipcRenderer.on('weather-update', (event, data) => callback(data));
    return () => ipcRenderer.removeAllListeners('weather-update');
  },
  
  // Discord messages
  getDiscordMessages: () => ipcRenderer.invoke('get-discord-messages'),
  onDiscordUpdate: (callback) => {
    ipcRenderer.on('discord-update', (event, data) => callback(data));
    return () => ipcRenderer.removeAllListeners('discord-update');
  },
  
  // Alarms
  getAlarms: () => ipcRenderer.invoke('get-alarms'),
  getAllAlarmTimes: () => ipcRenderer.invoke('get-all-alarm-times'),
  addAlarm: (time) => ipcRenderer.invoke('add-alarm', time),
  deleteAlarm: (time) => ipcRenderer.invoke('delete-alarm', time),
  onAlarmTrigger: (callback) => {
    ipcRenderer.on('alarm-trigger', (event, data) => callback(data));
    return () => ipcRenderer.removeAllListeners('alarm-trigger');
  },
  
  // Background images
  getBackgroundImage: () => ipcRenderer.invoke('get-background-image'),
  onBackgroundUpdate: (callback) => {
    ipcRenderer.on('background-update', (event, data) => callback(data));
    return () => ipcRenderer.removeAllListeners('background-update');
  },
  
  // Settings
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  resetSettings: () => ipcRenderer.invoke('reset-settings'),
  
  // App control
  exitApp: () => ipcRenderer.send('app-exit'),
  reloadConfig: () => ipcRenderer.send('reload-config'),
  
  // Platform info
  getPlatform: () => ipcRenderer.invoke('get-platform')
});

console.log('Preload script loaded successfully');

