/**
 * Background Manager
 * Handles background image rotation and Bing wallpaper downloads
 */

const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');
const { getImageFiles, ensureDirectoryExists } = require('../utils');

class BackgroundManager {
  constructor(config) {
    this.config = config;
    this.backgroundsDir = path.join(__dirname, '..', '..', 'assets', 'backgrounds');
    this.currentBackground = null;
    this.backgroundImages = [];
    this.initialized = false;
    this.init();
  }
  
  async init() {
    try {
      await ensureDirectoryExists(this.backgroundsDir);
      await this.loadBackgroundImages();
      await this.downloadBingWallpaper();
      this.initialized = true;
      console.log('Background manager initialized');
    } catch (error) {
      console.error('Error initializing background manager:', error);
    }
  }
  
  /**
   * Load list of available background images
   */
  async loadBackgroundImages() {
    try {
      this.backgroundImages = await getImageFiles(this.backgroundsDir);
      console.log(`Found ${this.backgroundImages.length} background images`);
      
      if (this.backgroundImages.length === 0) {
        console.warn('No background images found');
      }
    } catch (error) {
      console.error('Error loading background images:', error);
      this.backgroundImages = [];
    }
  }
  
  /**
   * Get a random background image
   * @returns {Promise<string>} Path to background image
   */
  async getRandomBackground() {
    // Reload the list of images each time to catch new downloads
    await this.loadBackgroundImages();
    
    if (this.backgroundImages.length === 0) {
      return null;
    }
    
    // Get a random image different from the current one
    let newBackground;
    if (this.backgroundImages.length === 1) {
      newBackground = this.backgroundImages[0];
    } else {
      do {
        const randomIndex = Math.floor(Math.random() * this.backgroundImages.length);
        newBackground = this.backgroundImages[randomIndex];
      } while (newBackground === this.currentBackground && this.backgroundImages.length > 1);
    }
    
    this.currentBackground = newBackground;
    console.log(`Selected background: ${path.basename(newBackground)}`);
    
    return newBackground;
  }
  
  /**
   * Download Bing's daily wallpaper
   * @returns {Promise<boolean>} True if successful
   */
  async downloadBingWallpaper() {
    try {
      console.log('Downloading Bing wallpaper...');
      
      // Fetch Bing's image of the day metadata
      const metaUrl = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US';
      const metaResponse = await axios.get(metaUrl, { timeout: 10000 });
      
      if (!metaResponse.data || !metaResponse.data.images || metaResponse.data.images.length === 0) {
        console.error('Invalid Bing API response');
        return false;
      }
      
      const imageData = metaResponse.data.images[0];
      const imageUrl = `https://www.bing.com${imageData.url}`;
      
      // Extract filename from URL
      const urlBase = imageData.urlbase || imageData.url;
      const filename = urlBase.split('/').pop().split('_')[0] + '.jpg';
      const filepath = path.join(this.backgroundsDir, filename);
      
      // Check if already downloaded
      try {
        await fs.access(filepath);
        console.log('Bing wallpaper already exists');
        return true;
      } catch {
        // File doesn't exist, proceed with download
      }
      
      // Download the image
      const imageResponse = await axios.get(imageUrl, {
        responseType: 'arraybuffer',
        timeout: 30000
      });
      
      await fs.writeFile(filepath, imageResponse.data);
      console.log(`Successfully downloaded Bing wallpaper: ${filename}`);
      
      // Clean up old wallpapers (keep only last 7)
      await this.cleanupOldWallpapers(7);
      
      // Reload background images
      await this.loadBackgroundImages();
      
      return true;
      
    } catch (error) {
      console.error('Error downloading Bing wallpaper:', error.message);
      return false;
    }
  }
  
  /**
   * Clean up old wallpapers, keeping only the most recent ones
   * @param {number} keepCount - Number of wallpapers to keep
   */
  async cleanupOldWallpapers(keepCount = 7) {
    try {
      const files = await getImageFiles(this.backgroundsDir);
      
      if (files.length <= keepCount) {
        return; // No cleanup needed
      }
      
      // Get file stats and sort by modification time
      const filesWithStats = await Promise.all(
        files.map(async (file) => {
          const stats = await fs.stat(file);
          return { file, mtime: stats.mtime };
        })
      );
      
      // Sort by modification time (newest first)
      filesWithStats.sort((a, b) => b.mtime - a.mtime);
      
      // Delete old files
      const filesToDelete = filesWithStats.slice(keepCount);
      for (const { file } of filesToDelete) {
        try {
          await fs.unlink(file);
          console.log(`Deleted old wallpaper: ${path.basename(file)}`);
        } catch (error) {
          console.error(`Failed to delete ${file}:`, error);
        }
      }
      
    } catch (error) {
      console.error('Error cleaning up old wallpapers:', error);
    }
  }
  
  /**
   * Get current background
   * @returns {string|null} Path to current background
   */
  getCurrentBackground() {
    return this.currentBackground;
  }
  
  /**
   * Cleanup resources
   */
  cleanup() {
    console.log('Cleaning up background manager');
    // Nothing to clean up for now
  }
}

module.exports = BackgroundManager;

