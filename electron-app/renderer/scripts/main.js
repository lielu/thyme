/**
 * Main Renderer Script
 * Handles UI updates and user interactions
 */

class ThymeUI {
  constructor() {
    this.elements = {};
    this.unsubscribers = [];
    this.alarmTimeout = null;
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.init());
    } else {
      this.init();
    }
  }
  
  init() {
    console.log('Initializing Thyme UI...');
    this.cacheElements();
    this.setupEventListeners();
    this.setupIpcListeners();
    this.startInitialUpdates();
    console.log('Thyme UI initialized');
  }
  
  cacheElements() {
    this.elements = {
      clock: document.getElementById('clock'),
      date: document.getElementById('date'),
      alarmsList: document.getElementById('alarms-list'),
      eventsList: document.getElementById('events-list'),
      discordMessages: document.getElementById('discord-messages'),
      weatherText: document.getElementById('weather-text'),
      weatherIcon: document.getElementById('weather-icon'),
      background: document.getElementById('background'),
      alarmOverlay: document.getElementById('alarm-overlay'),
      settingsIcon: document.getElementById('settings-icon'),
      settingsOverlay: document.getElementById('settings-overlay')
    };
  }
  
  setupEventListeners() {
    // Settings button
    this.elements.settingsIcon.addEventListener('click', () => {
      window.settingsUI.open();
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (!this.elements.settingsOverlay.classList.contains('hidden')) {
          window.settingsUI.close();
        } else {
          // Exit app on Escape when settings are not open
          window.electronAPI.exitApp();
        }
      } else if (e.key === 'F5') {
        // Reload configuration
        window.electronAPI.reloadConfig();
        this.startInitialUpdates();
      } else if (e.key === 'F6') {
        // Open settings
        window.settingsUI.open();
      }
    });
  }
  
  setupIpcListeners() {
    // Time updates
    const timeUnsubscribe = window.electronAPI.onTimeUpdate(() => {
      this.updateTime();
    });
    this.unsubscribers.push(timeUnsubscribe);
    
    // Calendar updates
    const calendarUnsubscribe = window.electronAPI.onCalendarUpdate((events) => {
      this.updateEvents(events);
    });
    this.unsubscribers.push(calendarUnsubscribe);
    
    // Weather updates
    const weatherUnsubscribe = window.electronAPI.onWeatherUpdate((weather) => {
      this.updateWeather(weather);
    });
    this.unsubscribers.push(weatherUnsubscribe);
    
    // Discord updates
    const discordUnsubscribe = window.electronAPI.onDiscordUpdate((messages) => {
      this.updateDiscord(messages);
    });
    this.unsubscribers.push(discordUnsubscribe);
    
    // Background updates
    const backgroundUnsubscribe = window.electronAPI.onBackgroundUpdate((backgroundUrl) => {
      this.updateBackground(backgroundUrl);
    });
    this.unsubscribers.push(backgroundUnsubscribe);
    
    // Alarm triggers
    const alarmUnsubscribe = window.electronAPI.onAlarmTrigger((alarmData) => {
      this.showAlarmNotification(alarmData);
    });
    this.unsubscribers.push(alarmUnsubscribe);
  }
  
  async startInitialUpdates() {
    try {
      // Initial data fetch
      await Promise.all([
        this.updateTime(),
        this.updateAlarms(),
        this.updateEvents(),
        this.updateWeather(),
        this.updateDiscord(),
        this.updateBackground()
      ]);
      console.log('Initial updates completed');
    } catch (error) {
      console.error('Error during initial updates:', error);
    }
  }
  
  async updateTime() {
    try {
      const { time, date } = await window.electronAPI.getTime();
      this.elements.clock.textContent = time;
      this.elements.date.textContent = date;
    } catch (error) {
      console.error('Error updating time:', error);
    }
  }
  
  async updateAlarms() {
    try {
      const alarms = await window.electronAPI.getAlarms();
      this.elements.alarmsList.textContent = alarms;
    } catch (error) {
      console.error('Error updating alarms:', error);
      this.elements.alarmsList.textContent = 'Error loading alarms';
    }
  }
  
  async updateEvents(events = null) {
    try {
      if (!events) {
        events = await window.electronAPI.getCalendarEvents();
      }
      
      if (!events || events.length === 0) {
        this.elements.eventsList.textContent = 'No events today';
      } else {
        this.elements.eventsList.innerHTML = events.join('<br>');
      }
    } catch (error) {
      console.error('Error updating events:', error);
      this.elements.eventsList.textContent = 'Error loading events';
    }
  }
  
  async updateWeather(weather = null) {
    try {
      if (!weather) {
        weather = await window.electronAPI.getWeather();
      }
      
      if (weather) {
        this.elements.weatherText.textContent = weather.tempText || '--° / --°';
        
        if (weather.iconPath) {
          this.elements.weatherIcon.src = `file://${weather.iconPath}`;
          this.elements.weatherIcon.alt = weather.iconFilename || 'Weather';
        }
      }
    } catch (error) {
      console.error('Error updating weather:', error);
      this.elements.weatherText.textContent = 'Weather unavailable';
    }
  }
  
  async updateDiscord(messages = null) {
    try {
      if (!messages) {
        messages = await window.electronAPI.getDiscordMessages();
      }
      
      if (!messages || messages.length === 0) {
        this.elements.discordMessages.textContent = 'No recent messages';
      } else {
        this.elements.discordMessages.innerHTML = messages.join('<br>');
      }
    } catch (error) {
      console.error('Error updating Discord:', error);
      this.elements.discordMessages.textContent = 'Discord unavailable';
    }
  }
  
  async updateBackground(backgroundUrl = null) {
    try {
      if (!backgroundUrl) {
        backgroundUrl = await window.electronAPI.getBackgroundImage();
      }
      
      if (backgroundUrl) {
        // Create a new image to preload
        const img = new Image();
        img.onload = () => {
          // Fade transition
          this.elements.background.style.opacity = '0';
          
          setTimeout(() => {
            this.elements.background.style.backgroundImage = `url('${backgroundUrl}')`;
            this.elements.background.style.opacity = '1';
          }, 500);
        };
        img.src = backgroundUrl;
      }
    } catch (error) {
      console.error('Error updating background:', error);
    }
  }
  
  showAlarmNotification(alarmData) {
    console.log('Showing alarm notification:', alarmData);
    
    // Clear any existing timeout
    if (this.alarmTimeout) {
      clearTimeout(this.alarmTimeout);
    }
    
    // Show overlay
    this.elements.alarmOverlay.classList.remove('hidden');
    
    // Hide after 10 seconds
    this.alarmTimeout = setTimeout(() => {
      this.hideAlarmNotification();
    }, 10000);
    
    // Allow clicking to dismiss
    const dismissHandler = () => {
      this.hideAlarmNotification();
      this.elements.alarmOverlay.removeEventListener('click', dismissHandler);
    };
    this.elements.alarmOverlay.addEventListener('click', dismissHandler);
  }
  
  hideAlarmNotification() {
    this.elements.alarmOverlay.classList.add('hidden');
    if (this.alarmTimeout) {
      clearTimeout(this.alarmTimeout);
      this.alarmTimeout = null;
    }
  }
  
  cleanup() {
    // Unsubscribe from all IPC listeners
    this.unsubscribers.forEach(unsubscribe => {
      if (typeof unsubscribe === 'function') {
        unsubscribe();
      }
    });
    this.unsubscribers = [];
    
    // Clear timeouts
    if (this.alarmTimeout) {
      clearTimeout(this.alarmTimeout);
    }
  }
}

// Initialize the UI
window.thymeUI = new ThymeUI();

// Cleanup on unload
window.addEventListener('beforeunload', () => {
  if (window.thymeUI) {
    window.thymeUI.cleanup();
  }
});

