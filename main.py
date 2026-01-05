import threading
import os
import sys
import time
from dotenv import load_dotenv
import server

# Load environment variables from .env
load_dotenv()

def check_environment():
    """Verify that the DISCORD_TOKEN is set."""
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        print("❌ Warning: DISCORD_TOKEN is not set in environment variables.")
        print("Please set DISCORD_TOKEN in the Secrets tab or .env file.")
        return False
    return True

def run_flask():
    """Start the Flask API server."""
    try:
        print("🌐 Starting Flask server on port 5000...")
        server.run()
    except Exception as e:
        print(f"❌ Flask server error: {e}")

def run_discord():
    """Start the Discord bot with simple retry logic for rate limits."""
    retry_count = 0
    max_retries = 3
    retry_delay = 300 # 5 minutes

    while retry_count < max_retries:
        try:
            import bot
            # Ensure the bot.py has a run() function or logic to start
            if hasattr(bot, 'run'):
                print(f"🤖 Starting Discord bot (Attempt {retry_count + 1})...")
                bot.run()
                break # Exit loop if bot runs and finishes normally
            else:
                print("❌ Error: bot.py does not have a run() function.")
                break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                retry_count += 1
                print(f"⚠️ Discord Rate Limit hit (429). Retrying in {retry_delay}s... ({retry_count}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"❌ Discord bot error: {e}")
                break

if __name__ == "__main__":
    print("🚀 Initializing Roblox Moderation System...")
    print("=" * 50)

    has_token = check_environment()

    # Start Discord bot in a background thread if token is available
    if has_token:
        discord_thread = threading.Thread(target=run_discord, daemon=True)
        discord_thread.start()

    # Run Flask in the main thread (keeps the app running)
    try:
        run_flask()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
