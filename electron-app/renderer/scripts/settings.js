/**
 * Settings UI Manager
 * Handles settings panel and user preferences
 */

class SettingsUI {
  constructor() {
    this.overlay = null;
    this.currentSettings = {};
    this.alarms = [];
  }
  
  async open() {
    try {
      // Load current settings
      this.currentSettings = await window.electronAPI.getSettings();
      this.alarms = await window.electronAPI.getAllAlarmTimes();
      
      // Create settings panel
      this.createSettingsPanel();
      
      // Show overlay
      const overlay = document.getElementById('settings-overlay');
      overlay.classList.remove('hidden');
      
      // Check calendar authentication status
      await this.updateCalendarAuthStatus();
      
    } catch (error) {
      console.error('Error opening settings:', error);
      alert('Failed to open settings');
    }
  }
  
  close() {
    const overlay = document.getElementById('settings-overlay');
    overlay.classList.add('hidden');
    overlay.innerHTML = '';
  }
  
  createSettingsPanel() {
    const overlay = document.getElementById('settings-overlay');
    
    const panel = document.createElement('div');
    panel.className = 'settings-panel';
    panel.innerHTML = `
      <div class="settings-header">
        <div class="settings-title">⚙️ Settings</div>
        <button class="settings-close" id="settings-close">✕</button>
      </div>
      
      <div class="settings-content">
        ${this.createGeneralSection()}
        ${this.createCalendarSection()}
        ${this.createWeatherSection()}
        ${this.createDiscordSection()}
        ${this.createAlarmsSection()}
      </div>
      
      <div class="settings-footer">
        <button class="btn btn-danger" id="settings-reset">Reset to Defaults</button>
        <div>
          <button class="btn btn-secondary" id="settings-cancel">Cancel</button>
          <button class="btn btn-primary" id="settings-save" style="margin-left: 12px;">💾 Save & Apply</button>
        </div>
      </div>
    `;
    
    overlay.innerHTML = '';
    overlay.appendChild(panel);
    
    // Setup event listeners
    this.setupSettingsEventListeners();
  }
  
  createGeneralSection() {
    return `
      <div class="settings-section">
        <h3>🖥️ Display Settings</h3>
        
        <div class="settings-field">
          <label for="setting-fullscreen">
            <input type="checkbox" id="setting-fullscreen" ${this.currentSettings.fullscreen ? 'checked' : ''}>
            Fullscreen Mode
          </label>
          <div class="settings-help-text">Run in fullscreen mode (recommended for kiosk)</div>
        </div>
        
        <div class="settings-field">
          <label for="setting-hide-cursor">
            <input type="checkbox" id="setting-hide-cursor" ${this.currentSettings.hideCursor ? 'checked' : ''}>
            Hide Mouse Cursor
          </label>
          <div class="settings-help-text">Hide the cursor for a cleaner look</div>
        </div>
      </div>
    `;
  }
  
  createCalendarSection() {
    return `
      <div class="settings-section">
        <h3>📅 Google Calendar</h3>
        
        <div class="settings-field">
          <label for="setting-calendar-id">Calendar ID</label>
          <input type="text" id="setting-calendar-id" 
                 value="${this.escapeHtml(this.currentSettings.calendarId || 'primary')}"
                 placeholder="primary">
          <div class="settings-help-text">Your Gmail address or calendar ID (use 'primary' for main calendar)</div>
        </div>
        
        <div class="settings-field" style="margin-top: 20px;">
          <label>Authentication Status</label>
          <div id="calendar-auth-status" style="padding: 12px; background: #3c3c3c; border-radius: 6px; margin-bottom: 12px;">
            <span style="color: #9a9a9a;">Checking...</span>
          </div>
          <button class="btn btn-primary" id="calendar-auth-button" style="width: 100%;">
            🔐 Authenticate with Google Calendar
          </button>
          <div class="settings-help-text" style="margin-top: 8px;">
            Click to sign in with your Google account and grant calendar access
          </div>
        </div>
        
        <div class="settings-help-text" style="margin-top: 16px; padding: 12px; background: #2d2d30; border-radius: 6px;">
          <strong>Setup Instructions:</strong><br>
          1. Get your <code>credentials.json</code> from <a href="https://console.cloud.google.com" target="_blank" style="color: #0078d4;">Google Cloud Console</a><br>
          2. Place it in the <code>config/</code> directory<br>
          3. Click "Authenticate" button above<br>
          4. Sign in and grant calendar access
        </div>
      </div>
    `;
  }
  
  createWeatherSection() {
    return `
      <div class="settings-section">
        <h3>🌤️ Weather & Location</h3>
        
        <div class="settings-field">
          <label for="setting-latitude">Latitude</label>
          <input type="number" id="setting-latitude" 
                 value="${this.currentSettings.latitude || 32.7767}"
                 step="0.0001"
                 placeholder="32.7767">
          <div class="settings-help-text">Decimal format (e.g., 32.7767 for Dallas, TX)</div>
        </div>
        
        <div class="settings-field">
          <label for="setting-longitude">Longitude</label>
          <input type="number" id="setting-longitude" 
                 value="${this.currentSettings.longitude || -96.7970}"
                 step="0.0001"
                 placeholder="-96.7970">
          <div class="settings-help-text">Decimal format (e.g., -96.7970 for Dallas, TX)</div>
        </div>
        
        <div class="settings-field">
          <label for="setting-timezone">Timezone</label>
          <select id="setting-timezone">
            ${this.createTimezoneOptions()}
          </select>
          <div class="settings-help-text">Select your timezone</div>
        </div>
        
        <div class="settings-field">
          <label for="setting-temp-unit">Temperature Unit</label>
          <select id="setting-temp-unit">
            <option value="fahrenheit" ${this.currentSettings.temperatureUnit === 'fahrenheit' ? 'selected' : ''}>Fahrenheit (°F)</option>
            <option value="celsius" ${this.currentSettings.temperatureUnit === 'celsius' ? 'selected' : ''}>Celsius (°C)</option>
          </select>
        </div>
      </div>
    `;
  }
  
  createDiscordSection() {
    return `
      <div class="settings-section">
        <h3>💬 Discord Integration</h3>
        
        <div class="settings-field">
          <label for="setting-discord-token">Bot Token</label>
          <input type="password" id="setting-discord-token" 
                 value="${this.escapeHtml(this.currentSettings.discordToken || '')}"
                 placeholder="Your Discord bot token">
          <div class="settings-help-text">Get from Discord Developer Portal</div>
        </div>
        
        <div class="settings-field">
          <label for="setting-discord-channel">Channel ID</label>
          <input type="text" id="setting-discord-channel" 
                 value="${this.escapeHtml(this.currentSettings.discordChannelId || '')}"
                 placeholder="Channel ID">
          <div class="settings-help-text">Enable Developer Mode in Discord to copy channel IDs</div>
        </div>
      </div>
    `;
  }
  
  createAlarmsSection() {
    const alarmsHtml = this.alarms.length > 0
      ? this.alarms.map(time => `
          <div class="alarm-item">
            <span class="alarm-time">${this.escapeHtml(time)}</span>
            <button class="alarm-delete" data-time="${this.escapeHtml(time)}">Delete</button>
          </div>
        `).join('')
      : '<div class="text-center text-muted">No alarms set</div>';
    
    return `
      <div class="settings-section">
        <h3>⏰ Alarms</h3>
        
        <div class="alarms-list-container" id="alarms-list-display">
          ${alarmsHtml}
        </div>
        
        <div class="alarm-add-form">
          <div class="settings-field" style="flex: 1; margin-bottom: 0;">
            <label for="alarm-time-input">Add New Alarm</label>
            <input type="time" id="alarm-time-input" placeholder="HH:MM">
          </div>
          <button class="btn btn-primary" id="alarm-add-btn" style="margin-top: 28px;">➕ Add</button>
        </div>
        
        <div class="settings-help-text mt-2">
          Alarms will trigger daily at the specified times
        </div>
      </div>
    `;
  }
  
  createTimezoneOptions() {
    const timezones = [
      'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
      'America/Anchorage', 'Pacific/Honolulu', 'America/Phoenix',
      'America/Toronto', 'America/Vancouver', 'America/Mexico_City',
      'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome',
      'Europe/Madrid', 'Europe/Moscow',
      'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Hong_Kong', 'Asia/Singapore',
      'Asia/Dubai', 'Asia/Kolkata',
      'Australia/Sydney', 'Australia/Melbourne', 'Australia/Perth',
      'Pacific/Auckland'
    ];
    
    const currentTz = this.currentSettings.timezone || 'America/Chicago';
    
    return timezones.map(tz => 
      `<option value="${tz}" ${tz === currentTz ? 'selected' : ''}>${tz.replace(/_/g, ' ')}</option>`
    ).join('');
  }
  
  setupSettingsEventListeners() {
    // Close button
    document.getElementById('settings-close').addEventListener('click', () => {
      this.close();
    });
    
    // Cancel button
    document.getElementById('settings-cancel').addEventListener('click', () => {
      this.close();
    });
    
    // Save button
    document.getElementById('settings-save').addEventListener('click', () => {
      this.saveSettings();
    });
    
    // Reset button
    document.getElementById('settings-reset').addEventListener('click', () => {
      this.resetSettings();
    });
    
    // Add alarm button
    document.getElementById('alarm-add-btn').addEventListener('click', () => {
      this.addAlarm();
    });
    
    // Delete alarm buttons
    document.querySelectorAll('.alarm-delete').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const time = e.target.dataset.time;
        this.deleteAlarm(time);
      });
    });
    
    // Allow Enter key to add alarm
    document.getElementById('alarm-time-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.addAlarm();
      }
    });
    
    // Calendar authentication button
    const calendarAuthBtn = document.getElementById('calendar-auth-button');
    if (calendarAuthBtn) {
      calendarAuthBtn.addEventListener('click', () => {
        this.authenticateCalendar();
      });
    }
  }
  
  async addAlarm() {
    const input = document.getElementById('alarm-time-input');
    const time = input.value.trim();
    
    if (!time) {
      alert('Please enter a time');
      return;
    }
    
    try {
      const result = await window.electronAPI.addAlarm(time);
      if (result.success) {
        this.alarms.push(time);
        this.alarms.sort();
        this.updateAlarmsDisplay();
        input.value = '';
      } else {
        alert(result.error || 'Failed to add alarm');
      }
    } catch (error) {
      console.error('Error adding alarm:', error);
      alert('Failed to add alarm');
    }
  }
  
  async deleteAlarm(time) {
    if (!confirm(`Delete alarm at ${time}?`)) {
      return;
    }
    
    try {
      const result = await window.electronAPI.deleteAlarm(time);
      if (result.success) {
        this.alarms = this.alarms.filter(t => t !== time);
        this.updateAlarmsDisplay();
      } else {
        alert(result.error || 'Failed to delete alarm');
      }
    } catch (error) {
      console.error('Error deleting alarm:', error);
      alert('Failed to delete alarm');
    }
  }
  
  updateAlarmsDisplay() {
    const container = document.getElementById('alarms-list-display');
    
    if (this.alarms.length === 0) {
      container.innerHTML = '<div class="text-center text-muted">No alarms set</div>';
      return;
    }
    
    container.innerHTML = this.alarms.map(time => `
      <div class="alarm-item">
        <span class="alarm-time">${this.escapeHtml(time)}</span>
        <button class="alarm-delete" data-time="${this.escapeHtml(time)}">Delete</button>
      </div>
    `).join('');
    
    // Re-attach event listeners
    container.querySelectorAll('.alarm-delete').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const time = e.target.dataset.time;
        this.deleteAlarm(time);
      });
    });
  }
  
  async saveSettings() {
    try {
      const settings = {
        fullscreen: document.getElementById('setting-fullscreen').checked,
        hideCursor: document.getElementById('setting-hide-cursor').checked,
        calendarId: document.getElementById('setting-calendar-id').value.trim(),
        latitude: parseFloat(document.getElementById('setting-latitude').value),
        longitude: parseFloat(document.getElementById('setting-longitude').value),
        timezone: document.getElementById('setting-timezone').value,
        temperatureUnit: document.getElementById('setting-temp-unit').value,
        discordToken: document.getElementById('setting-discord-token').value.trim(),
        discordChannelId: document.getElementById('setting-discord-channel').value.trim(),
        alarms: this.alarms
      };
      
      const result = await window.electronAPI.saveSettings(settings);
      
      if (result.success) {
        alert('Settings saved successfully! Please restart the app for all changes to take effect.');
        this.close();
        
        // Refresh the main UI
        if (window.thymeUI) {
          window.thymeUI.startInitialUpdates();
        }
      } else {
        alert(result.error || 'Failed to save settings');
      }
      
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings');
    }
  }
  
  async resetSettings() {
    if (!confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
      return;
    }
    
    try {
      const result = await window.electronAPI.resetSettings();
      
      if (result.success) {
        alert('Settings reset to defaults. Please restart the app.');
        this.close();
      } else {
        alert(result.error || 'Failed to reset settings');
      }
    } catch (error) {
      console.error('Error resetting settings:', error);
      alert('Failed to reset settings');
    }
  }
  
  async updateCalendarAuthStatus() {
    const statusDiv = document.getElementById('calendar-auth-status');
    const authButton = document.getElementById('calendar-auth-button');
    
    if (!statusDiv || !authButton) return;
    
    try {
      const status = await window.electronAPI.getCalendarAuthStatus();
      
      if (status.isAuthenticated) {
        statusDiv.innerHTML = '<span style="color: #10b981;">✓ Authenticated and ready</span>';
        authButton.textContent = '🔄 Re-authenticate';
        authButton.classList.remove('btn-primary');
        authButton.classList.add('btn-secondary');
      } else if (status.hasToken) {
        statusDiv.innerHTML = '<span style="color: #f59e0b;">⚠ Token found but not connected</span>';
        authButton.textContent = '🔐 Authenticate with Google Calendar';
      } else if (status.hasCredentials) {
        statusDiv.innerHTML = '<span style="color: #9a9a9a;">⏳ Not authenticated yet</span>';
        authButton.textContent = '🔐 Authenticate with Google Calendar';
      } else {
        statusDiv.innerHTML = '<span style="color: #ef4444;">✕ Missing credentials.json</span>';
        authButton.textContent = '❓ Setup Instructions';
        authButton.disabled = true;
      }
    } catch (error) {
      console.error('Error checking calendar auth status:', error);
      statusDiv.innerHTML = '<span style="color: #9a9a9a;">Unable to check status</span>';
    }
  }
  
  async authenticateCalendar() {
    const authButton = document.getElementById('calendar-auth-button');
    const statusDiv = document.getElementById('calendar-auth-status');
    
    if (!authButton || !statusDiv) return;
    
    // Check if credentials exist first
    const status = await window.electronAPI.getCalendarAuthStatus();
    if (!status.hasCredentials) {
      alert(
        'Missing credentials.json!\n\n' +
        'Please follow these steps:\n' +
        '1. Go to https://console.cloud.google.com\n' +
        '2. Create a project and enable Google Calendar API\n' +
        '3. Create OAuth 2.0 credentials (Desktop app)\n' +
        '4. Download as credentials.json\n' +
        '5. Place in config/ directory\n' +
        '6. Restart the app and try again'
      );
      return;
    }
    
    try {
      // Disable button during authentication
      authButton.disabled = true;
      authButton.textContent = '⏳ Opening authentication...';
      statusDiv.innerHTML = '<span style="color: #f59e0b;">🔄 Please sign in with Google...</span>';
      
      // Start OAuth flow
      const result = await window.electronAPI.startCalendarOAuth();
      
      if (result.success) {
        statusDiv.innerHTML = '<span style="color: #10b981;">✓ Authentication successful!</span>';
        authButton.textContent = '✓ Authenticated';
        authButton.classList.remove('btn-primary');
        authButton.classList.add('btn-secondary');
        
        // Show success message
        setTimeout(() => {
          alert('Google Calendar authenticated successfully!\n\nYour calendar events will now appear on the display.');
          // Update status
          this.updateCalendarAuthStatus();
        }, 500);
      } else {
        throw new Error(result.error || 'Authentication failed');
      }
      
    } catch (error) {
      console.error('Calendar authentication error:', error);
      statusDiv.innerHTML = '<span style="color: #ef4444;">✕ Authentication failed</span>';
      authButton.textContent = '🔐 Try Again';
      
      alert(
        'Authentication failed!\n\n' +
        'Error: ' + error.message + '\n\n' +
        'Please check:\n' +
        '1. credentials.json is in config/ directory\n' +
        '2. You granted calendar permissions\n' +
        '3. Your internet connection is working'
      );
    } finally {
      authButton.disabled = false;
    }
  }
  
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize settings UI
window.settingsUI = new SettingsUI();

