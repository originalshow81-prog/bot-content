import os
import logging
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
 
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")
 
SYSTEM_PROMPT = """Ești un expert în marketing și storytelling pentru rețele sociale (TikTok, Instagram).
Ajuți un creator de conținut care vinde mașini tip Lego (altă marcă), modele 1:8 și 1:10,
lungime 50-60 cm, 2500-4000 piese, calitate premium.
Publicul este mixt: copii, adulți, colecționari, oameni care caută cadouri speciale.
 
Stilul de storytelling al creatorului:
- Personal, sincer, ca o poveste reală
- Nu vinde direct — povestește o experiență
- Detalii tehnice transformate în emoții
- Final cu o concluzie subtilă care îndeamnă la acțiune
- Fraze scurte, ritm dinamic, potrivit pentru video
 
Exemplu de stil:
"Sincer, Porsche Mission R a fost ultima mea alegere când am decis ce să import.
2500 de piese, cel mai mic din colecție...
L-am terminat și l-am pus lângă celelalte.
De fiecare dată când cineva vede raftul, primul spre care merge mâna e Porsche-ul."
 
Răspunde ÎNTOTDEAUNA în limba română."""
 
 
def genereaza(prompt: str) -> str:
    try:
        response = model.generate_content(SYSTEM_PROMPT + "\n\n" + prompt)
        return response.text
    except Exception as e:
        logger.error(f"Eroare API: {e}")
        return f"❌ Eroare la generare: {str(e)}"
 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💡 Idei de videoclipuri", callback_data="idei")],
        [InlineKeyboardButton("📝 Script storytelling", callback_data="script_info")],
        [InlineKeyboardButton("🔥 Hook-uri puternice", callback_data="hookuri")],
    ]
    await update.message.reply_text(
        "👋 Salut! Sunt asistentul tău de conținut pentru mașini Lego.\n\n"
        "Ce vrei să generez azi?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
 
 
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
 
    if query.data == "idei":
        await query.edit_message_text("⏳ Generez idei...")
        response = genereaza(
            "Generează 5 idei creative de videoclipuri storytelling pentru TikTok/Instagram. "
            "Fiecare idee să aibă: titlu scurt + unghi narativ unic. "
            "Unghiuri diferite: surpriză, greșeală, comparație, emoție, curiozitate."
        )
        await query.edit_message_text(f"💡 *Idei de videoclipuri:*\n\n{response}", parse_mode="Markdown")
 
    elif query.data == "script_info":
        await query.edit_message_text(
            "📝 *Generare script*\n\n"
            "Trimite-mi numele modelului sau subiectul și îți scriu scriptul complet.\n\n"
            "Exemple:\n"
            "• `McLaren Senna`\n"
            "• `primul client mulțumit`\n"
            "• `de ce am ales să import aceste mașini`",
            parse_mode="Markdown"
        )
 
    elif query.data == "hookuri":
        await query.edit_message_text("⏳ Generez hook-uri...")
        response = genereaza(
            "Generează 7 hook-uri puternice pentru primele 3 secunde ale unui video TikTok/Instagram. "
            "Fiecare pe o linie separată. Abordări diferite: întrebare, afirmație șocantă, "
            "confesiune, cifră, provocare."
        )
        await query.edit_message_text(f"🔥 *Hook-uri puternice:*\n\n{response}", parse_mode="Markdown")
 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    msg = await update.message.reply_text("✍️ Scriu scriptul...")
    response = genereaza(
        f"Scrie un script complet de storytelling pentru un videoclip TikTok/Instagram despre: '{text}'. "
        f"Stil personal, sincer, fără să vândă direct. Lungime: 150-250 cuvinte. "
        f"La final adaugă 'Hook sugerat:' cu o variantă pentru primele 3 secunde."
    )
    await msg.edit_text(f"📝 *Script: {text}*\n\n{response}", parse_mode="Markdown")
 
 
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
 
 
if __name__ == "__main__":
    main()
