import os
import subprocess
import telebot
import threading
import re

# Replace 'TOKENHERE' with your actual bot token
bot_token = '6354335918:AAFiGd0j3cOQZZYsheraItGj7fhMaZa7TZs'
bot = telebot.TeleBot(bot_token)

# Create a lock to prevent race conditions
lock = threading.Lock()

@bot.message_handler(func=lambda message: re.match(r'https?://\S+', message.text))
def process_link(message):
    """Process a link sent by the user."""
    def run():
        try:
            print(f"Received message {message.message_id}!")
            url = message.text

            # Check if the link contains "napstar"
            if 'napstar' in url.lower():
                # Acquire the lock
                lock.acquire()
                # Get the chat ID of the user who sent the message
                chat_id = message.chat.id
                bot.reply_to(message, "Download Started...")
                # Create a unique download directory for this user based on their chat ID
                download_dir = f"downloads/{chat_id}"
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)

                # Use subprocess to run the Orpheus script with the download link as an argument
                try:
                    process = subprocess.run(['python3', 'orpheus.py', '-o', download_dir, url],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output = process.stdout.decode('utf-8')
                    error_output = process.stderr.decode('utf-8')

                    # Check for errors
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

                # call  back queary

               if give_link:
                 zip_file_path = f"{download_dir}/{chat_id}.zip"
                 with zipfile.ZipFile(zip_file_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                    for file_path in music_files:
                    zip_file.write(file_path, os.path.basename(file_path))
                 upload_result = pixeldrain.upload(zip_file_path, anonymous=True)
                 if not upload_result.json()["success"]:
                     bot.send_message(chat_id=update.message.chat_id, text="Error uploading the zip file to Pixeldrain.")
               else:
                  for file_path in music_files:
                    with open(file_path, 'rb') as file:
                        bot.send_document(chat_id, file)

                # Delete the chat ID directory and its contents from the local file system
                os.rmdir(download_dir)
                print("Files sent and folder removed.")
            else:
                bot.reply_to(message, "Invalid link. Please send a link containing 'napstar'.")

        except:
        finally:
            # Release the lock
            lock.release()

    # Create a new thread to run the process_link function
    thread = threading.Thread(target=run)
    thread.start()


if __name__ == "__main__":
    bot.polling()
