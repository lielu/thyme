/**
 * Configuration Manager
 * Handles loading, saving, and accessing application configuration
 */

const fs = require('fs').promises;
const path = require('path');

class Config {
  constructor() {
    this.configPath = path.join(__dirname, '..', 'config', 'alarm_config.json');
    this.config = this.getDefaultConfig();
    this.load();
  }
  
  getDefaultConfig() {
    return {
      // Application settings
      hideCursor: true,
      fullscreen: true,
      
      // Calendar settings
      calendarId: 'primary',
      
      // Weather settings
      latitude: 32.7767,
      longitude: -96.7970,
      timezone: 'America/Chicago',
      temperatureUnit: 'fahrenheit',
      
      // Discord settings
      discordToken: '',
      discordChannelId: '',
      
      // Display schedule
      displayOffTime: '',
      displayOnTime: '',
      
      // Alarms
      alarms: [],
      
      // UI settings
      clockFontSize: 120,
      dateFontSize: 36,
      alarmsFontSize: 24,
      eventsFontSize: 32,
      weatherFontSize: 28,
      
      // Update intervals (milliseconds)
      eventsRefreshInterval: 10000,
      weatherUpdateInterval: 3600000,
      discordUpdateInterval: 10000,
      backgroundChangeInterval: 30000
    };
  }
  
  async load() {
    try {
      const data = await fs.readFile(this.configPath, 'utf8');
      const loaded = JSON.parse(data);
      this.config = { ...this.getDefaultConfig(), ...loaded };
      console.log('Configuration loaded successfully');
    } catch (error) {
      if (error.code === 'ENOENT') {
        console.log('Configuration file not found, using defaults');
        await this.save();
      } else {
        console.error('Error loading configuration:', error);
      }
    }
  }
  
  async save() {
    try {
      const dir = path.dirname(this.configPath);
      await fs.mkdir(dir, { recursive: true });
      await fs.writeFile(this.configPath, JSON.stringify(this.config, null, 2));
      console.log('Configuration saved successfully');
    } catch (error) {
      console.error('Error saving configuration:', error);
      throw error;
    }
  }
  
  get(key) {
    return this.config[key];
  }
  
  set(key, value) {
    this.config[key] = value;
  }
  
  getAll() {
    return { ...this.config };
  }
  
  async saveSettings(settings) {
    this.config = { ...this.config, ...settings };
    await this.save();
  }
  
  async resetToDefaults() {
    this.config = this.getDefaultConfig();
    await this.save();
  }
  
  async reload() {
    await this.load();
  }
}

module.exports = Config;

