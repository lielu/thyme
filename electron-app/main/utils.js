/**
 * Utility Functions
 * Common helper functions used across the application
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Parse time string in HH:MM format
 * @param {string} timeStr - Time string
 * @returns {Object|null} Object with hours and minutes, or null if invalid
 */
function parseTimeString(timeStr) {
  if (!timeStr || typeof timeStr !== 'string') return null;
  
  const parts = timeStr.trim().split(':');
  if (parts.length !== 2) return null;
  
  const hours = parseInt(parts[0], 10);
  const minutes = parseInt(parts[1], 10);
  
  if (isNaN(hours) || isNaN(minutes)) return null;
  if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) return null;
  
  return { hours, minutes };
}

/**
 * Convert time string to minutes since midnight
 * @param {string} timeStr - Time string in HH:MM format
 * @returns {number|null} Minutes since midnight or null if invalid
 */
function timeToMinutes(timeStr) {
  const parsed = parseTimeString(timeStr);
  if (!parsed) return null;
  return parsed.hours * 60 + parsed.minutes;
}

/**
 * Check if current time is between two time strings
 * @param {string} startTime - Start time in HH:MM format
 * @param {string} endTime - End time in HH:MM format
 * @returns {boolean} True if current time is in range
 */
function isTimeBetween(startTime, endTime) {
  if (!startTime || !endTime) return false;
  
  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();
  
  const startMinutes = timeToMinutes(startTime);
  const endMinutes = timeToMinutes(endTime);
  
  if (startMinutes === null || endMinutes === null) return false;
  
  // Handle case where time range crosses midnight
  if (startMinutes > endMinutes) {
    return currentMinutes >= startMinutes || currentMinutes < endMinutes;
  }
  
  return currentMinutes >= startMinutes && currentMinutes < endMinutes;
}

/**
 * Get list of image files from directory
 * @param {string} directory - Directory path
 * @param {Array<string>} extensions - Array of file extensions
 * @returns {Promise<Array<string>>} Array of file paths
 */
async function getImageFiles(directory, extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']) {
  try {
    const files = await fs.readdir(directory);
    return files
      .filter(file => {
        const ext = path.extname(file).toLowerCase();
        return extensions.includes(ext);
      })
      .map(file => path.join(directory, file));
  } catch (error) {
    console.error(`Error reading directory ${directory}:`, error);
    return [];
  }
}

/**
 * Ensure directory exists, create if necessary
 * @param {string} directory - Directory path
 * @returns {Promise<boolean>} True if directory exists or was created
 */
async function ensureDirectoryExists(directory) {
  try {
    await fs.mkdir(directory, { recursive: true });
    return true;
  } catch (error) {
    console.error(`Failed to create directory ${directory}:`, error);
    return false;
  }
}

/**
 * Get platform-specific command
 * @param {Object} commands - Object with platform-specific commands
 * @returns {string} Command for current platform
 */
function getPlatformCommand(commands) {
  const platform = process.platform;
  
  if (platform === 'darwin') return commands.macos || commands.default || '';
  if (platform === 'win32') return commands.windows || commands.default || '';
  return commands.linux || commands.default || '';
}

/**
 * Format date for display
 * @param {Date} date - Date object
 * @returns {string} Formatted date string
 */
function formatDate(date = new Date()) {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

/**
 * Format time for display
 * @param {Date} date - Date object
 * @param {boolean} use24Hour - Use 24-hour format
 * @returns {string} Formatted time string
 */
function formatTime(date = new Date(), use24Hour = true) {
  return date.toLocaleTimeString('en-US', {
    hour12: !use24Hour,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

/**
 * Sleep for specified milliseconds
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise} Promise that resolves after delay
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Validate alarm time format
 * @param {string} time - Time string
 * @returns {boolean} True if valid
 */
function isValidAlarmTime(time) {
  return parseTimeString(time) !== null;
}

module.exports = {
  parseTimeString,
  timeToMinutes,
  isTimeBetween,
  getImageFiles,
  ensureDirectoryExists,
  getPlatformCommand,
  formatDate,
  formatTime,
  sleep,
  isValidAlarmTime
};

