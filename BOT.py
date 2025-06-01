import os
import json
import threading
import asyncio
from pyrogram import Client, filters
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# --- CONFIGURATION ---
BOT_TOKEN = "YOUR_BOT_TOKEN"
APP_ID = "YOUR_APP_ID"
API_HASH = "YOUR_API_HASH"
SUDO_USERS = [123456789]  # Your Telegram user ID(s) as integers
DOWNLOAD_DIRECTORY = "./downloads/"
DB_FILE = "users.json"
GOOGLE_CREDENTIALS_FILE = "credentials.json"  # Downloaded OAuth credentials file

# --- SIMPLE JSON "DB" ---
LOCK = threading.Lock()
def _load():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def set_user(user_id, data):
    with LOCK:
        db = _load()
        db[str(user_id)] = data
        _save(db)

def get_user(user_id):
    db = _load()
    return db.get(str(user_id), {})

def save_gdrive_token(user_id, token_dict):
    user = get_user(user_id)
    user['gdrive_token'] = token_dict
    set_user(user_id, user)

def get_gdrive_token(user_id):
    user = get_user(user_id)
    return user.get('gdrive_token')

def set_custom_folder(user_id, folder_id):
    user = get_user(user_id)
    user['custom_folder'] = folder_id
    set_user(user_id, user)

def get_custom_folder(user_id):
    user = get_user(user_id)
    return user.get('custom_folder')

# --- GOOGLE DRIVE UTILS ---
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_flow():
    return Flow.from_client_secrets_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )

def get_drive_service(token_dict):
    creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service

async def send_big_file(client, chat_id, path, text="Uploading..."):
    # Helper: send big file as a document (for large logs, etc)
    await client.send_document(chat_id, path, caption=text)

def upload_to_drive(token_dict, filepath, filename, parent_id=None):
    creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
    service = build("drive", "v3", credentials=creds)
    file_metadata = {'name': filename}
    if parent_id:
        file_metadata['parents'] = [parent_id]
    media = MediaFileUpload(filepath, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
    return file

# --- PYROGRAM BOT ---
app = Client("telegdrivebot",
             bot_token=BOT_TOKEN,
             api_id=APP_ID,
             api_hash=API_HASH)

@app.on_message(filters.command(["start", "help"]))
async def start(client, message):
    await message.reply(
        "**Hi!**\n"
        "Send me a file or a direct download link and I'll upload it to your Google Drive.\n"
        "Use /auth to connect your Google Drive account."
    )

@app.on_message(filters.command(["auth"]))
async def auth(client, message):
    user_id = message.from_user.id
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt="consent")
    await message.reply(
        f"**Google Drive Authorization:**\n"
        f"1. Click this [authorization link]({auth_url})\n"
        f"2. Sign in and copy the code you get\n"
        f"3. Send the code here as `/code YOUR_CODE`"
    )
    # Save the flow's state for this user
    user = get_user(user_id)
    user['auth_flow'] = flow.credentials_to_dict()
    set_user(user_id, user)
    # Note: We do NOT save the flow object itself, just use a new one for each /code

@app.on_message(filters.command(["code"]))
async def code_handler(client, message):
    user_id = message.from_user.id
    code = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not code:
        await message.reply("Please send the code as `/code YOUR_CODE`.")
        return
    flow = get_flow()
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials
        creds_dict = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }
        save_gdrive_token(user_id, creds_dict)
        await message.reply("✅ Google Drive account authorized successfully!")
    except Exception as e:
        await message.reply(f"❌ Failed to authorize: `{e}`")

@app.on_message(filters.command(["setfolder"]))
async def setfolder(client, message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Send the folder ID or link after /setfolder.")
        return
    folder = args[1].strip()
    set_custom_folder(user_id, folder)
    await message.reply(f"Custom upload folder set to: {folder}")

@app.on_message(filters.command(["revoke"]))
async def revoke(client, message):
    user_id = message.from_user.id
    set_user(user_id, {})  # Remove all user data
    await message.reply("Google Drive account revoked. Use /auth to authorize again.")

@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file(client, message):
    user_id = message.from_user.id
    token = get_gdrive_token(user_id)
    if not token:
        await message.reply("You must /auth first to use Google Drive.")
        return
    await message.reply("Downloading your file...")
    file_path = await message.download(DOWNLOAD_DIRECTORY)
    filename = os.path.basename(file_path)
    await message.reply("Uploading to Google Drive...")
    parent_id = get_custom_folder(user_id)
    try:
        file = upload_to_drive(token, file_path, filename, parent_id)
        await message.reply(
            f"✅ Uploaded `{filename}` to Google Drive!\n"
            f"[Open in Drive]({file.get('webViewLink')})",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(f"❌ Upload failed: `{e}`")

@app.on_message(filters.text & ~filters.command(["auth", "setfolder", "start", "help", "revoke", "code"]))
async def handle_link(client, message):
    user_id = message.from_user.id
    token = get_gdrive_token(user_id)
    if not token:
        await message.reply("You must /auth first to use Google Drive.")
        return
    url = message.text.strip()
    await message.reply(f"Downloading from {url} ...")
    # Download the file from URL (basic implementation)
    try:
        import requests
        r = requests.get(url, stream=True, timeout=30)
        if not r.ok:
            await message.reply("Failed to download file.")
            return
        filename = url.split("/")[-1]
        file_path = os.path.join(DOWNLOAD_DIRECTORY, filename)
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        await message.reply("Uploading to Google Drive...")
        parent_id = get_custom_folder(user_id)
        file = upload_to_drive(token, file_path, filename, parent_id)
        await message.reply(
            f"✅ Uploaded `{filename}` to Google Drive!\n"
            f"[Open in Drive]({file.get('webViewLink')})",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(f"❌ Failed: `{e}`")

if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)
    app.run()
