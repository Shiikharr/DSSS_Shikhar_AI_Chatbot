import logging
import requests
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# LM Studio configuration
LM_STUDIO_API_URL = "http://192.168.0.55:1234/v1" 
LM_STUDIO_MODEL = "llama-3.2-3b-instruct"         

# Chat history
messages = [{'role': 'system', 'content': 'You are a helpful assistant. Keep replies concise and helpful.'}]

# Handlers for Telegram bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I am Shikhar's personal AI Assistant Bot. I can have conversations with you. Please say something!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("I can help you with anything! Just type your question.")


async def bot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a reply using LM Studio."""
    user_input = update.message.text.strip()
    if not user_input:
        await update.message.reply_text("Please say something!")
        return

    # Append the user input to the chat history
    messages.append({'role': 'user', 'content': user_input})
    logger.info("Question from User: %s", user_input)

    try:
        # Sending the request to the LM Studio server to fetch the response from llama-3.2-3b-instruct
        response = requests.post(
            f"{LM_STUDIO_API_URL}/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": LM_STUDIO_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 200,
            },
        )

        if response.status_code == 200:
            # Parse the response
            data = response.json()
            reply = data["choices"][0]["message"]["content"].strip()
            
            # Append the assistant's reply to the chat history
            messages.append({'role': 'assistant', 'content': reply})

            # Sending the reply to the user
            await update.message.reply_text(reply)
        else:
            logger.error(f"Error from LM Studio: {response.status_code} - {response.text}")
            await update.message.reply_text("Sorry, I encountered an issue processing your request.")
    except Exception as e:
        logger.error(f"Exception: {e}")
        await update.message.reply_text("An error occurred while connecting to the AI model.")


def main() -> None:
    # Creating the Application and pass it to bot's token to start the bot.
    TELEGRAM_TOKEN = "7428432966:AAHvnmu2CmYS6y0RG1z2Ag-QMeHiMXPMDS8"
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Message handler for non-command text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_reply))

    # Run the bot
    application.run_polling()


if __name__ == "__main__":
    main()
