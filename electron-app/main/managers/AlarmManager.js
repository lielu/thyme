/**
 * Alarm Manager
 * Handles alarm scheduling and triggering
 */

const cron = require('node-cron');
const EventEmitter = require('events');
const { isValidAlarmTime, parseTimeString } = require('../utils');

class AlarmManager extends EventEmitter {
  constructor(config) {
    super();
    this.config = config;
    this.alarms = [];
    this.cronJobs = new Map();
    this.firedAlarmsToday = new Set();
    this.loadAlarms();
    this.startMidnightReset();
  }
  
  loadAlarms() {
    this.alarms = this.config.get('alarms') || [];
    console.log(`Loaded ${this.alarms.length} alarms`);
    this.scheduleAlarms();
  }
  
  scheduleAlarms() {
    // Clear existing cron jobs
    this.cronJobs.forEach(job => job.stop());
    this.cronJobs.clear();
    
    // Schedule each alarm
    this.alarms.forEach(alarmTime => {
      if (!isValidAlarmTime(alarmTime)) {
        console.warn(`Invalid alarm time: ${alarmTime}`);
        return;
      }
      
      const parsed = parseTimeString(alarmTime);
      const { hours, minutes } = parsed;
      
      // Cron expression: minute hour * * *
      const cronExpression = `${minutes} ${hours} * * *`;
      
      try {
        const job = cron.schedule(cronExpression, () => {
          this.triggerAlarm(alarmTime);
        });
        
        this.cronJobs.set(alarmTime, job);
        console.log(`Scheduled alarm for ${alarmTime}`);
      } catch (error) {
        console.error(`Failed to schedule alarm ${alarmTime}:`, error);
      }
    });
  }
  
  triggerAlarm(alarmTime) {
    const today = new Date().toDateString();
    const alarmId = `${today}-${alarmTime}`;
    
    // Check if already fired today
    if (this.firedAlarmsToday.has(alarmId)) {
      console.log(`Alarm ${alarmTime} already fired today`);
      return;
    }
    
    console.log(`Triggering alarm: ${alarmTime}`);
    this.firedAlarmsToday.add(alarmId);
    this.emit('alarm', alarmTime);
  }
  
  startMidnightReset() {
    // Reset fired alarms at midnight
    cron.schedule('0 0 * * *', () => {
      console.log('Resetting fired alarms for new day');
      this.firedAlarmsToday.clear();
    });
  }
  
  getAlarmSummary() {
    if (this.alarms.length === 0) {
      return 'No alarms set';
    }
    
    const sortedAlarms = [...this.alarms].sort();
    return `⏰ Alarms:\n${sortedAlarms.join('\n')}`;
  }
  
  getAllAlarmTimes() {
    return [...this.alarms].sort();
  }
  
  async addAlarm(time) {
    if (!isValidAlarmTime(time)) {
      throw new Error('Invalid alarm time format. Use HH:MM');
    }
    
    if (this.alarms.includes(time)) {
      throw new Error('Alarm already exists');
    }
    
    this.alarms.push(time);
    this.alarms.sort();
    
    // Update config
    this.config.set('alarms', this.alarms);
    await this.config.save();
    
    // Reschedule
    this.scheduleAlarms();
    
    console.log(`Added alarm: ${time}`);
    return true;
  }
  
  async deleteAlarm(time) {
    const index = this.alarms.indexOf(time);
    if (index === -1) {
      throw new Error('Alarm not found');
    }
    
    this.alarms.splice(index, 1);
    
    // Stop the cron job for this alarm
    const job = this.cronJobs.get(time);
    if (job) {
      job.stop();
      this.cronJobs.delete(time);
    }
    
    // Update config
    this.config.set('alarms', this.alarms);
    await this.config.save();
    
    console.log(`Deleted alarm: ${time}`);
    return true;
  }
  
  async setAlarms(alarms) {
    // Validate all alarms
    for (const time of alarms) {
      if (!isValidAlarmTime(time)) {
        throw new Error(`Invalid alarm time: ${time}`);
      }
    }
    
    this.alarms = [...alarms].sort();
    
    // Update config
    this.config.set('alarms', this.alarms);
    await this.config.save();
    
    // Reschedule all alarms
    this.scheduleAlarms();
    
    console.log(`Updated alarms: ${this.alarms.join(', ')}`);
    return true;
  }
  
  cleanup() {
    console.log('Cleaning up alarm manager');
    this.cronJobs.forEach(job => job.stop());
    this.cronJobs.clear();
  }
}

module.exports = AlarmManager;

