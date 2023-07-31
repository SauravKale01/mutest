import requests
import time
import random
from pyrogram import Client, filters
from pyrogram.types import Message

# Replace these with your own credentials
API_ID = 19099900
API_HASH = '2b445de78e5baf012a0793e60bd4fbf5'
BOT_TOKEN = '6206599982:AAFhXRwC0SnPCBK4WDwzdz7TbTsM2hccgZc'

app = Client("anime_quiz_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# AniList API Base URL
ANILIST_BASE_URL = "https://graphql.anilist.co"

SCORES = {}  # Dictionary to store users' scores

# Create a dictionary to store user-specific data
user_data = {}

# Add a variable to store the last character ID used to avoid repetition
last_character_id = None

def get_random_character():
    query = """
    query {
        Character(id: """ + str(random.randint(1, 10000)) + """) {
            id
            name {
                full
            }
            image {
                medium
            }
            media {
                nodes {
                    title {
                        romaji
                    }
                }
            }
        }
    }
    """

    response = requests.post(ANILIST_BASE_URL, json={"query": query})

    if response.status_code == 200:
        data = response.json()

        if "data" in data and "Character" in data["data"]:
            character_data = data["data"]["Character"]
            character_id = character_data["id"]

            # Check if the character ID is the same as the last one used
            # If yes, fetch another character
            if character_id == last_character_id:
                return get_random_character()

            last_character_id = character_id

            character_name = character_data["name"]["full"]
            character_image = character_data["image"]["medium"]
            anime_series = character_data["media"]["nodes"][0]["title"]["romaji"]

            return character_name, character_image, anime_series

    print("Error:", response.status_code, response.text)  # Add this line to check the API response
    return None, None, None

# ... (unchanged)

@app.on_message(filters.command("quiz"))
def quiz(_, message: Message):
    user_id = message.from_user.id

    if user_id not in SCORES:
        SCORES[user_id] = 0

    character_name, character_image, anime_series = get_random_character()

    if character_name and character_image and anime_series:
        # Add the character's name in the caption without the protective message
        caption = f"Who is this character?\n{character_name}"
        message.reply_photo(character_image, caption=caption)

        # Store the correct answer and anime series in the user_data dictionary
        user_data[user_id] = {
            "correct_answer": character_name,
            "anime_series": anime_series,
        }

        # Ask the next question after a 2-second delay
        time.sleep(2)
        app.ask(quiz, args=(message,))

    else:
        message.reply_text("Oops! Something went wrong. Please try again later.")

# ... (unchanged)

protective_message = (
    "I protecc, I attacc,\n"
    "but most importantly, I got your bacc! 🛡️\n\n"
    "You answered: {}"
)


@app.on_message(filters.command("score"))
def show_score(_, message: Message):
    user_id = message.from_user.id

    if user_id in SCORES:
        score = SCORES[user_id]
        message.reply_text(f"Your current score is: {score}")
    else:
        message.reply_text("You haven't played the quiz yet. Send /quiz to start.")

print("Bot Started")

if __name__ == "__main__":
    app.run()
