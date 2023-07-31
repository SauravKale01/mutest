import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your Telegram Bot token
TOKEN = '6206599982:AAFhXRwC0SnPCBK4WDwzdz7TbTsM2hccgZc'

# Jikan API endpoint for character search
JIKAN_API_URL = 'https://api.jikan.moe/v3/character/search/'

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello! I'm your Anime Character Lookup bot. Just send me the name of the anime character you want to know more about!")

def character_lookup(update, context):
    character_name = update.message.text.strip()

    if not character_name:
        update.message.reply_text("Please provide the name of the anime character you want to lookup.")
        return

    response = requests.get(f'{JIKAN_API_URL}{character_name}')
    data = response.json()

    if 'result' not in data or not data['result']:
        update.message.reply_text("Sorry, I couldn't find any information about that character.")
        return

    character = data['result'][0]
    name = character['name']
    url = character['url']
    image_url = character['image_url']
    description = character['about']

    message = f"**Character Name:** {name}\n\n**Description:** {description}\n\n[More Info]({url})"
    
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url, caption=message, parse_mode='Markdown')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, character_lookup))

    # Replace '<your_chat_id_here>' with your actual chat ID
    chat_id = -1001905486162
    updater.bot.send_message(chat_id=chat_id,
                             text="Bot started. Send me the name of the anime character you want to know more about!")

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
