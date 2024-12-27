import pytesseract
import pyautogui
import cv2
import time
import datetime
import winsound
import pyfiglet

def print_startup_message():
    # Generate ASCII art for "Marshy"
    ascii_art = pyfiglet.figlet_format(" Made by Marshy!")
    print("\nStarting up...\n")
    time.sleep(1)  # Simulate a small delay
    print(ascii_art)
    time.sleep(1)  # Pause for effect
    print("Thanks for Downloading!\n")

# Main script starts here
if __name__ == "__main__":
    print_startup_message()

# Path to tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def capture_chat_area(region=None):

    screenshot_path = "Captured_image.png"  # Use the same filename + to overwrite file
    screenshot = pyautogui.screenshot(region=region)  # Area where text is detected
    screenshot.save(screenshot_path)
    
    
    winsound.Beep(100, 100)  # Beeping to notify when a screen shot is taken
    
    # Screenshot notifaction in console when taken
    print(f"New screenshot saved (overwritten): {screenshot_path}")
    
    return screenshot_path

def preprocess_image(image):
    
    #PROCESS THE IMAGE

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply binary thresholding to improve contrast
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    
    return thresh

def get_new_player_username(screenshot_path):

    #Grab the username

    image = cv2.imread(screenshot_path)
    
    # Preprocess the image
    processed_image = preprocess_image(image)
    
    # Use Tesseract to extract text from the processed image
    text = pytesseract.image_to_string(processed_image)
    
    # Print the detected text for debugging purposes
    print("Detected text from screenshot:")
    print(text)
    
    for line in text.splitlines():
        if "NEW" in line:  # Look for NEW
            parts = line.split()
            if "NEW" in parts:
                index = parts.index("NEW")
                if index + 1 < len(parts):
                    return parts[index + 1]
    return None

def send_welcome_message(username):
    
    # open chat and send message 

    message = f"Welcome to CosmosMC {username}! Hope you have a good time and feel free to ask any questions! Use /help to get started. :D"
    print(f"Sending message: {message}")  # Debug: Print the message
    pyautogui.press('t')  # Open chat by pressing T
    time.sleep(0.2)  # Small delay to ensure chat opens
    pyautogui.write(message, interval=0.05)  # Type the message
    pyautogui.press('enter')  # Send message

# Main function
def main():
    chat_region = (10, 800, 600, 150)  # Define the region for the chat
    last_username = None
    
    try:
        while True:
            screenshot_path = capture_chat_area(region=chat_region)
            username = get_new_player_username(screenshot_path)
            if username and username != last_username:
                print(f"Detected new player: {username}")
                send_welcome_message(username)
                last_username = username
                time.sleep(10)  # Wait to avoid duplicates
            time.sleep(1)  # Check every second for new players
    except KeyboardInterrupt:
        print("\nScript stopped manually. Exiting...")

if __name__ == "__main__":
    main()
