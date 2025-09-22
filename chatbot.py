import time
import random
import threading
import os
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

os.environ['DISPLAY'] = ':1'
WEBSITE_URL = "http://chatroom2000.de"
MAX_WAIT_TIME = 25

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is alive and running!"
def keep_alive(): app.run(host='0.0.0.0', port=8080)

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--window-size=1280,800")

def generate_random_name():
    random_numbers = random.randint(10, 99)
    name = f"Anna 16 {random_numbers}"
    print(f"[INFO] Generierter Name: {name}")
    return name

def take_screenshot_and_upload(driver, filename_prefix):
    try:
        filename = f"{filename_prefix}_{int(time.time())}.png"
        driver.save_screenshot(filename)
        print(f"[INFO] Screenshot '{filename}' erstellt. Lade hoch...")
        os.system(f"curl --upload-file ./{filename} https://transfer.sh/{filename}")
    except Exception as e:
        print(f"[ERROR] Screenshot oder Upload fehlgeschlagen: {e}")

def handle_cookies(driver, wait):
    print("[+] Schritt 1: Suche nach Cookie-Bannern...")
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Einwilligen')]")))
        cookie_button.click()
        print("[SUCCESS] Cookie-Banner ('Einwilligen') erfolgreich weggeklickt.")
        return True
    except TimeoutException:
        print("[INFO] 'Einwilligen' Button nicht gefunden. Versuche Alternative...")
        try:
            cookie_button_alt = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Alle akzeptieren')]")))
            cookie_button_alt.click()
            print("[SUCCESS] Cookie-Banner ('Alle akzeptieren') erfolgreich weggeklickt.")
            return True
        except TimeoutException:
            print("[WARNUNG] Keiner der bekannten Cookie-Banner wurde gefunden. Mache trotzdem weiter.")
            return True

def perform_login(driver, wait, bot_name):
    print("[+] Schritt 2: Führe Login durch...")
    try:
        nickname_field = wait.until(EC.presence_of_element_located((By.NAME, "nickname")))
        nickname_field.send_keys(bot_name)
        agb_checkbox = wait.until(EC.element_to_be_clickable((By.ID, "tos")))
        agb_checkbox.click()
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='LOS GEHTS!']")))
        login_button.click()
        print("[SUCCESS] Login-Formular abgeschickt.")
        return True
    except Exception as e:
        print(f"[ERROR] Kritisches Element im Login-Formular nicht gefunden: {e}")
        return False

def dismiss_popups(driver, wait):
    print("[+] Schritt 3: Klicke nachfolgende Pop-ups weg...")
    popups = ["Chatregeln", "Unsere Do's", "Probleme-Fenster"]
    for popup_name in popups:
        try:
            print(f"  -> Warte auf Pop-up: '{popup_name}'...")
            button_xpath = "//button[contains(., 'Akzeptieren') or contains(., 'Fertig')]"
            popup_button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            popup_button.click()
            print(f"  -> '{popup_name}' erfolgreich weggeklickt.")
            time.sleep(2)
        except TimeoutException:
            print(f"[WARNUNG] Pop-up '{popup_name}' ist nicht erschienen. Ignoriere.")
    print("[SUCCESS] Alle erwarteten Pop-ups behandelt.")
    return True

def message_loop(driver, wait, bot_name):
    print("[+] Schritt 4: Starte Nachrichtenschleife...")
    while True:
        try:
            message_to_send = f"Hallo! Ich bin's, {bot_name}. Es ist {time.strftime('%H:%M:%S')}."
            message_field = wait.until(EC.presence_of_element_located((By.NAME, "message")))
            message_field.send_keys(message_to_send)
            message_field.send_keys(Keys.RETURN)
            print(f"[SUCCESS] Nachricht gesendet. Warte 60 Sekunden...")
            time.sleep(60)
        except Exception as loop_error:
            print(f"[ERROR] Fehler in der Nachrichtenschleife: {loop_error}")
            return

def start_bot():
    print("\n" + "="*50 + f"\nStarte neuen Bot-Zyklus am {time.strftime('%Y-%m-%d %H:%M:%S')}\n" + "="*50)
    driver = None
    try:
        print("[INFO] Versuche, den Chrome WebDriver zu starten...")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, MAX_WAIT_TIME)
        print("[SUCCESS] WebDriver erfolgreich gestartet.")
        print(f"[INFO] Lade Webseite: {WEBSITE_URL}...")
        driver.get(WEBSITE_URL)
        print("[SUCCESS] Webseite geladen.")
        if not handle_cookies(driver, wait): raise Exception("Fehler bei der Cookie-Behandlung.")
        bot_name = generate_random_name()
        if not perform_login(driver, wait, bot_name): raise Exception("Fehler beim Login-Vorgang.")
        if not dismiss_popups(driver, wait): raise Exception("Fehler beim Wegklicken der Pop-ups.")
        take_screenshot_and_upload(driver, "login_success")
        message_loop(driver, wait, bot_name)
    except Exception as e:
        print("!"*50 + f"\n[FATAL] Ein schwerwiegender, unerwarteter Fehler ist aufgetreten: {e}\n" + "!"*50)
        if driver: take_screenshot_and_upload(driver, "fatal_error")
    finally:
        if driver:
            print("[INFO] Schließe den Browser und räume auf...")
            driver.quit()
        print("[INFO] Bot-Zyklus beendet. Neustart wird vorbereitet.")

if __name__ == "__main__":
    print("[MAIN] Starte den Keep-alive Server in einem Hintergrund-Thread...")
    t = threading.Thread(target=keep_alive)
    t.daemon = True
    t.start()
    print("[MAIN] Starte die Haupt-Bot-Schleife...")
    while True:
        start_bot()
        print(f"[MAIN] Nächster Bot-Start in 15 Sekunden...")
        time.sleep(15)
