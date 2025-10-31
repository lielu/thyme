/**
 * Weather Manager
 * Fetches weather data from Open-Meteo API
 */

const axios = require('axios');
const path = require('path');

class WeatherManager {
  constructor(config) {
    this.config = config;
    this.lastWeatherData = null;
    this.weatherCodeMap = {
      0: 'clear.png',
      1: 'clear.png',
      2: 'partly_cloudy.png',
      3: 'cloudy.png',
      45: 'fog.png',
      48: 'fog.png',
      51: 'rain.png',
      53: 'rain.png',
      55: 'rain.png',
      56: 'rain.png',
      57: 'rain.png',
      61: 'rain.png',
      63: 'rain.png',
      65: 'rain.png',
      66: 'rain.png',
      67: 'rain.png',
      71: 'snow.png',
      73: 'snow.png',
      75: 'snow.png',
      77: 'snow.png',
      80: 'rain.png',
      81: 'rain.png',
      82: 'rain.png',
      85: 'snow.png',
      86: 'snow.png',
      95: 'thunderstorm.png',
      96: 'thunderstorm.png',
      99: 'thunderstorm.png'
    };
  }
  
  /**
   * Fetch weather data from Open-Meteo API
   * @returns {Promise<Object>} Weather data object
   */
  async fetchWeatherData() {
    try {
      const latitude = this.config.get('latitude') || 32.7767;
      const longitude = this.config.get('longitude') || -96.7970;
      const tempUnit = this.config.get('temperatureUnit') || 'fahrenheit';
      const timezone = this.config.get('timezone') || 'America/Chicago';
      
      // Build API URL
      const url = 'https://api.open-meteo.com/v1/forecast?' +
        `latitude=${latitude}&` +
        `longitude=${longitude}&` +
        `daily=temperature_2m_max,temperature_2m_min,weathercode&` +
        `current_weather=true&` +
        `temperature_unit=${tempUnit}&` +
        `timezone=${encodeURIComponent(timezone)}`;
      
      console.log('Fetching weather data...');
      const response = await axios.get(url, { timeout: 10000 });
      const data = response.data;
      
      // Extract temperature data
      const maxTemp = Math.round(data.daily.temperature_2m_max[0]);
      const minTemp = Math.round(data.daily.temperature_2m_min[0]);
      const weatherCode = data.daily.weathercode[0];
      
      // Format temperature text
      const tempText = `${maxTemp}° / ${minTemp}°`;
      
      // Get weather icon filename
      const iconFilename = this.weatherCodeMap[weatherCode] || 'clear.png';
      const iconPath = path.join(__dirname, '..', '..', 'assets', 'weather_icons', iconFilename);
      
      this.lastWeatherData = {
        tempText,
        iconFilename,
        iconPath,
        maxTemp,
        minTemp,
        weatherCode,
        currentTemp: data.current_weather ? Math.round(data.current_weather.temperature) : null
      };
      
      console.log(`Weather updated: ${tempText}, icon: ${iconFilename}`);
      return this.lastWeatherData;
      
    } catch (error) {
      console.error('Error fetching weather:', error.message);
      return this.getFallbackWeather();
    }
  }
  
  /**
   * Get fallback weather data when API fails
   * @returns {Object} Fallback weather data
   */
  getFallbackWeather() {
    if (this.lastWeatherData) {
      console.log('Using cached weather data');
      return this.lastWeatherData;
    }
    
    console.log('Using default weather data');
    const iconPath = path.join(__dirname, '..', '..', 'assets', 'weather_icons', 'clear.png');
    
    return {
      tempText: 'Weather unavailable',
      iconFilename: 'clear.png',
      iconPath,
      maxTemp: null,
      minTemp: null,
      weatherCode: 0,
      currentTemp: null
    };
  }
  
  /**
   * Get weather description from code
   * @param {number} code - Weather code
   * @returns {string} Weather description
   */
  getWeatherDescription(code) {
    const descriptions = {
      0: 'Clear sky',
      1: 'Mainly clear',
      2: 'Partly cloudy',
      3: 'Overcast',
      45: 'Foggy',
      48: 'Depositing rime fog',
      51: 'Light drizzle',
      53: 'Moderate drizzle',
      55: 'Dense drizzle',
      56: 'Light freezing drizzle',
      57: 'Dense freezing drizzle',
      61: 'Slight rain',
      63: 'Moderate rain',
      65: 'Heavy rain',
      66: 'Light freezing rain',
      67: 'Heavy freezing rain',
      71: 'Slight snow',
      73: 'Moderate snow',
      75: 'Heavy snow',
      77: 'Snow grains',
      80: 'Slight rain showers',
      81: 'Moderate rain showers',
      82: 'Violent rain showers',
      85: 'Slight snow showers',
      86: 'Heavy snow showers',
      95: 'Thunderstorm',
      96: 'Thunderstorm with slight hail',
      99: 'Thunderstorm with heavy hail'
    };
    
    return descriptions[code] || 'Unknown';
  }
  
  /**
   * Get last cached weather data
   * @returns {Object|null} Last weather data
   */
  getLastWeatherData() {
    return this.lastWeatherData;
  }
  
  /**
   * Cleanup resources
   */
  cleanup() {
    console.log('Cleaning up weather manager');
    // Nothing to clean up
  }
}

module.exports = WeatherManager;

