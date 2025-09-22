import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

WEBSITE_URL = "http://chatroom2000.de"

# Diese Optionen sind für den Server-Betrieb (Render & Codespaces) entscheidend
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("window-size=1920x1080")

def generate_random_name():
    random_numbers = random.randint(10, 99)
    name = f"Anna[{random_numbers}]16"
    return name

def start_bot():
    driver = webdriver.Chrome(options=chrome_options)
    print("WebDriver gestartet im Headless-Modus.")
    driver.get(WEBSITE_URL)
    print(f"Seite {WEBSITE_URL} wird geladen...")
    time.sleep(5) # Gib der Seite etwas mehr Zeit zum Laden

    try:
        print("Suche nach dem Benutzernamen-Feld...")
        # WICHTIG: Der korrekte Name des Feldes ist 'user'
        username_field = driver.find_element(By.NAME, "user")
        
        bot_name = generate_random_name()
        print(f"Generierter Name: {bot_name}")
        username_field.send_keys(bot_name)
        username_field.send_keys(Keys.RETURN)
        print(f"Erfolgreich eingeloggt als: {bot_name}")
        time.sleep(3)

    except Exception as e:
        print(f"Fehler beim Einloggen: {e}")
        driver.save_screenshot('error_screenshot_login.png') # Macht ein Bild vom Fehler
        print("Screenshot 'error_screenshot_login.png' erstellt.")
        driver.quit()
        return

    try:
        while True:
            if driver.current_url != WEBSITE_URL and not driver.current_url.startswith(WEBSITE_URL):
                print("URL hat sich geändert! Starte den Bot neu...")
                driver.quit()
                return

            # WICHTIG: Der korrekte Name des Nachrichtenfeldes ist 'message'
            message_field = driver.find_element(By.NAME, "message")
            message_to_send = "Dies ist eine automatisierte Nachricht vom Bot."
            message_field.send_keys(message_to_send)
            message_field.send_keys(Keys.RETURN)
            print(f"Nachricht gesendet: '{message_to_send}'")
            
            print("Warte 60 Sekunden bis zur nächsten Nachricht...")
            time.sleep(60)

    except Exception as e:
        print(f"Ein Fehler ist in der Hauptschleife aufgetreten: {e}")
        driver.save_screenshot('error_screenshot_loop.png')
        print("Screenshot 'error_screenshot_loop.png' erstellt.")
    finally:
        driver.quit()
        print("Browser wurde geschlossen.")

if __name__ == "__main__":
    while True:
        start_bot()
        print("Bot wird in 10 Sekunden neu gestartet...")
        time.sleep(10)
