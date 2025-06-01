# TelegDriveBot: Telegram → Google Drive Uploader Bot (Single-File, No Database)

TelegDriveBot is a powerful yet easy-to-use Telegram bot that lets you upload files from Telegram (or direct download links) straight to your Google Drive.  
This version is a **single Python file**, requires no database, and stores user authentication tokens and settings in a local JSON file.

---

## 🚀 Features

- **Authorize via Google OAuth**: Users connect their Google Drive to the bot.
- **Upload from Telegram**: Send files (document, video, audio, photo) to the bot and upload to your Google Drive.
- **Direct Link Uploads**: Send a direct HTTP/HTTPS link and the bot will fetch and upload it.
- **Custom Folder Support**: Set a custom Google Drive folder as your upload destination.
- **No Database Required**: All user data is stored in a local `users.json` file.
- **Easy Setup**: Just fill in your bot and Google credentials, and you're ready to go!

---

## 🛠️ Setup Instructions

### 1. Clone or Download This Repo

```
git clone https://github.com/KINGSTABLE/TG-TO-GD-UPLOAD-BOT.git
cd TG-TO-GD-UPLOAD-BOT
```
Or simply download the script file.

---

### 2. Create a Google Cloud Project and OAuth Credentials

- Go to the [Google Cloud Console](https://console.cloud.google.com/).
- Create a new project (or select an existing one).
- Enable the **Google Drive API** for the project.
- Go to **APIs & Services > Credentials**.
- Click **Create Credentials > OAuth client ID**.
- Choose **Desktop App**.
- Download the `credentials.json` file and place it in the same folder as the bot script.

See [Google's step-by-step guide](https://developers.google.com/drive/api/quickstart/python) if you need more help.

---

### 3. Create Your Telegram Bot

- Open [@BotFather](https://t.me/BotFather) on Telegram.
- Send `/newbot` and follow the prompts to get your **BOT_TOKEN**.

---

### 4. Fill in Your Credentials

Edit the top of the Python script and fill in:
- `BOT_TOKEN`
- `APP_ID` and `API_HASH` (get from [my.telegram.org](https://my.telegram.org))
- (Optional) Change the download directory, SUDO_USERS, etc.

---

### 5. Install Dependencies

```sh
pip install pyrogram tgcrypto google-auth google-auth-oauthlib google-api-python-client requests
```

---

### 6. Run the Bot

```sh
python telegdrivebot_full.py
```

---

## 💬 Usage

1. **/start or /help** – See usage instructions.
2. **/auth** – Start Google Drive authentication. Follow the link, paste back the code with `/code <your_code>`.
3. **Send a File** – Uploads to your Google Drive root (or selected folder).
4. **Send a Direct HTTP/HTTPS Link** – Bot downloads the file and uploads it.
5. **/setfolder <FOLDER_ID>** – Set a custom Google Drive folder as the upload target.
6. **/revoke** – Remove your Google Drive authorization.

---

## 📁 Privacy & Terms

- All user tokens and settings are stored locally in `users.json`.
- Use `/revoke` to delete your data.
- See [`privacy-policy.md`](privacy-policy.md) and [`terms-of-service.md`](terms-of-service.md).

---

## 📝 Notes

- For private/personal use, you can keep your Google OAuth consent screen in "testing" and add your email as a test user.
- If you want to make the bot public, you must publish the OAuth app and provide a public Privacy Policy and Terms of Service.
- This version is for **single-server/single-user** or small group use. For production/multi-server use, consider a database-backed version.

---

## ⭐️ Credits

- Powered by [Pyrogram](https://github.com/pyrogram/pyrogram) and [Google Drive API](https://developers.google.com/drive).
- Inspired by [many open-source Telegram Drive bots](https://github.com/topics/telegram-drive-bot).
- MADE BY @TOOLS_BOTS_KING
---

## 🟢 License

MIT License. See [LICENSE](LICENSE) for details.
