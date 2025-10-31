/**
 * Calendar Manager
 * Handles Google Calendar API integration
 */

const fs = require('fs').promises;
const path = require('path');
const { google } = require('googleapis');

class CalendarManager {
  constructor(config) {
    this.config = config;
    this.calendar = null;
    this.auth = null;
    this.credentialsPath = path.join(__dirname, '..', '..', 'config', 'credentials.json');
    this.tokenPath = path.join(__dirname, '..', '..', 'config', 'token.json');
    this.initialized = false;
    this.lastEvents = [];
    this.init();
  }
  
  async init() {
    try {
      await this.authenticate();
      this.initialized = true;
      console.log('Calendar manager initialized');
    } catch (error) {
      console.error('Error initializing calendar manager:', error.message);
      this.initialized = false;
    }
  }
  
  /**
   * Authenticate with Google Calendar API
   */
  async authenticate() {
    try {
      // Check if credentials file exists
      try {
        await fs.access(this.credentialsPath);
      } catch {
        console.warn('Google Calendar credentials not found at:', this.credentialsPath);
        return;
      }
      
      // Load credentials
      const credentials = JSON.parse(await fs.readFile(this.credentialsPath, 'utf8'));
      const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;
      
      // Create OAuth2 client
      const oAuth2Client = new google.auth.OAuth2(
        client_id,
        client_secret,
        redirect_uris[0]
      );
      
      // Check if we have a saved token
      try {
        const token = JSON.parse(await fs.readFile(this.tokenPath, 'utf8'));
        oAuth2Client.setCredentials(token);
        
        // Check if token is expired
        if (oAuth2Client.isTokenExpiring()) {
          console.log('Token expiring, refreshing...');
          const { credentials } = await oAuth2Client.refreshAccessToken();
          oAuth2Client.setCredentials(credentials);
          await fs.writeFile(this.tokenPath, JSON.stringify(credentials));
          console.log('Token refreshed and saved');
        }
        
      } catch (error) {
        console.warn('No saved token found. Calendar integration requires manual OAuth setup.');
        console.warn('Please run the Python version once to complete OAuth authentication.');
        return;
      }
      
      this.auth = oAuth2Client;
      this.calendar = google.calendar({ version: 'v3', auth: oAuth2Client });
      console.log('Google Calendar authenticated successfully');
      
    } catch (error) {
      console.error('Error authenticating with Google Calendar:', error.message);
      throw error;
    }
  }
  
  /**
   * Fetch today's calendar events
   * @param {number} maxEvents - Maximum number of events to fetch
   * @returns {Promise<Array<string>>} Array of formatted event strings
   */
  async fetchTodaysEvents(maxEvents = 3) {
    if (!this.calendar) {
      return ['Calendar not configured'];
    }
    
    try {
      const calendarId = this.config.get('calendarId') || 'primary';
      
      // Get today's date range
      const now = new Date();
      const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
      
      // Fetch events
      const response = await this.calendar.events.list({
        calendarId: calendarId,
        timeMin: startOfDay.toISOString(),
        timeMax: endOfDay.toISOString(),
        maxResults: maxEvents,
        singleEvents: true,
        orderBy: 'startTime',
      });
      
      const events = response.data.items || [];
      
      if (events.length === 0) {
        this.lastEvents = ['No events today'];
        return this.lastEvents;
      }
      
      // Format events
      const formattedEvents = events.map(event => {
        const start = event.start.dateTime || event.start.date;
        const startDate = new Date(start);
        const timeStr = event.start.dateTime 
          ? startDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
          : 'All day';
        
        return `${timeStr} - ${event.summary}`;
      });
      
      this.lastEvents = formattedEvents;
      console.log(`Fetched ${formattedEvents.length} calendar events`);
      return formattedEvents;
      
    } catch (error) {
      console.error('Error fetching calendar events:', error.message);
      return this.lastEvents.length > 0 ? this.lastEvents : ['Error loading events'];
    }
  }
  
  /**
   * Get upcoming events for speech announcement
   * @returns {Promise<string>} Text for TTS
   */
  async getUpcomingEventsForSpeech() {
    try {
      const events = await this.fetchTodaysEvents(5);
      
      if (events.length === 0 || events[0] === 'No events today') {
        return 'You have no events scheduled for today.';
      }
      
      if (events[0] === 'Error loading events' || events[0] === 'Calendar not configured') {
        return 'Unable to load calendar events.';
      }
      
      let speech = 'Your events for today are: ';
      speech += events.join('. ');
      
      return speech;
      
    } catch (error) {
      console.error('Error getting events for speech:', error);
      return 'Unable to load calendar events.';
    }
  }
  
  /**
   * Get events in a specific date range
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   * @param {number} maxEvents - Maximum number of events
   * @returns {Promise<Array>} Array of event objects
   */
  async getEventsInRange(startDate, endDate, maxEvents = 10) {
    if (!this.calendar) {
      return [];
    }
    
    try {
      const calendarId = this.config.get('calendarId') || 'primary';
      
      const response = await this.calendar.events.list({
        calendarId: calendarId,
        timeMin: startDate.toISOString(),
        timeMax: endDate.toISOString(),
        maxResults: maxEvents,
        singleEvents: true,
        orderBy: 'startTime',
      });
      
      return response.data.items || [];
      
    } catch (error) {
      console.error('Error fetching events in range:', error);
      return [];
    }
  }
  
  /**
   * Check if calendar is available
   * @returns {boolean} True if calendar is available
   */
  isAvailable() {
    return this.calendar !== null;
  }
  
  /**
   * Cleanup resources
   */
  cleanup() {
    console.log('Cleaning up calendar manager');
    this.calendar = null;
    this.auth = null;
  }
}

module.exports = CalendarManager;

