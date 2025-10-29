import asyncio
import os
import sys
from telethon import TelegramClient, events
from config import API_ID, API_HASH, SEARCH_BOT_USERNAME, STREAMING_BOT_USERNAME

# Import authentication module
try:
    from login import TelegramAuth
except ImportError:
    print("❌ Error: login.py not found. Please ensure login.py is in the same directory.")
    sys.exit(1)

# Use configuration from config.py
api_id = int(API_ID)
api_hash = API_HASH
bot_username = SEARCH_BOT_USERNAME

# Create a Telegram client session
client = TelegramClient('prosearch_single', api_id, api_hash)

def list_buttons_with_coords(messages):
    items = []
    message_with_buttons = None
    for msg in messages:
        if getattr(msg, "buttons", None):
            message_with_buttons = msg
    if not message_with_buttons:
        return [], None
    for i, row in enumerate(message_with_buttons.buttons):
        for j, btn in enumerate(row):
            label = (getattr(btn, "text", None) or "").strip()
            if not label:
                continue
            lower = label.lower()
            if "update" in lower or "group" in lower or "backup" in lower or "channel" in lower:
                continue
            is_clickable = bool(getattr(btn, "data", None) or getattr(btn, "url", None))
            if not is_clickable:
                continue
            items.append({
                "message": message_with_buttons,
                "i": i,
                "j": j,
                "label": label,
                "has_url": bool(getattr(btn, "url", None)),
                "has_callback": bool(getattr(btn, "data", None)),
            })
    return items, message_with_buttons

async def main():
    # Check authentication before proceeding
    print("=" * 60)
    print("🎬 CLOUD THEATRE - MOVIE SEARCH")
    print("=" * 60)
    
    auth = TelegramAuth()
    if not auth.is_authenticated():
        print("\n🔒 Authentication required!")
        print("Please run 'python login.py' first to authenticate.\n")
        choice = input("Would you like to login now? (Y/n): ").strip().lower()
        if choice in {'', 'y', 'yes'}:
            # Import and run login
            from login import main as login_main
            success = await login_main()
            if not success:
                print("\n❌ Authentication failed. Exiting.")
                return
        else:
            print("\n❌ Authentication required. Exiting.")
            return
    
    print(f"\n✅ Authenticated as: {auth.admin_name}")
    print(f"📱 Phone: {auth.phone}")
    print("=" * 60 + "\n")
    
    await client.start()
    print("✅ Client started.")
    
    # Ask user for the username to forward files to
    # Default to streaming bot if configured, otherwise ask user
    if STREAMING_BOT_USERNAME:
        use_default = input(f"Forward files to streaming bot ({STREAMING_BOT_USERNAME})? (Y/n): ").strip().lower()
        if use_default in {'', 'y', 'yes'}:
            forward_username = STREAMING_BOT_USERNAME
            if not forward_username.startswith('@'):
                forward_username = '@' + forward_username
            print(f"📤 Files will be forwarded to streaming bot: {forward_username}")
        else:
            forward_username = input("Enter username to forward files to (e.g., @username or username): ").strip()
            if not forward_username.startswith('@'):
                forward_username = '@' + forward_username
            print(f"📤 Files will be forwarded to: {forward_username}")
    else:
        forward_username = input("Enter username to forward files to (e.g., @username or username): ").strip()
        if not forward_username.startswith('@'):
            forward_username = '@' + forward_username
        print(f"📤 Files will be forwarded to: {forward_username}")

    while True:
        user_input = input("\nEnter movie name (or 'q' to quit): ").strip()
        if user_input.lower() in {"q", "quit", "exit"}:
            print("👋 Exiting.")
            break
        
        query = user_input or "Inception"
        print(f"🔎 Searching: {query}")

        try:
            async with client.conversation(bot_username, timeout=120) as conv:
                await conv.send_message(query)
                print("⏳ Waiting for bot response...")

                replies = []
                first = await conv.get_response()
                replies.append(first)
                
                while True:
                    try:
                        nxt = await conv.get_response(timeout=4)
                        replies.append(nxt)
                    except asyncio.TimeoutError:
                        break

                print("\n🎬 Bot's Response:\n")
                aggregated = "\n\n".join((m.text or "").strip() for m in replies if (m.text or "").strip())
                print(aggregated)

                buttons, _ = list_buttons_with_coords(replies)
                if buttons:
                    print("\n🎛️ Button options (enter index to click, 'q' to quit):")
                    for idx, item in enumerate(buttons, 1):
                        kind = "URL" if item["has_url"] and not item["has_callback"] else ("CB" if item["has_callback"] else "BTN")
                        print(f"{idx:2d}. [{kind}] {item['label']}")
                else:
                    print("\nℹ️ No button options found in the first response page.")

                while buttons:
                    choice = input("\nSelect button index, 's' for new search, or 'q' to quit: ").strip().lower()
                    if choice in {"q", "quit", "exit"}:
                        print("👋 Exiting.")
                        await client.disconnect()
                        print("\n🔌 Disconnected.")
                        return
                    if choice in {"s", "search", "new"}:
                        print("🔍 Starting new search...")
                        break
                    if not choice.isdigit():
                        print("Please enter a valid number.")
                        continue
                    
                    sel = int(choice) - 1
                    if sel < 0 or sel >= len(buttons):
                        print("Index out of range. Try again.")
                        continue

                    target = buttons[sel]
                    print(f"🎯 Clicking button: {target['label']}")
                    if target["has_url"] and not target["has_callback"]:
                        print("This is a URL button; opening URLs is not supported via the API. Choose a callback option.")
                        continue

                    try:
                        result = await target["message"].click(i=target["i"], j=target["j"])
                        print(f"✅ Click sent successfully: {result}")
                        
                        # Handle URL -> /start flow
                        if hasattr(result, 'url') and result.url:
                            url = result.url
                            print(f"🔗 Bot provided URL: {url}")
                            if "start=" in url:
                                start_payload = "/start " + url.split("start=")[1]
                                print(f"   Command: {start_payload}")
                                await client.send_message(bot_username, start_payload)
                                await asyncio.sleep(5)
                                msgs = await client.get_messages(bot_username, limit=10)
                                sent = False
                                for m in msgs:
                                    if getattr(m, "document", None) or getattr(m, "video", None) or getattr(m, "audio", None):
                                        try:
                                            print(f"📤 Forwarding file to {forward_username}...")
                                            await client.forward_messages(forward_username, m)
                                            print("✅ File forwarded successfully!")
                                            sent = True
                                            buttons = []
                                            break
                                        except Exception as fwd_err:
                                            print(f"⚠️ Failed to forward file: {fwd_err}")
                                if not sent:
                                    print("   No file found in recent messages.")
                            continue
                    except Exception as e:
                        print(f"⚠️ Click failed: {e}")
                        continue

                    # Pagination: NEXT edits the same message (only for callback buttons)
                    is_next = (
                        target["has_callback"]
                        and not target["has_url"]
                        and ("next" in target["label"].lower() or "⏩" in target["label"])
                    )
                    if is_next:
                        try:
                            print("⏳ Waiting for pagination...")
                            edited_event = await conv.wait_event(events.MessageEdited(chats=bot_username), timeout=10)
                            if (hasattr(edited_event, "message") and 
                                getattr(edited_event.message, "id", None) == target["message"].id):
                                current_button_message = edited_event.message
                                buttons, _ = list_buttons_with_coords([current_button_message])
                                if buttons:
                                    print("\n🔁 Updated options:")
                                    for idx, item in enumerate(buttons, 1):
                                        print(f"{idx:2d}. {item['label']}")
                                    continue
                                else:
                                    print("No further options available.")
                                    break
                            else:
                                print("Pagination failed - message not edited as expected.")
                                break
                        except asyncio.TimeoutError:
                            print("No pagination response received.")
                            try:
                                refreshed = await client.get_messages(bot_username, ids=target["message"].id)
                                if getattr(refreshed, "buttons", None) is not None and str(refreshed.buttons) != str(target["message"].buttons):
                                    buttons, _ = list_buttons_with_coords([refreshed])
                                    if buttons:
                                        print("\n🔁 Updated options (refreshed):")
                                        for idx, item in enumerate(buttons, 1):
                                            print(f"{idx:2d}. {item['label']}")
                                        continue
                            except Exception:
                                pass
                            break
                        continue

                    # Otherwise, wait for new message (file card or text)
                    try:
                        resp = await conv.get_response(timeout=10)
                        if getattr(resp, "document", None) or getattr(resp, "video", None) or getattr(resp, "audio", None):
                            try:
                                print(f"📤 Forwarding file to {forward_username}...")
                                await client.forward_messages(forward_username, resp)
                                print("✅ File forwarded successfully!")
                                buttons = []
                                break
                            except Exception as fwd_err:
                                print(f"⚠️ Failed to forward file: {fwd_err}")
                                continue
                        if resp.text and resp.text.strip():
                            print(resp.text.strip())
                            continue
                    except asyncio.TimeoutError:
                        print("No response received after click.")
                        continue

        except asyncio.TimeoutError:
            print("⚠️ Timed out waiting for the bot's response. Try again.")

    # Cleanly disconnect after the search loop ends
    await client.disconnect()
    print("\n🔌 Disconnected.")

# Run the async function
asyncio.run(main())
