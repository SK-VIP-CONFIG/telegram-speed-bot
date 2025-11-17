import logging
import struct
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot Token (YAHI CHANGE KARNA HAI)
TOKEN = "7432795021:AAGMOoMf9GtHwmk8DHTS03ydH1MEAKeqx1k"

# Value Mappings
value_mappings = {
    "KNOCK SPEED": -0.64,
    "STAND BACK SPEED": -143.9,
    "STAND RIGHT SPEED": -119.9,
    "CROUCH SPEED": -135.25,
    "BACK CROUCH SPEED": -103.28,
    "RIGHT CROUCH SPEED": -86.05,
    "PRONE SPEED": -359.5,
    "PRONE BACK/RIGHT": -20.0,
    "SPRINT SPEED": 160.5
}

# Float to hex bytes
def float_to_hex_bytes(value):
    return struct.pack('<f', value)

# Modify float value in file
def modify_file(file_path, search_value, new_value):
    with open(file_path, 'rb') as f:
        data = f.read()
    search = float_to_hex_bytes(search_value)
    replace = float_to_hex_bytes(new_value)

    if search in data:
        data = data.replace(search, replace, 1)
        with open(file_path, 'wb') as f:
            f.write(data)
        return True
    return False

# /start command
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "🤖 **File Modifier Bot** is ready!\n\n"
        "📁 **How to use:**\n"
        "1. Send me a .uexp or .dat file\n"
        "2. I'll send you a format\n" 
        "3. Edit the values and send back\n"
        "4. Receive modified file\n\n"
        "🚀 Send a file to get started!"
    )

# File upload handler
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document
    if not file.file_name.endswith(('.uexp', '.dat')):
        update.message.reply_text("❌ Only .uexp or .dat files are supported!")
        return

    file_path = f"./{file.file_name}"
    file.get_file().download(file_path)
    context.user_data['file_path'] = file_path

    update.message.reply_text(
        "✅ File Received! Now send new values in this format:\n\n"
        "📑 Copy the format below, edit values and send:\n"
        "```\n"
        "KNOCK SPEED: -0.64\n"
        "STAND BACK SPEED: -143.9\n" 
        "STAND RIGHT SPEED: -119.9\n"
        "CROUCH SPEED: -135.25\n"
        "BACK CROUCH SPEED: -103.28\n"
        "RIGHT CROUCH SPEED: -86.05\n"
        "PRONE SPEED: -359.5\n"
        "PRONE BACK/RIGHT: -20.0\n"
        "SPRINT SPEED: 160.5\n"
        "```",
        parse_mode="Markdown"
    )

# Text message handler
def handle_text(update: Update, context: CallbackContext):
    if 'file_path' not in context.user_data:
        update.message.reply_text("❗ First send a .uexp or .dat file.")
        return

    try:
        text = update.message.text.strip()
        lines = text.split('\n')
        file_path = context.user_data['file_path']

        results = []
        for line in lines:
            if ':' not in line:
                continue
            name, val = line.split(':', 1)
            name = name.strip().upper()
            try:
                new_val = float(val.strip())
            except ValueError:
                results.append(f"❌ {name}: Invalid number.")
                continue

            if name not in value_mappings:
                results.append(f"❌ {name}: Not a valid key.")
                continue

            old_val = value_mappings[name]
            success = modify_file(file_path, old_val, new_val)

            if success:
                results.append(f"✅ {name}: Modified.")
            else:
                results.append(f"⚠️ {name}: Value not found.")

        update.message.reply_text('\n'.join(results))
        update.message.reply_document(open(file_path, 'rb'))
        
        # Clean up file
        os.remove(file_path)
        del context.user_data['file_path']
        
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}")

# Error handler
def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    logger.info("🚀 Starting Telegram Bot on Railway...")
    
    try:
        updater = Updater(TOKEN, use_context=True)
        dp = updater.dispatcher

        # Add handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.document, handle_file))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
        dp.add_error_handler(error_handler)

        # Start bot
        updater.start_polling(drop_pending_updates=True)
        logger.info("✅ Bot started successfully on Railway!")
        
        # Run until stopped
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        # Auto-restart after 10 seconds
        time.sleep(10)
        main()

if __name__ == '__main__':
    main()
