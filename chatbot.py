import time
import random
import threading
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive and running!"
def keep_alive():
    app.run(host='0.0.0.0', port=8080)

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
    # NEU: Wir geben VOR der kritischen Zeile eine Nachricht aus
    print("Versuche, den Chrome WebDriver zu starten...")
    driver = None # Definieren wir driver hier, damit er im finally-Block existiert
    try:
        # NEU: Die kritische Zeile ist jetzt in einem try-Block
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)
        print("WebDriver erfolgreich gestartet im Headless-Modus.")
        
        # --- AB HIER IST DER CODE WIEDER IDENTISCH ---
        driver.get(WEBSITE_URL)
        print(f"Seite {WEBSITE_URL} geladen.")
        # ... (der Rest des Login-Prozesses)
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
        # NEU: Gibt jetzt eine spezifischere Fehlermeldung für den Startfehler
        if driver is None:
            print(f"Ein schwerwiegender Fehler ist BEIM STARTEN des WebDrivers aufgetreten: {e}")
        else:
            print(f"Ein schwerwiegender Fehler ist aufgetreten: {e}")
            print("Erstelle einen Screenshot des Fehlers: 'error_screenshot.png'")
            driver.save_screenshot('error_screenshot.png')
    finally:
        if driver:
            driver.quit()
        print("Browser wurde geschlossen (oder konnte nicht gestartet werden). Bereite Neustart vor.")

if __name__ == "__main__":
    t = threading.Thread(target=keep_alive)
    t.daemon = True
    t.start()
    print("Keep-alive Server gestartet.")
    while True:
        start_bot()
        print("Bot wird in 15 Sekunden neu gestartet...")
        time.sleep(15)
