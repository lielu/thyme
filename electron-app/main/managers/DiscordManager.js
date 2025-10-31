/**
 * Discord Manager
 * Handles Discord bot integration to display channel messages
 */

const { Client, GatewayIntentBits } = require('discord.js');

class DiscordManager {
  constructor(config) {
    this.config = config;
    this.client = null;
    this.isReady = false;
    this.recentMessages = [];
    this.maxMessages = 5;
    this.init();
  }
  
  async init() {
    try {
      const token = this.config.get('discordToken');
      const channelId = this.config.get('discordChannelId');
      
      if (!token || !channelId || token === '' || channelId === '') {
        console.log('Discord not configured - skipping initialization');
        return;
      }
      
      // Create Discord client
      this.client = new Client({
        intents: [
          GatewayIntentBits.Guilds,
          GatewayIntentBits.GuildMessages,
          GatewayIntentBits.MessageContent
        ]
      });
      
      // Set up event handlers
      this.client.once('ready', () => {
        console.log(`Discord bot logged in as ${this.client.user.tag}`);
        this.isReady = true;
        this.fetchRecentMessages();
      });
      
      this.client.on('messageCreate', (message) => {
        this.handleNewMessage(message);
      });
      
      this.client.on('error', (error) => {
        console.error('Discord client error:', error);
      });
      
      // Login to Discord
      await this.client.login(token);
      console.log('Discord manager initialized');
      
    } catch (error) {
      console.error('Error initializing Discord manager:', error.message);
      this.isReady = false;
    }
  }
  
  /**
   * Fetch recent messages from configured channel
   */
  async fetchRecentMessages() {
    if (!this.client || !this.isReady) {
      return;
    }
    
    try {
      const channelId = this.config.get('discordChannelId');
      const channel = await this.client.channels.fetch(channelId);
      
      if (!channel || !channel.isTextBased()) {
        console.error('Invalid Discord channel');
        return;
      }
      
      // Fetch recent messages
      const messages = await channel.messages.fetch({ limit: this.maxMessages });
      
      // Store messages (newest first)
      this.recentMessages = Array.from(messages.values())
        .sort((a, b) => b.createdTimestamp - a.createdTimestamp)
        .slice(0, this.maxMessages);
      
      console.log(`Fetched ${this.recentMessages.length} Discord messages`);
      
    } catch (error) {
      console.error('Error fetching Discord messages:', error);
    }
  }
  
  /**
   * Handle new message from Discord
   * @param {Message} message - Discord message object
   */
  handleNewMessage(message) {
    const channelId = this.config.get('discordChannelId');
    
    // Only track messages from configured channel
    if (message.channel.id !== channelId) {
      return;
    }
    
    // Add to recent messages
    this.recentMessages.unshift(message);
    
    // Keep only the most recent messages
    if (this.recentMessages.length > this.maxMessages) {
      this.recentMessages = this.recentMessages.slice(0, this.maxMessages);
    }
    
    console.log(`New Discord message from ${message.author.username}`);
  }
  
  /**
   * Get recent messages formatted for display
   * @returns {Array<string>} Array of formatted message strings
   */
  getRecentMessages() {
    if (!this.isReady || this.recentMessages.length === 0) {
      return ['No recent messages'];
    }
    
    return this.recentMessages.map(message => {
      const timestamp = message.createdAt.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
      
      const author = message.author.username;
      let content = message.content;
      
      // Truncate long messages
      if (content.length > 100) {
        content = content.substring(0, 97) + '...';
      }
      
      // Handle empty content (e.g., embeds or attachments only)
      if (!content) {
        if (message.embeds.length > 0) {
          content = '[Embed]';
        } else if (message.attachments.size > 0) {
          content = '[Attachment]';
        } else {
          content = '[No content]';
        }
      }
      
      return `${timestamp} ${author}: ${content}`;
    });
  }
  
  /**
   * Get messages as single display text
   * @returns {string} Formatted text for display
   */
  getMessagesDisplayText() {
    if (!this.isReady) {
      return '💬 Discord:\n(not configured)';
    }
    
    const messages = this.getRecentMessages();
    return `💬 Discord:\n${messages.join('\n')}`;
  }
  
  /**
   * Check if Discord is ready
   * @returns {boolean} True if ready
   */
  isConnected() {
    return this.isReady;
  }
  
  /**
   * Cleanup resources
   */
  async cleanup() {
    console.log('Cleaning up Discord manager');
    
    if (this.client) {
      try {
        await this.client.destroy();
        console.log('Discord client disconnected');
      } catch (error) {
        console.error('Error disconnecting Discord client:', error);
      }
    }
    
    this.client = null;
    this.isReady = false;
    this.recentMessages = [];
  }
}

module.exports = DiscordManager;

