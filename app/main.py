import logging
import os
import asyncio # Добавляем для возможной задержки между сообщениями
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction, MessageLimit # MessageLimit.TEXT_LENGTH = 4096
from genai.genai import GenAI
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение при команде /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Отправь мне любой текст, и я постараюсь ответить с помощью AI.",
    )
    logger.info(f"Пользователь {user.id} ({user.username}) запустил бота.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id # Получаем ID чата для отправки

    if not message_text:
        logger.warning(f"Получено пустое сообщение от пользователя {user_id}")
        return

    logger.info(f"Получено сообщение от {user_id} в чате {chat_id}: '{message_text}'")

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if 'gen_ai' not in context.bot_data:
         try:
             context.bot_data['gen_ai'] = GenAI()
             logger.info("Экземпляр GenAI создан и сохранен в bot_data.")
         except ValueError:
             await update.message.reply_text("Ошибка: Не удалось инициализировать AI модель. Проверьте ключ API Google.")
             return
             
    gen_ai_instance: GenAI = context.bot_data['gen_ai']

    ai_response_dict = gen_ai_instance.gen_text(message_text)
    response_text = ai_response_dict.get("response", "Произошла неожиданная ошибка.")

    # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
    # Вместо прямого ответа используем функцию для отправки длинных сообщений
    await send_long_message(context, chat_id, response_text)
    # -----------------------
    
    logger.info(f"Отправлен ответ для {user_id} в чат {chat_id}.")

async def send_long_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str):
    """Отправляет длинное сообщение, разбивая его на части."""
    if not text:
        return

    # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
    # Используем правильное имя атрибута
    max_length = MessageLimit.MAX_TEXT_LENGTH
    # -----------------------

    start_index = 0
    while start_index < len(text):
        end_index = start_index + max_length
        chunk = text[start_index:end_index]
        
        try:
            await context.bot.send_message(chat_id=chat_id, text=chunk)
            logger.debug(f"Отправлен чанк длиной {len(chunk)} в чат {chat_id}")
        except Exception as e:
             logger.error(f"Не удалось отправить чанк в чат {chat_id}: {e}", exc_info=True)
             break

        start_index = end_index
        await asyncio.sleep(0.1)

def main() -> None:
    """Запускает бота."""
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TOKEN:
        logger.critical("TELEGRAM_BOT_TOKEN не найден в переменных окружения! Бот не может быть запущен.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Регистрация обработчиков завершена.")

    logger.info("Запуск бота...")
    application.run_polling()

if __name__ == '__main__':
    main()