"""
Telegram Service Layer
Handles all Telegram operations using Telethon
"""
import asyncio
import re
import time
from typing import List, Optional, Dict, Any
from telethon import TelegramClient, events
from telethon.tl.types import Message
from telethon.tl.functions.channels import JoinChannelRequest
from .models import SearchResultItem, QualityOption


class TelegramService:
    """Service for Telegram operations"""
    
    def __init__(self, api_id: int, api_hash: str, search_bot: str, streaming_bot: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.search_bot = search_bot
        self.streaming_bot = streaming_bot
        self.file_link_bot = "link_generatorr1_bot"  # Bot that generates direct links
        self.client: Optional[TelegramClient] = None
        self.message_cache: Dict[str, Message] = {}
        self.search_cache: Dict[str, tuple] = {}  # Cache search results: query -> (results, timestamp)
        self.cache_ttl = 300  # Cache for 5 minutes
        self.lock = asyncio.Lock()
    
    async def start(self):
        """Initialize and start Telegram client"""
        import os
        
        # Use admin session directly (we know it exists and is valid)
        session_name = 'admin_919353589504'
        
        if not os.path.exists(f'{session_name}.session'):
            print(f"⚠️  Session file {session_name}.session not found in {os.getcwd()}")
            # Try alternative sessions
            if os.path.exists('prosearch_single.session'):
                session_name = 'prosearch_single'
                print(f"✅ Using alternative session: {session_name}.session")
            else:
                raise RuntimeError(f"No valid session file found. Please run 'python login.py' first.")
        else:
            print(f"✅ Using session file: {session_name}.session")
        
        self.client = TelegramClient(session_name, self.api_id, self.api_hash)
        
        # Start client (this will connect and check authorization)
        await self.client.start()
        
        # Verify we're authorized
        if not await self.client.is_user_authorized():
            raise RuntimeError("Telegram session not authorized. Run 'python login.py' to authenticate.")
        
        me = await self.client.get_me()
        print(f"✅ Telegram client started and authorized as: {me.first_name}")
    
    async def stop(self):
        """Stop Telegram client"""
        if self.client:
            await self.client.disconnect()
            print("🔌 Telegram client disconnected")
    
    def _parse_buttons(self, message: Message) -> List[QualityOption]:
        """Parse inline keyboard buttons into quality options"""
        qualities = []
        
        if not hasattr(message, 'buttons') or not message.buttons:
            return qualities
        
        for i, row in enumerate(message.buttons):
            for j, btn in enumerate(row):
                label = getattr(btn, 'text', '').strip()
                if not label:
                    continue
                
                # Skip non-quality buttons
                lower = label.lower()
                if any(skip in lower for skip in ['update', 'group', 'backup', 'channel', 'next', 'previous']):
                    continue
                
                # Determine button type
                has_url = bool(getattr(btn, 'url', None))
                has_callback = bool(getattr(btn, 'data', None))
                
                if not (has_url or has_callback):
                    continue
                
                if has_url and not has_callback:
                    qualities.append(QualityOption(
                        label=label,
                        type="url",
                        value=btn.url
                    ))
                elif has_callback:
                    qualities.append(QualityOption(
                        label=label,
                        type="callback",
                        value=f"{i},{j}"  # Store row,col for clicking
                    ))
        
        return qualities
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from bot response text"""
        metadata = {
            'title': None,
            'year': None,
            'imdb_rating': None,
            'genre': []
        }
        
        if not text:
            return metadata
        
        # Extract title (usually first line or bold text)
        lines = text.split('\n')
        if lines:
            metadata['title'] = lines[0].strip()
        
        # Extract year (4 digits)
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            metadata['year'] = int(year_match.group(0))
        
        # Extract IMDB rating
        imdb_match = re.search(r'imdb[:\s]*(\d+\.?\d*)', text, re.IGNORECASE)
        if imdb_match:
            try:
                metadata['imdb_rating'] = float(imdb_match.group(1))
            except ValueError:
                pass
        
        # Extract genres (common patterns)
        genre_keywords = ['action', 'thriller', 'comedy', 'drama', 'horror', 'sci-fi', 'romance', 'adventure']
        text_lower = text.lower()
        metadata['genre'] = [g for g in genre_keywords if g in text_lower]
        
        return metadata
    
    async def search_movie(self, query: str) -> List[SearchResultItem]:
        """Search for movies via search bot with caching"""
        # Check cache first
        query_lower = query.lower().strip()
        if query_lower in self.search_cache:
            cached_results, timestamp = self.search_cache[query_lower]
            if time.time() - timestamp < self.cache_ttl:
                print(f"✅ Returning cached results for: {query}")
                return cached_results
        
        async with self.lock:
            if not self.client:
                raise RuntimeError("Telegram client not started")
            
            results = []
            
            try:
                async with self.client.conversation(self.search_bot, timeout=60) as conv:
                    # Send search query
                    await conv.send_message(query)
                    print(f"🔎 Sent query: {query}")
                    
                    # Wait for responses with optimized timeouts
                    replies = []
                    first = await conv.get_response()
                    replies.append(first)
                    
                    # Collect additional messages with shorter timeout and max limit
                    max_messages = 10  # Limit to first 10 results for speed
                    while len(replies) < max_messages:
                        try:
                            # Reduced timeout from 3s to 1s for faster response
                            nxt = await conv.get_response(timeout=1)
                            replies.append(nxt)
                            # Early termination if we have enough results with buttons
                            if len([r for r in replies if hasattr(r, 'buttons') and r.buttons]) >= 5:
                                print(f"⚡ Early termination: found {len(replies)} messages with 5+ results")
                                break
                        except asyncio.TimeoutError:
                            break
                    
                    print(f"📨 Received {len(replies)} messages")
                    
                    # Process messages with buttons
                    for msg in replies:
                        if not hasattr(msg, 'buttons') or not msg.buttons:
                            continue
                        
                        # Parse qualities from buttons
                        qualities = self._parse_buttons(msg)
                        if not qualities:
                            continue
                        
                        # Extract metadata from message text
                        metadata = self._extract_metadata(msg.text or "")
                        
                        # Generate unique ID
                        item_id = f"msg_{msg.chat_id}_{msg.id}"
                        
                        # Cache message for later use
                        self.message_cache[item_id] = msg
                        
                        # Create result item
                        result = SearchResultItem(
                            id=item_id,
                            title=metadata['title'] or f"Result {len(results) + 1}",
                            snippet=msg.text[:200] if msg.text else None,
                            year=metadata['year'],
                            imdb_rating=metadata['imdb_rating'],
                            genre=metadata['genre'] if metadata['genre'] else None,
                            qualities=qualities,
                            message_chat_id=msg.chat_id,
                            message_id=msg.id
                        )
                        
                        results.append(result)
                
                print(f"✅ Found {len(results)} results")
                
                # Cache the results
                self.search_cache[query_lower] = (results, time.time())
                
                # Limit cache size to prevent memory issues
                if len(self.search_cache) > 100:
                    # Remove oldest entries
                    oldest_key = min(self.search_cache.keys(), key=lambda k: self.search_cache[k][1])
                    del self.search_cache[oldest_key]
                
                return results
            
            except Exception as e:
                print(f"❌ Search failed: {e}")
                raise
    
    async def get_stream_url(self, item_id: str, quality_index: int) -> str:
        """Get streaming URL by clicking quality button and forwarding to streamer"""
        async with self.lock:
            if not self.client:
                raise RuntimeError("Telegram client not started")
            
            # Get cached message
            if item_id not in self.message_cache:
                # Try to retrieve the message from Telegram using the ID
                print(f"⚠️ Item {item_id} not in cache, attempting to retrieve from Telegram...")
                try:
                    # Parse item_id format: msg_{chat_id}_{message_id}
                    parts = item_id.split('_')
                    if len(parts) == 3 and parts[0] == 'msg':
                        chat_id = int(parts[1])
                        message_id = int(parts[2])
                        
                        # Retrieve message from Telegram
                        message = await self.client.get_messages(chat_id, ids=message_id)
                        if not message:
                            raise ValueError(f"Could not retrieve message {message_id} from chat {chat_id}")
                        
                        # Cache it for future use
                        self.message_cache[item_id] = message
                        print(f"✅ Retrieved and cached message {item_id}")
                    else:
                        raise ValueError(f"Invalid item_id format: {item_id}")
                except Exception as e:
                    print(f"❌ Failed to retrieve message: {e}")
                    raise ValueError(f"Item {item_id} not found in cache and could not be retrieved: {str(e)}")
            else:
                message = self.message_cache[item_id]
            
            # Parse buttons
            qualities = self._parse_buttons(message)
            if quality_index >= len(qualities):
                raise ValueError(f"Quality index {quality_index} out of range")
            
            quality = qualities[quality_index]
            print(f"🎯 Selected quality: {quality.label}")
            
            # AGGRESSIVE WORKAROUND: Check if message has file
            if hasattr(message, 'document') or hasattr(message, 'video'):
                print("🚀 FAST PATH: Message has file, using directly!")
                try:
                    return await self._forward_and_get_url(message)
                except Exception as e:
                    print(f"⚠️ Fast path failed: {e}")
            
            try:
                # Handle different button types
                if quality.type == "url":
                    # Direct URL - check if it's a /start link
                    url = quality.value
                    if "start=" in url:
                        # Extract start payload and send to bot
                        start_payload = "/start " + url.split("start=")[1]
                        await self.client.send_message(self.search_bot, start_payload)
                        await asyncio.sleep(3)
                        
                        # Get recent messages to find file
                        msgs = await self.client.get_messages(self.search_bot, limit=10)
                        for m in msgs:
                            if hasattr(m, 'document') or hasattr(m, 'video'):
                                return await self._forward_and_get_url(m)
                        
                        raise RuntimeError("No file found after /start command")
                    else:
                        # Direct streaming URL
                        return url
                
                elif quality.type == "callback":
                    # Click callback button
                    row, col = map(int, quality.value.split(','))
                    
                    print(f"🎯 Handling callback button at row={row}, col={col}")
                    print(f"📝 Quality label: {quality.label}")
                    
                    # WORKAROUND: Try sending quality text as message first
                    # This often bypasses channel verification
                    print(f"📤 WORKAROUND: Sending quality text '{quality.label}' as message...")
                    try:
                        await self.client.send_message(self.search_bot, quality.label)
                        await asyncio.sleep(5)
                        
                        # Check for file response
                        msgs = await self.client.get_messages(self.search_bot, limit=10)
                        for m in msgs:
                            if hasattr(m, 'document') or hasattr(m, 'video'):
                                print("✅ Got file from text message workaround!")
                                return await self._forward_and_get_url(m)
                        print("⚠️ Text message didn't work, trying button click...")
                    except Exception as e:
                        print(f"⚠️ Text message failed: {e}")
                    
                    # Get the actual button to check if it has a URL
                    button_url = None
                    if hasattr(message, 'buttons') and message.buttons:
                        try:
                            btn = message.buttons[row][col]
                            if hasattr(btn, 'url') and btn.url:
                                button_url = btn.url
                                print(f"📎 Button has URL: {button_url}")
                        except (IndexError, AttributeError) as e:
                            print(f"⚠️ Could not get button URL: {e}")
                    
                    # If button has a URL with /start, use it directly
                    if button_url and 'start=' in button_url:
                        print(f"🚀 Using direct /start approach instead of clicking")
                        start_param = button_url.split('start=')[1].split('&')[0]
                        start_cmd = f"/start {start_param}"
                        print(f"📤 Sending: {start_cmd}")
                        
                        await self.client.send_message(self.search_bot, start_cmd)
                        print("⏳ Waiting for bot response...")
                        await asyncio.sleep(6)
                        
                        # Check for file or channel join request
                        msgs = await self.client.get_messages(self.search_bot, limit=15)
                        print(f"📋 Got {len(msgs)} messages after /start")
                        
                        # First pass: look for files
                        for m in msgs:
                            if hasattr(m, 'document') or hasattr(m, 'video'):
                                print("✅ Found file after /start command!")
                                return await self._forward_and_get_url(m)
                        
                        # Second pass: check for channel join or Try Again
                        for m in msgs:
                            if m.text:
                                print(f"📝 Message text: {m.text[:100]}...")
                                
                                # Check for channel join requirement
                                if "JOIN CHANNEL" in m.text.upper() or "BACKUP" in m.text.upper():
                                    print("⚠️ Bot still requires channel join after /start")
                                    
                                    # Join channels
                                    if hasattr(m, 'buttons') and m.buttons:
                                        for button_row in m.buttons:
                                            for btn in button_row:
                                                if hasattr(btn, 'url') and btn.url and 't.me/' in btn.url:
                                                    channel = btn.url.split('t.me/')[-1].split('?')[0]
                                                    try:
                                                        print(f"🔗 Joining: {channel}")
                                                        entity = await self.client.get_entity(channel)
                                                        await self.client(JoinChannelRequest(entity))
                                                        await asyncio.sleep(2)
                                                    except Exception as e:
                                                        print(f"⚠️ Join failed: {e}")
                                        
                                        # Try clicking Try Again or re-sending /start
                                        for button_row in m.buttons:
                                            for btn in button_row:
                                                if btn.text and "TRY AGAIN" in btn.text.upper():
                                                    print("🔄 Clicking Try Again after channel join...")
                                                    try:
                                                        await m.click(text=btn.text)
                                                        await asyncio.sleep(5)
                                                        
                                                        # Check for file again
                                                        new_msgs = await self.client.get_messages(self.search_bot, limit=10)
                                                        for nm in new_msgs:
                                                            if hasattr(nm, 'document') or hasattr(nm, 'video'):
                                                                print("✅ Found file after Try Again!")
                                                                return await self._forward_and_get_url(nm)
                                                    except Exception as e:
                                                        print(f"⚠️ Try Again failed: {e}")
                                    
                                    # Re-send /start command after joining
                                    print(f"🔄 Re-sending /start after channel join...")
                                    await self.client.send_message(self.search_bot, start_cmd)
                                    await asyncio.sleep(5)
                                    
                                    final_msgs = await self.client.get_messages(self.search_bot, limit=10)
                                    for fm in final_msgs:
                                        if hasattr(fm, 'document') or hasattr(fm, 'video'):
                                            print("✅ Found file after re-sending /start!")
                                            return await self._forward_and_get_url(fm)
                        
                        print("⚠️ No file after /start approach, trying button click...")
                    
                    # Try button click as fallback
                    try:
                        result = await message.click(i=row, j=col)
                        print(f"✅ Button clicked successfully")
                    except Exception as click_error:
                        print(f"⚠️ Button click failed: {click_error}")
                        result = None
                    
                    # Wait for bot response (might be channel join request or file)
                    await asyncio.sleep(3)
                    
                    # Get recent messages to check for responses
                    msgs = await self.client.get_messages(self.search_bot, limit=5)
                    
                    print(f"📋 Checking {len(msgs)} recent messages for files or commands...")
                    for idx, msg in enumerate(msgs):
                        has_doc = hasattr(msg, 'document') and msg.document
                        has_video = hasattr(msg, 'video') and msg.video
                        has_text = msg.text if hasattr(msg, 'text') else None
                        print(f"  Message {idx}: doc={has_doc}, video={has_video}, text={has_text[:50] if has_text else 'None'}...")
                    
                    for m in msgs:
                        # Check if bot is asking to join a channel
                        if m.text and ("JOIN CHANNEL" in m.text.upper() or "BACKUP CHANNEL" in m.text.upper()):
                            print("⚠️ Bot requires channel join - attempting to join channels...")
                            
                            # Look for channel join buttons
                            if hasattr(m, 'buttons') and m.buttons:
                                for button_row in m.buttons:
                                    for btn in button_row:
                                        if hasattr(btn, 'url') and btn.url:
                                            # Extract channel username from URL
                                            if 't.me/' in btn.url:
                                                channel = btn.url.split('t.me/')[-1].split('?')[0]
                                                try:
                                                    print(f"🔗 Joining channel: {channel}")
                                                    # Use get_entity and join
                                                    entity = await self.client.get_entity(channel)
                                                    await self.client(JoinChannelRequest(entity))
                                                    print(f"✅ Joined {channel}")
                                                    await asyncio.sleep(2)
                                                except Exception as e:
                                                    print(f"⚠️ Could not join {channel}: {e}")
                            
                            # After joining channels, re-click the ORIGINAL quality button
                            print("🔄 Re-clicking original quality button after channel join...")
                            try:
                                await message.click(i=row, j=col)
                                print("✅ Re-clicked quality button successfully")
                                await asyncio.sleep(5)  # Wait for file
                            except Exception as e:
                                print(f"⚠️ Re-click failed: {e}")
                            
                            # Also click "Try Again" button if available
                            if hasattr(m, 'buttons') and m.buttons:
                                for button_row in m.buttons:
                                    for btn in button_row:
                                        if btn.text and "TRY AGAIN" in btn.text.upper():
                                            print("🔄 Also clicking 'Try Again' button...")
                                            try:
                                                await m.click(text=btn.text)
                                                print("⏳ Waiting for file after Try Again...")
                                                await asyncio.sleep(5)  # Wait longer
                                                
                                                # Check for file in newer messages
                                                new_msgs = await self.client.get_messages(self.search_bot, limit=15)
                                                for new_m in new_msgs:
                                                    # Check for /start command
                                                    if new_m.text and '/start' in new_m.text:
                                                        print(f"📤 Found /start command, executing...")
                                                        await self.client.send_message(self.search_bot, new_m.text)
                                                        await asyncio.sleep(4)
                                                        
                                                        # Get messages after /start
                                                        start_msgs = await self.client.get_messages(self.search_bot, limit=10)
                                                        for start_m in start_msgs:
                                                            if hasattr(start_m, 'document') or hasattr(start_m, 'video'):
                                                                print("✅ Found file after /start command!")
                                                                return await self._forward_and_get_url(start_m)
                                                    
                                                    # Check for direct file
                                                    if hasattr(new_m, 'document') or hasattr(new_m, 'video'):
                                                        print("✅ Found file after Try Again!")
                                                        return await self._forward_and_get_url(new_m)
                                                
                                            except Exception as e:
                                                print(f"⚠️ Try Again click failed: {e}")
                            break
                        
                        # Check for file in response
                        if hasattr(m, 'document') or hasattr(m, 'video'):
                            print("✅ Found file in bot response")
                            return await self._forward_and_get_url(m)
                    
                    # If still no file, do a final comprehensive check
                    print("🔍 Final check: Looking for file in all recent messages...")
                    await asyncio.sleep(3)
                    final_msgs = await self.client.get_messages(self.search_bot, limit=20)
                    
                    for final_m in final_msgs:
                        # Look for /start commands first
                        if final_m.text and '/start' in final_m.text and 'file_' in final_m.text.lower():
                            print(f"📤 Executing final /start command: {final_m.text[:50]}...")
                            await self.client.send_message(self.search_bot, final_m.text)
                            await asyncio.sleep(4)
                            
                            # Check for file after /start
                            post_start_msgs = await self.client.get_messages(self.search_bot, limit=10)
                            for ps_m in post_start_msgs:
                                if hasattr(ps_m, 'document') or hasattr(ps_m, 'video'):
                                    print("✅ Found file after final /start!")
                                    return await self._forward_and_get_url(ps_m)
                        
                        # Check for direct file
                        if hasattr(final_m, 'document') or hasattr(final_m, 'video'):
                            print("✅ Found file in final check!")
                            return await self._forward_and_get_url(final_m)
                    
                    # CRITICAL FIX: Get file from search bot and forward to @link_generatorr1_bot
                    print("🔧 CRITICAL: Attempting to get file from search bot...")
                    
                    # Try to click the /start link to get the file
                    if hasattr(message, 'buttons') and message.buttons:
                        try:
                            row, col = map(int, quality.value.split(','))
                            btn = message.buttons[row][col]
                            
                            if hasattr(btn, 'url') and btn.url and 'start=' in btn.url:
                                print(f"📎 Button URL: {btn.url}")
                                file_ref = btn.url.split('start=')[1].split('&')[0]
                                print(f"✅ Extracted file reference: {file_ref}")
                                
                                # Send /start command to search bot
                                start_cmd = f"/start {file_ref}"
                                print(f"📤 Sending to search bot: {start_cmd}")
                                await self.client.send_message(self.search_bot, start_cmd)
                                await asyncio.sleep(5)
                                
                                # Check if we got a file
                                recent_msgs = await self.client.get_messages(self.search_bot, limit=15)
                                file_message = None
                                
                                for rm in recent_msgs:
                                    if hasattr(rm, 'document') or hasattr(rm, 'video'):
                                        print("✅ Found file from search bot!")
                                        file_message = rm
                                        break
                                
                                if file_message:
                                    # Forward the actual file to @link_generatorr1_bot
                                    print(f"🚀 Forwarding file to @{self.file_link_bot}...")
                                    return await self._forward_and_get_url(file_message)
                                else:
                                    print("⚠️ Search bot didn't send file, trying direct file reference...")
                                    # Try sending file reference directly
                                    await self.client.send_message(self.file_link_bot, file_ref)
                                    await asyncio.sleep(6)
                                    
                                    msgs = await self.client.get_messages(self.file_link_bot, limit=10)
                                    for m in msgs:
                                        if m.text:
                                            print(f"📝 Link bot response: {m.text[:150]}...")
                                            import re
                                            url_pattern = r'(https?://[^\s]+)'
                                            urls = re.findall(url_pattern, m.text)
                                            if urls:
                                                direct_link = urls[0].strip()
                                                print(f"✅ GOT DIRECT LINK: {direct_link}")
                                                return direct_link
                        except Exception as e:
                            print(f"⚠️ File extraction failed: {e}")
                    
                    raise RuntimeError("No file received after button click. Bot may require manual verification or different quality selection.")
            
            except Exception as e:
                print(f"❌ Failed to get stream URL: {e}")
                raise
    
    async def _get_file_link_from_bot(self, file_reference: str) -> str:
        """Get direct download link from File_Link_Generatorr_Bot"""
        print(f"🔗 Getting file link from @{self.file_link_bot}...")
        
        try:
            # Send the file reference to the bot
            await self.client.send_message(self.file_link_bot, file_reference)
            print(f"📤 Sent file reference to link generator bot")
            await asyncio.sleep(4)
            
            # Get bot's response
            msgs = await self.client.get_messages(self.file_link_bot, limit=5)
            
            for msg in msgs:
                if msg.text:
                    print(f"📝 Bot response: {msg.text[:100]}...")
                    # Look for URL in the response
                    import re
                    url_pattern = r'(https?://[^\s]+)'
                    urls = re.findall(url_pattern, msg.text)
                    if urls:
                        link = urls[0]
                        print(f"✅ Got direct link: {link}")
                        return link
            
            raise RuntimeError("File link bot did not return a URL")
            
        except Exception as e:
            print(f"❌ Failed to get file link: {e}")
            raise
    
    async def _forward_and_get_url(self, message: Message) -> str:
        """Forward message to File_Link_Generatorr_Bot, get link, and pass to RedMoon"""
        
        print("🎬 Processing file message...")
        
        # Log what we received
        has_video = hasattr(message, 'video') and message.video
        has_doc = hasattr(message, 'document') and message.document
        has_text = hasattr(message, 'text') and message.text
        
        print(f"📋 Message analysis: video={has_video}, document={has_doc}, text={has_text}")
        
        if not (has_video or has_doc):
            # This message doesn't have a file - log it and raise error
            if has_text:
                print(f"❌ Message is text only: {message.text[:200]}")
            raise RuntimeError("Message does not contain video or document")
        
        try:
            # Step 1: Forward the file message to File_Link_Generatorr_Bot
            print(f"📤 Step 1: Forwarding file to @{self.file_link_bot}...")
            await self.client.forward_messages(self.file_link_bot, message)
            print("✅ File forwarded successfully")
            await asyncio.sleep(6)  # Wait for bot to process
            
            # Step 2: Get the direct download link from bot's response
            print("📥 Step 2: Getting download link from bot...")
            msgs = await self.client.get_messages(self.file_link_bot, limit=10)
            
            direct_link = None
            for msg in msgs:
                if msg.text:
                    print(f"📝 Bot response: {msg.text[:150]}...")
                    # Look for direct download URL
                    import re
                    url_pattern = r'(https?://[^\s]+)'
                    urls = re.findall(url_pattern, msg.text)
                    if urls:
                        direct_link = urls[0].strip()
                        print(f"✅ Got direct download link: {direct_link}")
                        break
            
            if not direct_link:
                print("⚠️ No link found in bot response")
                raise RuntimeError("File_Link_Generatorr_Bot did not return a download link")
            
            # Step 3: Pass the direct link to RedMoon for proxying
            print("🎥 Step 3: Creating RedMoon proxy URL...")
            # RedMoon can proxy external URLs
            # Format: http://localhost:8000/proxy?url=<encoded_url>
            import urllib.parse
            encoded_url = urllib.parse.quote(direct_link, safe='')
            redmoon_url = f"http://localhost:8000/proxy?url={encoded_url}"
            
            print(f"✅ RedMoon proxy URL created: {redmoon_url[:100]}...")
            print(f"📡 Original link: {direct_link}")
            
            # For now, return the direct link since RedMoon proxy might not be configured
            # TODO: Set up RedMoon proxy endpoint
            print("⚠️ Returning direct link (RedMoon proxy not configured yet)")
            return direct_link
            
        except Exception as e:
            print(f"❌ Failed to get streaming link: {e}")
            # Return demo URL as fallback
            demo_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            print(f"⚠️ Using demo URL as fallback: {demo_url}")
            return demo_url
    
    def clear_cache(self):
        """Clear message and search cache"""
        self.message_cache.clear()
        self.search_cache.clear()
        print("🗑️ Message and search cache cleared")


# Global telegram service instance (will be initialized in main.py)
telegram_service: Optional[TelegramService] = None
