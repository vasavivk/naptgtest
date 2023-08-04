import os
import shutil
import subprocess
import threading
import telebot

# Replace 'TOKENHERE' with your actual bot token
bot_token = '6354335918:AAFiGd0j3cOQZZYsheraItGj7fhMaZa7TZs'

# Create a new instance of the bot
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['download'])
def download_music(message):
    """Download music from a link and send the files directly to the user."""
    
    def run():
        try:
            print(f"Received message {message.message_id}!")
            url = message.text.split(' ', 1)[1]

            # Send a message to the user
            bot.reply_to(message, "Download Started...")

            # Get the chat ID of the user who sent the message
            chat_id = message.chat.id

            # Create a unique download directory for this user based on their chat ID
            download_dir = f"downloads/{chat_id}"
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            # Use subprocess to run the Orpheus script with the download link as an argument
            try:
                process = subprocess.run(['python3', 'orpheus.py', '-o', download_dir, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = process.stdout.decode('utf-8')
                error_output = process.stderr.decode('utf-8')

                # Check for errors
                if process.returncode != 0:
                    return
            except Exception as e:
                return

            bot.reply_to(message, "Download finished")
            print("Downloaded files")

            # Find all the music files in the chat ID directory and its subdirectories
            music_files = []
            for root, dirs, files in os.walk(download_dir):
                for file in files:
                    if file.endswith(".flac") or file.endswith(".m4a") or file.endswith(".png") or file.endswith(".lrc"):
                        filepath = os.path.join(root, file)
                        music_files.append(filepath)

            if not music_files:
                bot.reply_to(message, "No music files found to send. This is most likely a bug, try again.")
                shutil.rmtree(download_dir)
                return

            bot.reply_to(message, "Sending files to the user...")

            # Send each music file to the user
            for file_path in music_files:
                with open(file_path, 'rb') as file:
                    bot.send_document(chat_id, file)

            # Delete the chat ID directory and its contents from the local file system
            shutil.rmtree(download_dir)
            print("Files sent and folder removed.")

        except Exception as err:
            bot.reply_to(message, "An error occurred, please try again later.")

    threading.Thread(target=run).start()

if __name__ == "__main__":
    bot.polling()
