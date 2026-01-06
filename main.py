import threading
import os
import sys
import time
from dotenv import load_dotenv

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
        import server
        print("🌐 Starting Flask server on port 5000...")
        server.run()
    except Exception as e:
        print(f"❌ Flask server error: {e}")

def run_discord():
    """Start the Discord bot."""
    try:
        import bot
        # Ensure the bot.py has a run() function or logic to start
        if hasattr(bot, 'run'):
            print("🤖 Starting Discord bot...")
            bot.run()
        else:
            print("❌ Error: bot.py does not have a run() function.")
    except Exception as e:
        print(f"❌ Discord bot error: {e}")

if __name__ == "__main__":
    print("🚀 Initializing Roblox Moderation System...")
    print("=" * 50)

    if not check_environment():
        # We continue even if token is missing so the user can see the error in logs
        pass

    # Start Flask in a background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Give Flask a moment to start up
    time.sleep(2)

    # Start the Discord bot in the main thread
    try:
        run_discord()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)