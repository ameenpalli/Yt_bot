import logging
import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ലോഗിങ് സെറ്റപ്പ് ചെയ്യുക, ഇത് ബോട്ട് പ്രവർത്തിക്കുമ്പോൾ എന്താണ് സംഭവിക്കുന്നതെന്ന് കാണാൻ സഹായിക്കും
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start കമാൻഡിനുള്ള ഫംഗ്ഷൻ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"ഹായ് {user_name}! ഒരു YouTube വീഡിയോ ലിങ്ക് അയച്ചാൽ ഞാൻ അത് MP3 ആയി ഡൗൺലോഡ് ചെയ്ത് തരാം."
    )

# YouTube ലിങ്ക് കൈകാര്യം ചെയ്യുന്ന ഫംഗ്ഷൻ
async def process_youtube_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    youtube_url = update.message.text
    
    # ലിങ്ക് ശരിയാണോ എന്ന് പരിശോധിക്കുന്നു
    if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
        await update.message.reply_text("ദയവായി ഒരു ശരിയായ YouTube ലിങ്ക് അയയ്ക്കുക.")
        return

    await update.message.reply_text("MP3 ഡൗൺലോഡ് ചെയ്യുകയാണ്, ദയവായി കാത്തിരിക്കുക...")

    try:
        # yt-dlp ക്ക് വേണ്ട ഓപ്ഷനുകൾ
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            # ഫയൽ നെയിം ലളിതമാക്കാനുള്ള ഓപ്ഷൻ
            'outtmpl': '%(title)s.%(ext)s',
            'restrictfilenames': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ഡൗൺലോഡ് ചെയ്യുന്നതിന് മുമ്പ് തന്നെ ഫയലിന്റെ പേര് പ്രവചിക്കുന്നു
            info = ydl.extract_info(youtube_url, download=False)
            original_filename = ydl.prepare_filename(info)
            final_filename = original_filename.rsplit('.', 1)[0] + '.mp3'
            
            # ഡൗൺലോഡ് ചെയ്ത് MP3 ആക്കി മാറ്റുന്നു
            ydl.download([youtube_url])

        # ഫയൽ ഉണ്ടോ എന്ന് പരിശോധിക്കുന്നു
        if not os.path.exists(final_filename):
            await update.message.reply_text("MP3 ഫയൽ ഉണ്ടാക്കാൻ സാധിച്ചില്ല. ദയവായി ffmpeg ശരിയായി ഇൻസ്റ്റാൾ ചെയ്തിട്ടുണ്ടോയെന്ന് ഉറപ്പുവരുത്തുക.")
            return

        # MP3 ഫയൽ ടെലിഗ്രാമിലേക്ക് അയയ്ക്കുന്നു
        with open(final_filename, 'rb') as audio_file:
            await update.message.reply_document(audio_file)
        
        await update.message.reply_text("ഡൗൺലോഡ് പൂർത്തിയായി.")
        
        # ഫയൽ ഡിലീറ്റ് ചെയ്യുക
        os.remove(final_filename)

    except Exception as e:
        await update.message.reply_text(f"ഒരു പിശക് സംഭവിച്ചു: {e}")

# മെയിൻ ഫംഗ്ഷൻ, ബോട്ട് പ്രവർത്തിപ്പിക്കാൻ
if __name__ == '__main__':
    TOKEN = '8228152793:AAFM4bepBOQ1b-BDzKXqfRHWMaHeiuZPWos'
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # കമാൻഡുകൾ ചേർക്കുക
    application.add_handler(CommandHandler("start", start))
    
    # YouTube ലിങ്കുകൾക്കായി മെസ്സേജ് ഹാൻഡ്ലർ
    youtube_link_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), process_youtube_link)
    application.add_handler(youtube_link_handler)
    
    # ബോട്ട് പ്രവർത്തിപ്പിക്കുക
    application.run_polling()