#!/usr/bin/env python3
"""
Test Config Reading

Test script to verify that configuration is being read correctly 
from alarm_config.txt instead of environment variables.
"""

from config import user_config
import os

def test_config_loading():
    """Test that configuration is loaded correctly."""
    print("=== Testing Configuration Loading ===\n")
    
    print("📁 Current alarm_config.txt content:")
    try:
        with open('alarm_config.txt', 'r') as f:
            content = f.read()
            print(content)
    except FileNotFoundError:
        print("❌ alarm_config.txt not found")
        return
    
    print("\n🔧 Loaded Configuration:")
    print(f"Calendar ID: {user_config.calendar_id}")
    print(f"Latitude: {user_config.latitude}")
    print(f"Longitude: {user_config.longitude}")
    print(f"Timezone: {user_config.timezone}")
    print(f"Temperature Unit: {user_config.temperature_unit}")
    
    # Show Discord settings (mask token for security)
    discord_token = user_config.discord_token
    if discord_token and discord_token != '<discord_token>':
        print(f"Discord Token: ...{discord_token[-8:]} (last 8 chars)")
        print(f"Discord Channel ID: {user_config.discord_channel_id}")
    else:
        print("Discord Token: Not configured")
        print("Discord Channel ID: Not configured")
    
    print("\n🌐 Environment Variables (for comparison):")
    env_vars = [
        'KIOSK_CALENDAR_ID',
        'KIOSK_LATITUDE', 
        'KIOSK_LONGITUDE',
        'KIOSK_TIMEZONE',
        'KIOSK_TEMP_UNIT',
        'KIOSK_DISCORD_TOKEN',
        'KIOSK_DISCORD_CHANNEL_ID'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        if 'TOKEN' in var and value != 'Not set':
            value = f"...{value[-8:]}"
        print(f"{var}: {value}")
    
    print("\n✅ Configuration test complete!")

if __name__ == "__main__":
    test_config_loading() 