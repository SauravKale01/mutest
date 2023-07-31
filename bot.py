import requests
import time
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

def get_random_character():
    query = """
    query {
        Page(page: 1, perPage: 1) {
            characters {
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
    }
    """

    response = requests.post(ANILIST_BASE_URL, json={"query": query})

    if response.status_code == 200:
        data = response.json()

        if "data" in data and "Page" in data["data"] and "characters" in data["data"]["Page"]:
            character_data = data["data"]["Page"]["characters"][0]
            character_name = character_data["name"]["full"]
            character_image = character_data["image"]["medium"]
            anime_series = character_data["media"]["nodes"][0]["title"]["romaji"]

            return character_name, character_image, anime_series

    print("Error:", response.status_code, response.text)  # Add this line to check the API response
    return None, None, None

@app.on_message(filters.command("start"))
def start(_, message: Message):
    message.reply_text("Welcome to the Anime Character Quiz Bot!\nSend /quiz to start the quiz.")

@app.on_message(filters.command("quiz"))
def quiz(_, message: Message):
    user_id = message.from_user.id

    if user_id not in SCORES:
        SCORES[user_id] = 0

    character_name, character_image, anime_series = get_random_character()

    if character_name and character_image and anime_series:
        # Add the character's name in the caption along with the protective message
        caption = f"Who is this character?\n{character_name}\n\n{protective_message}"
        message.reply_photo(character_image, caption=caption)

        # Store the correct answer and anime series in the user_data dictionary
        app.user_data[user_id] = {
            "correct_answer": character_name,
            "anime_series": anime_series,
        }
    else:
        message.reply_text("Oops! Something went wrong. Please try again later.")

    # Introduce a slight delay (2 seconds) before asking the next question
    time.sleep(2)
    message.reply_text("Next question:")

@app.on_message(filters.text & ~filters.command("quiz"))
def check_answer(_, message: Message):
    user_id = message.from_user.id

    # Check if the user has played the quiz before
    if user_id not in app.user_data:
        message.reply_text("Send /quiz to start the quiz.")
        return

    # Retrieve the correct answer and anime series from user_data
    user_data = app.user_data[user_id]
    correct_answer = user_data.get("correct_answer")
    anime_series = user_data.get("anime_series")

    # Check if the user's answer matches the correct answer
    if message.text.strip().lower() == correct_answer.lower():
        SCORES[user_id] += 1
        message.reply_text(f"Correct! This character is from {anime_series}. Your score: {SCORES[user_id]}")
    else:
        message.reply_text(f"Wrong! This character is from {anime_series}. Your score: {SCORES[user_id]}")

    # Ask the next question
    quiz(_, message)


@app.on_message(filters.command("score"))
def show_score(_, message: Message):
    user_id = message.from_user.id

    if user_id in SCORES:
        score = SCORES[user_id]
        message.reply_text(f"Your current score is: {score}")
    else:
        message.reply_text("You haven't played the quiz yet. Send /quiz to start.")

protective_message = (
    "I protecc, I attacc,\n"
    "but most importantly, I got your bacc! 🛡️"
)

print("Bot Started")

if __name__ == "__main__":
    app.run()
