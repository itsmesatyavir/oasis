import websocket
import json
import threading
import time
from colorama import Fore, Style, init

# Initialize colorama for bright colors
init(autoreset=True)

# Branding
BRAND_NAME = Fore.CYAN + "FORESTARMY" + Style.RESET_ALL
AUTHOR = Fore.CYAN + "Proudly Made By Itsmesatyavir" + Style.RESET_ALL
BRIGHT_GREEN = Fore.LIGHTGREEN_EX
BRIGHT_YELLOW = Fore.LIGHTYELLOW_EX
BRIGHT_RED = Fore.LIGHTRED_EX

# Read tokens from family.txt
def load_tokens():
    try:
        with open("family.txt", "r") as file:
            tokens = [line.strip() for line in file.readlines() if line.strip()]
            if not tokens:
                print(f"{BRIGHT_RED}❌ No tokens found in family.txt!{Style.RESET_ALL}")
                exit(1)
            return tokens
    except FileNotFoundError:
        print(f"{BRIGHT_RED}❌ family.txt not found!{Style.RESET_ALL}")
        exit(1)

# Load tokens
TOKENS = load_tokens()
current_token_index = 0

def get_next_token():
    """Rotates to the next token in case of failure."""
    global current_token_index
    current_token_index = (current_token_index + 1) % len(TOKENS)
    return TOKENS[current_token_index]

# Global variable for tracking points
latest_points = "Loading..."

def connect_websocket():
    """Handles WebSocket connection with auto-retry on failure."""
    global latest_points
    token = get_next_token()
    ws_url = f"wss://ws.distribute.ai/?token={token}&version=0.1.23&platform=extension&lastConnectionId="

    def on_message(ws, message):
        """Handles incoming WebSocket messages."""
        global latest_points
        try:
            data = json.loads(message)
            print(f"\n📩 {BRIGHT_GREEN}Raw Data Received:{Style.RESET_ALL} {json.dumps(data, indent=2)}")

            if data.get("type") == "init":
                name = data["data"].get("name", "Unknown")
                print(f"✅ Connected as: {BRIGHT_YELLOW}{name}{Style.RESET_ALL}")

            if data.get("data") and "points" in data["data"]:
                latest_points = data["data"]["points"]

            print(f"🌟 Total Points: {BRIGHT_YELLOW}{latest_points}{Style.RESET_ALL}")

        except json.JSONDecodeError:
            print(f"{BRIGHT_RED}❌ Failed to parse JSON response.{Style.RESET_ALL}")

    def on_error(ws, error):
        """Handles WebSocket errors."""
        print(f"{BRIGHT_RED}❌ WebSocket Error: {error}{Style.RESET_ALL}")

    def on_close(ws, close_status_code, close_msg):
        """Handles WebSocket closure and attempts reconnection."""
        print(f"{BRIGHT_RED}🔴 WebSocket Closed. Switching Token...{Style.RESET_ALL}")
        time.sleep(5)
        connect_websocket()

    def on_open(ws):
        """Handles WebSocket connection."""
        print(f"\n{BRAND_NAME} | {AUTHOR}")
        print(f"{BRIGHT_GREEN}🔗 WebSocket Connected!{Style.RESET_ALL}")

        def send_ping():
            """Sends a ping every 20 seconds."""
            while True:
                try:
                    ws.send(json.dumps({"type": "ping"}))
                    print(f"\n📡 {BRIGHT_GREEN}Sent Ping (every 20 sec){Style.RESET_ALL}")
                    print(f"🌟 Total Points: {BRIGHT_YELLOW}{latest_points}{Style.RESET_ALL}")
                    time.sleep(20)
                except websocket.WebSocketConnectionClosedException:
                    print(f"{BRIGHT_RED}❌ Connection closed. Stopping ping.{Style.RESET_ALL}")
                    break

        threading.Thread(target=send_ping, daemon=True).start()

    # Start WebSocket connection
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

# Start WebSocket connection
connect_websocket()
