import telebot
import requests
import os

# --- TOKEN KAU ---
BOT_TOKEN = '8355388874:AAFAo5kO1mjfROz6auP4eITu5G0spvKNuXI'
bot = telebot.TeleBot(BOT_TOKEN)

def upload_file(file_path):
    # Kita guna Pomf.lain.la sebab Catbox tengah buat hal
    url = "https://pomf.lain.la/upload.php"
    try:
        with open(file_path, 'rb') as f:
            files = {'files[]': (os.path.basename(file_path), f)}
            response = requests.post(url, files=files, timeout=60)
            json_res = response.json()
            if json_res['success']:
                return json_res['files'][0]['url']
            return "Gagal upload ke Pomf."
    except Exception as e:
        return f"Error: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ **Bot Pomf Uploader Ready!**\nHantar fail, saya bagi link direct.", parse_mode="Markdown")

@bot.message_handler(content_types=['photo', 'video', 'document', 'audio'])
def handle_files(message):
    status = bot.reply_to(message, "⏳ Sedang diproses...")
    try:
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            ext = ".jpg"
        elif message.content_type == 'video':
            file_id = message.video.file_id
            ext = ".mp4"
        elif message.content_type == 'document':
            file_id = message.document.file_id
            ext = os.path.splitext(message.document.file_name)[1]
        else:
            file_id = message.audio.file_id
            ext = ".mp3"

        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        temp_name = f"up_{message.chat.id}{ext}"
        with open(temp_name, 'wb') as f:
            f.write(downloaded)

        link = upload_file(temp_name)
        
        if link.startswith("http"):
            bot.edit_message_text(f"✅ **Berjaya!**\n\n🔗 Link: `{link}`", message.chat.id, status.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(f"❌ {link}", message.chat.id, status.message_id)

        if os.path.exists(temp_name): os.remove(temp_name)
    except Exception as e:
        bot.edit_message_text(f"⚠️ Error: {str(e)}", message.chat.id, status.message_id)

print("🚀 Bot Pomf Jalan...")
bot.infinity_polling()
