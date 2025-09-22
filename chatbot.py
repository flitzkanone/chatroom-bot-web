import time
import random
import threading # Neu hinzugefügt
from flask import Flask # Neu hinzugefügt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- KLEINER WEB-SERVER ZUM AM LEBEN HALTEN DES BOTS ---
app = Flask(__name__)

@app.route('/')
def home():
    # Dieser Text wird angezeigt, wenn jemand die Web-Adresse des Bots aufruft.
    return "Bot is alive and running!"

def keep_alive():
    # Startet den Flask-Server. Er wird auf dem von Render vorgegebenen Port laufen.
    app.run(host='0.0.0.0', port=8080)

# --- DEIN BOT-CODE (unverändert) ---
WEBSITE_URL = "http://chatroom2000.de"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("window-size=1920,1080")

def generate_random_name():
    random_numbers = random.randint(10, 99)
    name = f"Anna 16 {random_numbers}"
    return name

def start_bot():
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    print("WebDriver gestartet im Headless-Modus.")
    try:
        driver.get(WEBSITE_URL)
        print(f"Seite {WEBSITE_URL} geladen.")
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Einwilligen')]")))
            cookie_button.click()
            print("Cookie-Banner ('Einwilligen') erfolgreich weggeklickt.")
        except TimeoutException:
            try:
                cookie_button_alt = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Alle akzeptieren')]")))
                cookie_button_alt.click()
                print("Cookie-Banner ('Alle akzeptieren') erfolgreich weggeklickt.")
            except TimeoutException:
                print("Kein bekannter Cookie-Banner wurde gefunden. Mache weiter.")
        time.sleep(1)
        print("Suche nach dem Login-Formular...")
        nickname_field = wait.until(EC.presence_of_element_located((By.NAME, "nickname")))
        bot_name = generate_random_name()
        nickname_field.send_keys(bot_name)
        print(f"Nickname '{bot_name}' eingegeben.")
        agb_checkbox = wait.until(EC.element_to_be_clickable((By.ID, "tos")))
        agb_checkbox.click()
        print("AGB-Checkbox angeklickt.")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='LOS GEHTS!']")))
        login_button.click()
        print("Login-Button 'LOS GEHTS!' geklickt. Warte auf den Chat...")
        chatregeln_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Akzeptieren')]")))
        chatregeln_button.click()
        print("Chatregeln akzeptiert.")
        time.sleep(2)
        dos_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Akzeptieren')]")))
        dos_button.click()
        print("'Unsere Do's' akzeptiert.")
        time.sleep(2)
        fertig_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Fertig')]")))
        fertig_button.click()
        print("'Probleme'-Fenster geschlossen. Bot ist jetzt im Chat aktiv.")
        while True:
            try:
                message_to_send = f"Hallo zusammen! Viele Grüße von {bot_name}."
                message_field = wait.until(EC.presence_of_element_located((By.NAME, "message")))
                message_field.send_keys(message_to_send)
                message_field.send_keys(Keys.RETURN)
                print(f"Nachricht gesendet: '{message_to_send}'")
                print("Warte 60 Sekunden bis zur nächsten Nachricht...")
                time.sleep(60)
            except Exception as loop_error:
                print(f"Fehler in der Nachrichtenschleife: {loop_error}")
                driver.save_screenshot('error_in_loop.png')
                break
    except Exception as e:
        print(f"Ein schwerwiegender Fehler ist aufgetreten: {e}")
        print("Erstelle einen Screenshot des Fehlers: 'error_screenshot.png'")
        driver.save_screenshot('error_screenshot.png')
    finally:
        driver.quit()
        print("Browser wurde geschlossen. Bereite Neustart vor.")

# --- HAUPTPROGRAMM ---
if __name__ == "__main__":
    # Starte den Web-Server in einem Hintergrund-Thread
    t = threading.Thread(target=keep_alive)
    t.daemon = True # Erlaube dem Hauptprogramm, sich zu beenden, auch wenn dieser Thread läuft
    t.start()
    print("Keep-alive Server gestartet.")

    # Starte die Haupt-Bot-Schleife im Vordergrund
    while True:
        start_bot()
        print("Bot wird in 15 Sekunden neu gestartet...")
        time.sleep(15)
