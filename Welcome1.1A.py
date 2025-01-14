import os
import subprocess
import sys
import time
import pyautogui
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import pygetwindow as gw
from pathlib import Path
import pyfiglet
import re
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def install_packages():
    """Install required packages if they are not already installed."""
    required_packages = [
        "pyautogui",
        "transformers",
        "pygetwindow",
        "pyfiglet"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            logging.info(f"Installing package: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

def print_startup_message():
    """Print the startup message with ASCII art."""
    ascii_art = pyfiglet.figlet_format("Made by Todd!")
    logging.info("Starting up...")
    time.sleep(1)
    print(ascii_art)
    time.sleep(1)
    logging.info("Thanks for Downloading!")

def find_lunar_log():
    """Find the most recent log file for Lunar Client."""
    base_path = Path.home() / ".lunarclient" / "logs" / "game"
    if not base_path.exists():
        logging.error("Lunar Client log path not found.")
        return None

    log_files = list(base_path.glob("*.log"))
    if not log_files:
        logging.error("No Lunar Client log files found.")
        return None

    most_recent_log = max(log_files, key=os.path.getmtime)
    return str(most_recent_log)

def find_minecraft_log():
    """Find the most recent log file for regular Minecraft."""
    base_path = Path.home() / "AppData" / "Roaming" / ".minecraft" / "logs"

    if not base_path.exists():
        logging.error("Minecraft log path not found.")
        return None

    log_files = list(base_path.glob("*.log"))
    if not log_files:
        logging.error("No Minecraft log files found.")
        return None

    most_recent_log = max(log_files, key=os.path.getmtime)
    return str(most_recent_log)

def get_active_log_file():
    """Detect which log file is active by comparing modification times."""
    lunar_log = find_lunar_log()
    minecraft_log = find_minecraft_log()
    
    if not lunar_log and not minecraft_log:
        logging.error("No log files found.")
        return None

    try:
        lunar_update_time = os.path.getmtime(lunar_log) if lunar_log else 0
        minecraft_update_time = os.path.getmtime(minecraft_log) if minecraft_log else 0
        
        if lunar_update_time > minecraft_update_time:
            return lunar_log
        elif minecraft_update_time > lunar_update_time:
            return minecraft_log
    except FileNotFoundError:
        pass  
    
    return None

def monitor_log_file(log_file_path):
    """Monitor the log file for the wake word and extract the question."""
    wake_word = "mbot"
    last_question = None
    with open(log_file_path, "r", encoding="utf-8", errors="ignore") as log_file:
        log_file.seek(0, 2)  
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(0.1)  
                continue
            if wake_word in line:
                try:
                    question = line.split(wake_word, 1)[1].strip()
                    if question != last_question:
                        last_question = question
                        yield question
                except IndexError:
                    continue

def generate_response(question):
    """Generate a response using BlenderBot or predefined responses."""
    predefined_responses = {
        "background": "I am an AI assistant created by Marshy. I use BlenderBot for generating responses.",
        "creator": "I was created by Marshy.",
        "purpose": "I am here to assist you with your queries and provide helpful information.",
        "name": "I am known as Mbot, a friendly AI assistant for cosmos!.",
        "2 + 2": "The answer to 2 + 2 is 4.",
    }

    for keyword, response in predefined_responses.items():
        if keyword in question.lower():
            return response

    # If no predefined response matches, use BlenderBot
    tokenizer = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-600M-distill")
    model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-600M-distill")
    
    inputs = tokenizer(question, return_tensors="pt")
    reply_ids = model.generate(**inputs)
    response = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
    return response

def is_minecraft_active():
    """Check if a Minecraft client is the active window."""
    active_window = gw.getActiveWindow()
    if active_window:
        return "minecraft" in active_window.title.lower() or "lunar" in active_window.title.lower()
    return False

def send_response(response):
    """Simulate keyboard input to send a message in Minecraft."""
    wait_time = 0
    while not is_minecraft_active():
        if wait_time >= 60:  
            logging.error("Minecraft is not active. Cannot send the message.")
            return
        time.sleep(1)  
        wait_time += 1
    pyautogui.press("t")  
    time.sleep(0.5)
    pyautogui.typewrite(response)
    pyautogui.press("enter")

def monitor_chat(log_file_path, stop_event):
    """Monitor the chat for the keyword 'NEW' followed by a username."""
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
            log_file.seek(0, os.SEEK_END)  # Move to the end of the file
            while not stop_event.is_set():
                line = log_file.readline()
                if not line:
                    time.sleep(0.1)  # Sleep briefly to avoid busy-waiting
                    continue

                match = re.search(r'\[CHAT\] \+ NEW (\w+)', line)
                if match:
                    username = match.group(1)
                    send_welcome_message(username)
    except FileNotFoundError:
        logging.error(f"Log file not found: {log_file_path}")
    except Exception as e:
        logging.error(f"Error while monitoring chat: {e}")

def send_welcome_message(username):
    """Send a welcome message to the chat."""
    message = f"welcome to cosmos {username} if you need help or anything just ask!"
    pyautogui.press('t')  
    time.sleep(0.5)  
    pyautogui.typewrite(message)
    pyautogui.press('enter')

def listen_for_quit(stop_event):
    """Listen for 'quit' command in the terminal to stop the script."""
    while not stop_event.is_set():
        user_input = input()
        if user_input.lower() == "quit":
            stop_event.set()

if __name__ == "__main__":
    print_startup_message()
    
    active_log = get_active_log_file()
    if not active_log:
        logging.error("No active log file detected. Exiting.")
        exit()

    logging.info(f"Monitoring log file: {active_log}")

    last_response = None
    stop_event = threading.Event()
    threading.Thread(target=monitor_chat, args=(active_log, stop_event)).start()
    threading.Thread(target=listen_for_quit, args=(stop_event,)).start()

    for question in monitor_log_file(active_log):
        logging.info(f"Question detected: {question}")
        response = generate_response(question)
        logging.info(f"Generated response: {response}")
        if response != last_response:
            send_response(response)
            last_response = response
