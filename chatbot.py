import time
import random
import threading
import os
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service  # <-- WICHTIGER, NEUER IMPORT
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

# === GRUNDEINSTELLUNGEN ===
WEBSITE_URL = "http://chatroom2000.de"
MAX_WAIT_TIME = 25
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"  # <-- WIR DEFINIEREN DEN PFAD

# === FLASK APP (UNVERÄNDERT) ===
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is alive and running!"
def keep_alive(): app.run(host='0.0.0.0', port=8080)

# === CHROME OPTIONS FÜR HEADLESS ===
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1280,800")
chrome_options.add_argument("--disable-gpu") # Eine zusätzliche Option zur Stabilitätsverbesserung

# (Der Rest des Codes bleibt identisch, nur der Start des WebDrivers wird geändert)
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
        cookie_button.click(); print("[SUCCESS] Cookie-Banner ('Einwilligen') geklickt.")
        return True
    except TimeoutException:
        print("[INFO] 'Einwilligen' nicht gefunden. Versuche Alternative...")
        try:
            cookie_button_alt = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Alle akzeptieren')]")))
            cookie_button_alt.click(); print("[SUCCESS] Cookie-Banner ('Alle akzeptieren') geklickt.")
            return True
        except TimeoutException:
            print("[WARNUNG] Keinen Cookie-Banner gefunden. Mache weiter.")
            return True

def perform_login(driver, wait, bot_name):
    print("[+] Schritt 2: Führe Login durch...")
    try:
        nickname_field = wait.until(EC.presence_of_element_located((By.NAME, "nickname"))); nickname_field.send_keys(bot_name)
        agb_checkbox = wait.until(EC.element_to_be_clickable((By.ID, "tos"))); agb_checkbox.click()
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='LOS GEHTS!']"))); login_button.click()
        print("[SUCCESS] Login-Formular abgeschickt.")
        return True
    except Exception as e:
        print(f"[ERROR] Kritisches Element im Login-Formular nicht gefunden: {e}"); return False

def dismiss_popups(driver, wait):
    print("[+] Schritt 3: Klicke Pop-ups weg...")
    for popup_name in ["Chatregeln", "Unsere Do's", "Probleme-Fenster"]:
        try:
            print(f"  -> Warte auf Pop-up: '{popup_name}'...")
            button_xpath = "//button[contains(., 'Akzeptieren') or contains(., 'Fertig')]"
            popup_button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath))); popup_button.click()
            print(f"  -> '{popup_name}' weggeklickt.")
            time.sleep(2)
        except TimeoutException:
            print(f"[WARNUNG] Pop-up '{popup_name}' nicht erschienen.")
    print("[SUCCESS] Alle Pop-ups behandelt.")
    return True

def message_loop(driver, wait, bot_name):
    print("[+] Schritt 4: Starte Nachrichtenschleife...")
    while True:
        try:
            message_to_send = f"Hallo! Ich bin's, {bot_name}. Es ist {time.strftime('%H:%M:%S')}."
            message_field = wait.until(EC.presence_of_element_located((By.NAME, "message"))); message_field.send_keys(message_to_send); message_field.send_keys(Keys.RETURN)
            print(f"[SUCCESS] Nachricht gesendet. Warte 60 Sekunden...")
            time.sleep(60)
        except Exception as loop_error:
            print(f"[ERROR] Fehler in der Nachrichtenschleife: {loop_error}"); return

def start_bot():
    print("\n" + "="*50 + f"\nStarte neuen Bot-Zyklus am {time.strftime('%Y-%m-%d %H:%M:%S')}\n" + "="*50)
    driver = None
    try:
        print("[INFO] Versuche, den Chrome WebDriver zu starten (mit explizitem Pfad)...")
        
        # --- DIE ENTSCHEIDENDE ÄNDERUNG ---
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # ------------------------------------
        
        wait = WebDriverWait(driver, MAX_WAIT_TIME)
        print("[SUCCESS] WebDriver erfolgreich gestartet im Headless-Modus.")
        driver.get(WEBSITE_URL); print("[SUCCESS] Webseite geladen.")
        if not handle_cookies(driver, wait): raise Exception("Fehler bei Cookies.")
        bot_name = generate_random_name()
        if not perform_login(driver, wait, bot_name): raise Exception("Fehler beim Login.")
        if not dismiss_popups(driver, wait): raise Exception("Fehler bei Pop-ups.")
        take_screenshot_and_upload(driver, "login_success")
        message_loop(driver, wait, bot_name)
    except Exception as e:
        print("!"*50 + f"\n[FATAL] Schwerwiegender Fehler: {e}\n" + "!"*50)
        if driver: take_screenshot_and_upload(driver, "fatal_error")
    finally:
        if driver: driver.quit()
        print("[INFO] Bot-Zyklus beendet.")

if __name__ == "__main__":
    print("[MAIN] Starte Keep-alive Server...")
    threading.Thread(target=keep_alive, daemon=True).start()
    print("[MAIN] Starte Haupt-Bot-Schleife...")
    while True:
        start_bot()
        print(f"[MAIN] Nächster Start in 15 Sekunden...")
        time.sleep(15)
