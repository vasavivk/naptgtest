import os
import subprocess
import telebot
import re

bot_token = '6354335918:AAFiGd0j3cOQZZYsheraItGj7fhMaZa7TZs'
bot = telebot.TeleBot(bot_token)

@bot.message_handler(func=lambda message: re.match(r'https?://\S+', message.text))
def process_link(message):
    try:
        print(f"Received message {message.message_id}!")
        url = message.text

        if 'napster' in url:
            chat_id = message.chat.id
            bot.reply_to(message, "Download Started...")
            download_dir = f"downloads/{chat_id}"
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            try:
                process = subprocess.run(['python3', 'orpheus.py', '-o', download_dir, url],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = process.stdout.decode('utf-8')
                error_output = process.stderr.decode('utf-8')

                if process.returncode != 0:
                    return
            except Exception as e:
                return

            bot.reply_to(message, "Download finished")
            print("Downloaded files")
            music_files = []
            for root, dirs, files in os.walk(download_dir):
                for file in files:
                    if file.endswith(".flac") or file.endswith(".m4a") or file.endswith(".png") or file.endswith(".jpg") or file.endswith(".lrc"):
                        filepath = os.path.join(root, file)
                        music_files.append(filepath)

            if not music_files:
                bot.reply_to(message, "No music files found to send. This is most likely a bug, try again.")
                shutil.rmtree(download_dir)
                return

            bot.reply_to(message, "Sending files to the user...")

            for file_path in music_files:
                with open(file_path, 'rb') as file:
                    bot.send_document(chat_id, file)

            os.rmdir(download_dir)
            print("Files sent and folder removed.")
        else:
            bot.reply_to(message, "Invalid link. Please send a link containing 'napstar'.")
    except:
         bot.reply_to(message, "Something went wrong")

if __name__ == "__main__":
    bot.polling()
