"""
Telegram OTP Login System
Authenticates admin users via phone number and OTP before allowing access to search functionality
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from config import API_ID, API_HASH

# Session storage file
SESSION_FILE = "auth_session.json"
SESSION_VALIDITY_HOURS = 24

class TelegramAuth:
    def __init__(self):
        self.api_id = int(API_ID)
        self.api_hash = API_HASH
        self.client = None
        self.phone = None
        self.admin_name = None
        
    def save_session(self):
        """Save authenticated session info"""
        session_data = {
            "admin_name": self.admin_name,
            "phone": self.phone,
            "timestamp": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(hours=SESSION_VALIDITY_HOURS)).isoformat()
        }
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f)
        print(f"✅ Session saved. Valid for {SESSION_VALIDITY_HOURS} hours.")
    
    def load_session(self):
        """Load and validate existing session"""
        if not os.path.exists(SESSION_FILE):
            return False
        
        try:
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
            
            expires = datetime.fromisoformat(session_data['expires'])
            if datetime.now() > expires:
                print("⚠️ Session expired. Please login again.")
                os.remove(SESSION_FILE)
                return False
            
            self.admin_name = session_data['admin_name']
            self.phone = session_data['phone']
            print(f"✅ Welcome back, {self.admin_name}!")
            print(f"📱 Phone: {self.phone}")
            return True
        except Exception as e:
            print(f"⚠️ Error loading session: {e}")
            return False
    
    async def login(self, admin_name, phone_number):
        """Authenticate user with Telegram OTP"""
        self.admin_name = admin_name
        
        # Ensure phone number starts with +91
        if not phone_number.startswith('+91'):
            if phone_number.startswith('91'):
                phone_number = '+' + phone_number
            elif phone_number.startswith('+'):
                phone_number = phone_number
            else:
                phone_number = '+91' + phone_number
        
        self.phone = phone_number
        
        print(f"\n👤 Admin: {admin_name}")
        print(f"📱 Phone: {phone_number}")
        print("\n🔐 Initiating Telegram authentication...")
        
        # Create Telegram client with unique session name
        session_name = f"admin_{phone_number.replace('+', '').replace(' ', '')}"
        self.client = TelegramClient(session_name, self.api_id, self.api_hash)
        
        try:
            await self.client.connect()
            
            # Check if already authorized
            if await self.client.is_user_authorized():
                print("✅ Already authenticated!")
                self.save_session()
                return True
            
            # Send OTP
            print("📤 Sending OTP to your phone...")
            await self.client.send_code_request(phone_number)
            
            # Get OTP from user
            otp = input("\n🔢 Enter the OTP code you received: ").strip()
            
            try:
                await self.client.sign_in(phone_number, otp)
                print("✅ Authentication successful!")
                self.save_session()
                return True
                
            except SessionPasswordNeededError:
                # 2FA is enabled
                password = input("🔒 Two-factor authentication enabled. Enter your password: ").strip()
                await self.client.sign_in(password=password)
                print("✅ Authentication successful!")
                self.save_session()
                return True
                
            except PhoneCodeInvalidError:
                print("❌ Invalid OTP code. Please try again.")
                return False
                
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
        finally:
            if self.client:
                await self.client.disconnect()
    
    def is_authenticated(self):
        """Check if user has valid session"""
        return self.load_session()
    
    def logout(self):
        """Clear authentication session"""
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
            print("✅ Logged out successfully!")
        else:
            print("ℹ️ No active session found.")


async def main():
    """Main login flow"""
    auth = TelegramAuth()
    
    print("=" * 60)
    print("🎬 CLOUD THEATRE - ADMIN LOGIN")
    print("=" * 60)
    
    # Check existing session
    if auth.is_authenticated():
        choice = input("\n🔄 Continue with existing session? (Y/n): ").strip().lower()
        if choice in {'', 'y', 'yes'}:
            print("\n✅ Authentication verified!")
            return True
        else:
            auth.logout()
    
    # New login
    print("\n📝 Please enter your details:")
    admin_name = input("👤 Admin Name: ").strip()
    
    if not admin_name:
        print("❌ Admin name is required!")
        return False
    
    phone_input = input("📱 Phone Number (without +91): ").strip()
    
    if not phone_input:
        print("❌ Phone number is required!")
        return False
    
    # Authenticate
    success = await auth.login(admin_name, phone_input)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ LOGIN SUCCESSFUL!")
        print("=" * 60)
        print(f"👤 Admin: {auth.admin_name}")
        print(f"📱 Phone: {auth.phone}")
        print(f"⏰ Session valid for: {SESSION_VALIDITY_HOURS} hours")
        print("=" * 60)
        return True
    else:
        print("\n❌ Login failed. Please try again.")
        return False


if __name__ == "__main__":
    asyncio.run(main())
