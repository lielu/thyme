#!/usr/bin/env python3
"""
Test Discord Manager

Simple test script to verify Discord integration works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from discord_manager import DiscordManager
from config import user_config

def test_environment_variables():
    """Test if Discord environment variables are set."""
    print("🔍 Checking environment variables...")
    
    token = user_config.discord_token
    channel_id = user_config.discord_channel_id
    
    if not token:
        print("❌ KIOSK_DISCORD_TOKEN not set")
        print("   Set it with: export KIOSK_DISCORD_TOKEN='your_bot_token'")
        return False
    else:
        print(f"✅ KIOSK_DISCORD_TOKEN set (ending in: ...{token[-6:]})")
    
    if not channel_id:
        print("❌ KIOSK_DISCORD_CHANNEL_ID not set")
        print("   Set it with: export KIOSK_DISCORD_CHANNEL_ID='your_channel_id'")
        return False
    else:
        print(f"✅ KIOSK_DISCORD_CHANNEL_ID set: {channel_id}")
    
    return True

def test_discord_manager():
    """Test Discord manager creation and connection."""
    print("\n🤖 Testing Discord manager...")
    
    try:
        dm = DiscordManager()
        print("✅ DiscordManager created successfully")
        
        # Wait a bit for connection
        print("⏳ Waiting for Discord bot to connect...")
        max_wait = 30  # seconds
        wait_time = 0
        
        while not dm.is_authenticated() and wait_time < max_wait:
            time.sleep(1)
            wait_time += 1
            if wait_time % 5 == 0:
                print(f"   Still waiting... ({wait_time}/{max_wait}s)")
        
        if dm.is_authenticated():
            print("✅ Discord bot connected successfully!")
            return dm
        else:
            print(f"❌ Discord bot failed to connect within {max_wait} seconds")
            return None
            
    except Exception as e:
        print(f"❌ Error creating Discord manager: {e}")
        return None

def test_message_fetching(dm):
    """Test fetching messages from Discord."""
    print("\n📨 Testing message fetching...")
    
    try:
        # Get display text
        display_text = dm.get_messages_display_text()
        print("✅ Message fetching successful")
        print("📱 Current display text:")
        print("=" * 40)
        print(display_text)
        print("=" * 40)
        
        if "no recent messages" in display_text.lower():
            print("💡 Tip: Send a test message in your Discord channel to see it appear here!")
            
    except Exception as e:
        print(f"❌ Error fetching messages: {e}")

def main():
    """Main test function."""
    print("🚀 Discord Integration Test")
    print("=" * 50)
    
    # Test 1: Environment variables
    if not test_environment_variables():
        print("\n❌ Environment variable test failed")
        print("   Please set your Discord token and channel ID")
        return 1
    
    # Test 2: Discord manager
    dm = test_discord_manager()
    if not dm:
        print("\n❌ Discord manager test failed")
        print("   Check the troubleshooting guide in discord_setup_guide.md")
        return 1
    
    # Test 3: Message fetching
    test_message_fetching(dm)
    
    print("\n🎉 All tests completed!")
    print("   Your Discord integration is ready to use with the kiosk!")
    
    # Cleanup
    if dm:
        dm.cleanup()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 