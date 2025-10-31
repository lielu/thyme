/**
 * Audio Manager
 * Handles alarm sounds and text-to-speech
 */

const path = require('path');
const say = require('say');
const { spawn } = require('child_process');
const { getPlatformCommand } = require('../utils');

class AudioManager {
  constructor(config) {
    this.config = config;
    this.alarmProcess = null;
    this.ttsProcess = null;
  }
  
  /**
   * Play alarm sound
   * @returns {Promise<boolean>} True if successful
   */
  async playAlarm() {
    try {
      const alarmPath = path.join(__dirname, '..', '..', 'assets', 'sounds', 'alarm.wav');
      
      // Get platform-specific audio player command
      const command = getPlatformCommand({
        macos: 'afplay',
        linux: 'aplay',
        windows: 'powershell',
        default: 'afplay'
      });
      
      // Stop any existing alarm
      this.stopAlarm();
      
      if (process.platform === 'win32') {
        // Windows: use PowerShell
        this.alarmProcess = spawn('powershell', [
          '-c',
          `(New-Object Media.SoundPlayer '${alarmPath}').PlaySync();`
        ]);
      } else {
        // macOS/Linux: use afplay or aplay
        this.alarmProcess = spawn(command, [alarmPath]);
      }
      
      this.alarmProcess.on('error', (error) => {
        console.error('Error playing alarm:', error);
      });
      
      this.alarmProcess.on('close', (code) => {
        console.log(`Alarm sound process exited with code ${code}`);
        this.alarmProcess = null;
      });
      
      console.log('Alarm sound started');
      return true;
      
    } catch (error) {
      console.error('Failed to play alarm:', error);
      return false;
    }
  }
  
  /**
   * Stop alarm sound
   */
  stopAlarm() {
    if (this.alarmProcess) {
      try {
        this.alarmProcess.kill();
        this.alarmProcess = null;
        console.log('Alarm sound stopped');
      } catch (error) {
        console.error('Error stopping alarm:', error);
      }
    }
  }
  
  /**
   * Speak text using text-to-speech
   * @param {string} text - Text to speak
   * @param {Object} options - TTS options
   * @returns {Promise<boolean>} True if successful
   */
  async speak(text, options = {}) {
    return new Promise((resolve) => {
      if (!text || text.trim().length === 0) {
        console.log('No text to speak');
        resolve(false);
        return;
      }
      
      try {
        // Stop any existing TTS
        this.stopSpeech();
        
        // Default options
        const ttsOptions = {
          voice: null, // Use system default
          speed: 1.0,
          ...options
        };
        
        console.log(`Speaking: "${text}"`);
        
        say.speak(text, ttsOptions.voice, ttsOptions.speed, (error) => {
          if (error) {
            console.error('TTS error:', error);
            resolve(false);
          } else {
            console.log('TTS completed');
            resolve(true);
          }
        });
        
      } catch (error) {
        console.error('Failed to speak text:', error);
        resolve(false);
      }
    });
  }
  
  /**
   * Stop text-to-speech
   */
  stopSpeech() {
    try {
      say.stop();
      console.log('TTS stopped');
    } catch (error) {
      console.error('Error stopping TTS:', error);
    }
  }
  
  /**
   * Get available TTS voices
   * @returns {Promise<Array>} List of available voices
   */
  async getVoices() {
    return new Promise((resolve) => {
      say.getInstalledVoices((error, voices) => {
        if (error) {
          console.error('Error getting voices:', error);
          resolve([]);
        } else {
          resolve(voices || []);
        }
      });
    });
  }
  
  /**
   * Test TTS with a sample phrase
   */
  async testTTS() {
    const testPhrases = [
      'Text to speech is working correctly.',
      'Good morning! Time to wake up.',
      'Have a great day!'
    ];
    
    const randomPhrase = testPhrases[Math.floor(Math.random() * testPhrases.length)];
    return await this.speak(randomPhrase);
  }
  
  /**
   * Cleanup resources
   */
  cleanup() {
    console.log('Cleaning up audio manager');
    this.stopAlarm();
    this.stopSpeech();
  }
}

module.exports = AudioManager;

