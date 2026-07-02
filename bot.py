import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Poll
from telegram.ext import (
    Application,
    CommandHandler,
    PollAnswerHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load questions
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

QUIZ_TIME_LIMIT = 30  # seconds per question, adjust as you like


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! /quiz buyrug'ini yuboring va test boshlanadi.\n"
        f"Jami savollar soni: {len(QUESTIONS)}"
    )


async def quiz(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Har bir chat uchun holatni bot_data ichida saqlaymiz (chat_data emas),
    # chunki poll_answer yangilanishlari chat_data bilan to'g'ri bog'lanmaydi.
    quiz_states = context.bot_data.setdefault("quiz_states", {})
    quiz_states[chat_id] = {"score": 0, "current": 0}

    await send_question(chat_id, context, quiz_states[chat_id])


async def send_question(chat_id, context: ContextTypes.DEFAULT_TYPE, state: dict):
    idx = state["current"]

    if idx >= len(QUESTIONS):
        score = state["score"]
        await context.bot.send_message(
            chat_id,
            f"Test tugadi! Natijangiz: {score} / {len(QUESTIONS)}",
        )
        return

    q = QUESTIONS[idx]
    message = await context.bot.send_poll(
        chat_id=chat_id,
        question=f"{idx + 1}. {q['question']}",
        options=q["options"],
        type=Poll.QUIZ,
        correct_option_id=q["correct_option_id"],
        is_anonymous=False,
        open_period=QUIZ_TIME_LIMIT,
    )

    # Qaysi poll qaysi chatga tegishli ekanini eslab qolamiz
    poll_owner = context.bot_data.setdefault("poll_owner", {})
    poll_owner[message.poll.id] = chat_id

    # Agar foydalanuvchi belgilangan vaqt ichida javob bermasa,
    # bot baribir keyingi savolga avtomatik o'tsin.
    context.job_queue.run_once(
        handle_timeout,
        when=QUIZ_TIME_LIMIT + 2,
        data={"chat_id": chat_id, "idx": idx, "poll_id": message.poll.id},
        name=f"timeout-{chat_id}-{idx}",
    )


async def handle_timeout(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    chat_id = job_data["chat_id"]
    idx = job_data["idx"]
    poll_id = job_data["poll_id"]

    quiz_states = context.bot_data.get("quiz_states", {})
    state = quiz_states.get(chat_id)

    # Agar bu vaqtda javob allaqachon kelgan bo'lsa (current ilgarilab ketgan
    # bo'lsa), demak savol allaqachon davom ettirilgan — hech narsa qilmaymiz.
    if state is None or state["current"] != idx:
        return

    state["current"] = idx + 1
    context.bot_data.get("poll_owner", {}).pop(poll_id, None)

    await send_question(chat_id, context, state)


async def receive_poll_answer(update, context: ContextTypes.DEFAULT_TYPE):
    poll_answer = update.poll_answer
    poll_id = poll_answer.poll_id

    poll_owner = context.bot_data.get("poll_owner", {})
    quiz_states = context.bot_data.get("quiz_states", {})

    chat_id = poll_owner.get(poll_id)
    if chat_id is None or chat_id not in quiz_states:
        return

    state = quiz_states[chat_id]
    idx = state["current"]
    q = QUESTIONS[idx]

    selected = poll_answer.option_ids[0] if poll_answer.option_ids else None
    if selected == q["correct_option_id"]:
        state["score"] += 1

    state["current"] = idx + 1

    # endi bu poll bilan ishimiz tugadi, xotirani band qilmasin
    poll_owner.pop(poll_id, None)

    await send_question(chat_id, context, state)


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti")

    def log_message(self, format, *args):
        pass  # keep the console clean, we don't need HTTP access logs


def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    logger.info(f"Health-check server {port}-portda ishga tushdi")
    server.serve_forever()


def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_TOKEN muhit o'zgaruvchisi topilmadi. "
            "BotFather'dan olgan tokenni o'rnating."
        )

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(PollAnswerHandler(receive_poll_answer))

    # Render'ning bepul Web Service turi portga ulanishni talab qiladi,
    # shuning uchun bot bilan birga kichik HTTP server ham ishga tushiramiz.
    threading.Thread(target=start_health_server, daemon=True).start()

    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
