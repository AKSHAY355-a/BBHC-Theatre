"""
BBHC Theatre - Flask Backend
Handles authentication, movie search, and streaming integration
"""
import asyncio
import json
import os
import re
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_cors import CORS
from functools import wraps
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.errors.rpcerrorlist import AuthRestartError
from config import API_ID, API_HASH, SEARCH_BOT_USERNAME, STREAMING_BOT_USERNAME
import nest_asyncio
import tempfile
import os as _os
from typing import Optional

# Apply nest_asyncio globally
nest_asyncio.apply()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Configuration
SESSION_VALIDITY_HOURS = 24
ADMIN_CREDENTIALS_FILE = "admin_credentials.json"
PENDING_LOGINS = {}

# Thread lock for Telegram operations
telegram_lock = threading.Lock()

# Telegram client
api_id = int(API_ID)
api_hash = API_HASH
bot_username = SEARCH_BOT_USERNAME

def save_admin_credentials(admin_name, phone):
    credentials = {
        "admin_name": admin_name,
        "phone": phone,
        "created_at": datetime.now().isoformat()
    }
    with open(ADMIN_CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f)

def load_admin_credentials():
    if os.path.exists(ADMIN_CREDENTIALS_FILE):
        with open(ADMIN_CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session.get('logged_in'):
            return jsonify({'error': 'Authentication required', 'redirect': '/login'}), 401
        if 'expires_at' in session:
            expires_at = datetime.fromisoformat(session['expires_at'])
            if datetime.now() > expires_at:
                session.clear()
                return jsonify({'error': 'Session expired', 'redirect': '/login'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'logged_in' not in session or not session.get('logged_in'):
        return redirect(url_for('login_page'))
    if 'expires_at' in session:
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            session.clear()
            return redirect(url_for('login_page'))
    return render_template('index.html', admin_name=session.get('admin_name'))

@app.route('/login')
def login_page():
    credentials = load_admin_credentials()
    return render_template('login.html', has_credentials=(credentials is not None))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/check-credentials', methods=['GET'])
def check_credentials():
    credentials = load_admin_credentials()
    if credentials:
        return jsonify({
            'exists': True,
            'admin_name': credentials['admin_name'],
            'phone': credentials['phone']
        })
    return jsonify({'exists': False})

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    admin_name = data.get('admin_name', '').strip()
    phone_number = data.get('phone_number', '').strip()
    
    if not admin_name or not phone_number:
        return jsonify({'error': 'Admin name and phone number are required'}), 400
    
    if not phone_number.startswith('+91'):
        if phone_number.startswith('91'):
            phone_number = '+' + phone_number
        else:
            phone_number = '+91' + phone_number
    
    session_name = f"admin_{phone_number.replace('+', '').replace(' ', '')}"
    
    async def send_code():
        client = TelegramClient(session_name, api_id, api_hash)
        try:
            # Ensure connection established
            for _ in range(3):
                await client.connect()
                if client.is_connected():
                    break
                await asyncio.sleep(0.5)

            # Retry sending code on transient Telegram errors
            last_err = None
            for _ in range(3):
                try:
                    result = await client.send_code_request(phone_number)
                    phone_code_hash = result.phone_code_hash
                    return phone_code_hash
                except (ConnectionError, AuthRestartError) as e:  # type: ignore[misc]
                    last_err = e
                    # Reconnect and retry
                    try:
                        if client.is_connected():
                            await client.disconnect()
                    except Exception:
                        pass
                    await asyncio.sleep(1.0)
                    await client.connect()
                except Exception as e:
                    last_err = e
                    break
            if last_err:
                raise last_err
        finally:
            if client.is_connected():
                await client.disconnect()
    
    try:
        with telegram_lock:
            phone_code_hash = asyncio.run(send_code())
        
        PENDING_LOGINS[phone_number] = {
            'admin_name': admin_name,
            'phone': phone_number,
            'session_name': session_name,
            'phone_code_hash': phone_code_hash,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({'success': True, 'message': 'OTP sent', 'phone': phone_number})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to send OTP: {str(e)}'}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    phone_number = data.get('phone_number', '').strip()
    otp_code = data.get('otp_code', '').strip()
    password = data.get('password', '').strip()
    
    if not phone_number or not otp_code:
        return jsonify({'error': 'Phone and OTP required'}), 400
    
    pending = PENDING_LOGINS.get(phone_number)
    if not pending:
        return jsonify({'error': 'No pending login'}), 400
    
    session_name = pending['session_name']
    admin_name = pending['admin_name']
    phone_code_hash = pending.get('phone_code_hash')
    
    if not phone_code_hash:
        return jsonify({'error': 'Invalid session. Please request OTP again.'}), 400
    
    async def verify_code():
        client = TelegramClient(session_name, api_id, api_hash)
        try:
            await client.connect()
            try:
                await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)
                return True
            except SessionPasswordNeededError:
                if password:
                    await client.sign_in(password=password)
                    return True
                return '2fa_required'
            except PhoneCodeInvalidError:
                return False
        finally:
            if client.is_connected():
                await client.disconnect()
    
    try:
        with telegram_lock:
            result = asyncio.run(verify_code())
        
        if result == '2fa_required':
            return jsonify({'error': '2fa_required'}), 400
        if not result:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        save_admin_credentials(admin_name, phone_number)
        session['logged_in'] = True
        session['admin_name'] = admin_name
        session['phone'] = phone_number
        session['login_time'] = datetime.now().isoformat()
        session['expires_at'] = (datetime.now() + timedelta(hours=SESSION_VALIDITY_HOURS)).isoformat()
        del PENDING_LOGINS[phone_number]
        
        return jsonify({'success': True, 'admin_name': admin_name, 'redirect': '/'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

@app.route('/api/session-status', methods=['GET'])
def session_status():
    if 'logged_in' in session and session.get('logged_in'):
        if 'expires_at' in session:
            expires_at = datetime.fromisoformat(session['expires_at'])
            if datetime.now() > expires_at:
                session.clear()
                return jsonify({'logged_in': False})
        return jsonify({
            'logged_in': True,
            'admin_name': session.get('admin_name'),
            'phone': session.get('phone')
        })
    return jsonify({'logged_in': False})

@app.route('/api/search-movie', methods=['POST'])
@login_required
def search_movie():
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    async def search():
        phone = session.get('phone')
        session_name = f"admin_{phone.replace('+', '').replace(' ', '')}"
        client = TelegramClient(session_name, api_id, api_hash)
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.start()
            
            results = []
            
            async with client.conversation(bot_username, timeout=30) as conv:
                await conv.send_message(query)
                replies = [await conv.get_response()]
                try:
                    for _ in range(3):
                        replies.append(await conv.get_response(timeout=2))
                except:
                    pass
                
                for msg in replies:
                    if hasattr(msg, 'buttons') and msg.buttons:
                        for row_idx, row in enumerate(msg.buttons):
                            for btn_idx, btn in enumerate(row):
                                label = getattr(btn, 'text', '').strip()
                                if label and 'update' not in label.lower() and 'group' not in label.lower() and 'backup' not in label.lower() and 'channel' not in label.lower():
                                    results.append({
                                        'title': label,
                                        'message_id': msg.id,
                                        'row': row_idx,
                                        'col': btn_idx
                                    })
            return results
        finally:
            await client.disconnect()
    
    try:
        with telegram_lock:
            results = asyncio.run(search())
        return jsonify({'success': True, 'results': results, 'query': query})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/get-stream-link', methods=['POST'])
@login_required
def get_stream_link():
    data = request.json
    message_id = data.get('message_id')
    row = data.get('row')
    col = data.get('col')
    
    async def get_link():
        phone = session.get('phone')
        session_name = f"admin_{phone.replace('+', '').replace(' ', '')}"
        client = TelegramClient(session_name, api_id, api_hash)
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.start()
            
            msg = await client.get_messages(bot_username, ids=message_id)
            if msg and hasattr(msg, 'buttons'):
                await msg.click(i=row, j=col)
                await asyncio.sleep(3)
                messages = await client.get_messages(bot_username, limit=10)
                
                for m in messages:
                    if hasattr(m, 'document') or hasattr(m, 'video'):
                        if STREAMING_BOT_USERNAME:
                            await client.forward_messages(STREAMING_BOT_USERNAME, m)
                            await asyncio.sleep(2)
                            bot_messages = await client.get_messages(STREAMING_BOT_USERNAME, limit=5)
                            for bot_msg in bot_messages:
                                if bot_msg.text and 'watch' in bot_msg.text.lower():
                                    urls = re.findall(r'(https?://[^\s]+)', bot_msg.text)
                                    if urls:
                                        return urls[0]
            return None
        finally:
            await client.disconnect()
    
    try:
        with telegram_lock:
            stream_url = asyncio.run(get_link())
        
        if stream_url:
            return jsonify({'success': True, 'stream_url': stream_url})
        return jsonify({'error': 'Failed to get stream link'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed: {str(e)}'}), 500

@app.route('/api/download', methods=['GET'])
@login_required
def download_media():
    message_id = request.args.get('message_id', type=int)
    row = request.args.get('row', type=int)
    col = request.args.get('col', type=int)

    if message_id is None or row is None or col is None:
        return jsonify({'error': 'Missing required parameters'}), 400

    async def fetch_and_download():
        phone = session.get('phone')
        session_name = f"admin_{phone.replace('+', '').replace(' ', '')}"
        client = TelegramClient(session_name, api_id, api_hash)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.start()

            msg = await client.get_messages(bot_username, ids=message_id)
            if msg and hasattr(msg, 'buttons'):
                # Click the requested button. Some bots respond with edited message, new message, or URL.
                click_result = None
                try:
                    click_result = await msg.click(i=row, j=col)
                except Exception:
                    pass

                # Handle URL deep-links like t.me/bot?start=XXXX by sending /start payload back to the bot
                try:
                    url = getattr(click_result, 'url', None)
                    if url and 'start=' in url:
                        start_payload = '/start ' + url.split('start=')[-1]
                        await client.send_message(bot_username, start_payload)
                except Exception:
                    pass

                # Poll for a media message from the bot after clicking
                media_msg: Optional[object] = None
                for _ in range(10):  # ~10 seconds total
                    messages = await client.get_messages(bot_username, limit=20)
                    for m in messages:
                        if getattr(m, 'document', None) or getattr(m, 'video', None) or getattr(m, 'audio', None):
                            media_msg = m
                            break
                    if media_msg:
                        break
                    await asyncio.sleep(1)

                # As a fallback, try to refresh the original message and scan again
                if not media_msg:
                    try:
                        refreshed = await client.get_messages(bot_username, ids=message_id)
                        if refreshed:
                            messages = await client.get_messages(bot_username, limit=30)
                            for m in messages:
                                if getattr(m, 'document', None) or getattr(m, 'video', None) or getattr(m, 'audio', None):
                                    media_msg = m
                                    break
                    except Exception:
                        pass

                if not media_msg:
                    return None, None

                # Determine filename
                filename = None
                if getattr(media_msg, 'document', None) and getattr(media_msg.document, 'attributes', None):
                    for attr in media_msg.document.attributes:
                        name = getattr(attr, 'file_name', None)
                        if name:
                            filename = name
                            break

                if not filename:
                    filename = (media_msg.file and getattr(media_msg.file, 'name', None)) or 'movie.mp4'

                # Download to a temporary file
                tmp_dir = tempfile.gettempdir()
                safe_name = re.sub(r"[^A-Za-z0-9._-]", '_', filename)
                tmp_path = _os.path.join(tmp_dir, f"bbhc_{safe_name}")

                await client.download_media(media_msg, file=tmp_path)
                return tmp_path, safe_name
            return None, None
        finally:
            await client.disconnect()

    try:
        with telegram_lock:
            tmp_path, safe_name = asyncio.run(fetch_and_download())

        if not tmp_path or not _os.path.exists(tmp_path):
            return jsonify({'error': 'Failed to fetch media from Telegram'}), 500

        # Serve file as attachment; cleanup after request
        response = send_file(tmp_path, as_attachment=True, download_name=safe_name)

        @response.call_on_close
        def _cleanup_file():
            try:
                if _os.path.exists(tmp_path):
                    _os.remove(tmp_path)
            except Exception:
                pass

        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
