import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

WEBSITE_URL = "http://chatroom2000.de"

# Diese Optionen sind für den Server-Betrieb (Render & Codespaces) entscheidend
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("window-size=1920,1080") # Eine gute Auflösung ist wichtig

def generate_random_name():
    random_numbers = random.randint(10, 99)
    name = f"Anna{random_numbers}xx" # Geändert, um den Regeln der Seite zu entsprechen
    return name

def start_bot():
    driver = webdriver.Chrome(options=chrome_options)
    # Wartezeit von bis zu 20 Sekunden pro Schritt definieren
    wait = WebDriverWait(driver, 20)
    
    print("WebDriver gestartet im Headless-Modus.")

    try:
        # --- SCHRITT 1: SEITE LADEN ---
        driver.get(WEBSITE_URL)
        print(f"Seite {WEBSITE_URL} geladen.")

        # --- SCHRITT 2: COOKIE-BANNER AKZEPTIEREN (wie in Bild 1 & 2) ---
        # Die Seite hat verschiedene Cookie-Banner. Wir versuchen beide möglichen Buttons zu finden.
        try:
            # Versuch 1: Der "Einwilligen" Button
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Einwilligen')]")))
            cookie_button.click()
            print("Cookie-Banner ('Einwilligen') erfolgreich weggeklickt.")
        except TimeoutException:
            try:
                # Versuch 2: Der "Alle akzeptieren" Button
                cookie_button_alt = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Alle akzeptieren')]")))
                cookie_button_alt.click()
                print("Cookie-Banner ('Alle akzeptieren') erfolgreich weggeklickt.")
            except TimeoutException:
                print("Kein bekannter Cookie-Banner wurde gefunden. Mache weiter.")
        
        time.sleep(1) # Kurze Pause nach dem Klick

        # --- SCHRITT 3: LOGIN-FORMULAR AUSFÜLLEN (wie in Bild 3 & 4) ---
        print("Suche nach dem Login-Formular...")
        # Nickname-Feld finden und ausfüllen
        nickname_field = wait.until(EC.presence_of_element_located((By.NAME, "nickname")))
        bot_name = generate_random_name()
        nickname_field.send_keys(bot_name)
        print(f"Nickname '{bot_name}' eingegeben.")
        
        # AGB-Checkbox finden und anklicken
        agb_checkbox = wait.until(EC.element_to_be_clickable((By.ID, "tos")))
        agb_checkbox.click()
        print("AGB-Checkbox angeklickt.")

        # "LOS GEHTS!"-Button finden und klicken
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='LOS GEHTS!']")))
        login_button.click()
        print("Login-Button 'LOS GEHTS!' geklickt. Warte auf den Chat...")
        
        # --- SCHRITT 4: POP-UPS NACH DEM LOGIN WEGKLICKEN (wie in Bild 5, 6, 7) ---
        # Warte und klicke auf "Akzeptieren" für die Chatregeln
        chatregeln_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Akzeptieren')]")))
        chatregeln_button.click()
        print("Chatregeln akzeptiert.")
        time.sleep(2) # Kurze Pause für das nächste Pop-up

        # Warte und klicke auf "Akzeptieren" für die "Do's"
        dos_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Akzeptieren')]")))
        dos_button.click()
        print("'Unsere Do's' akzeptiert.")
        time.sleep(2)

        # Warte und klicke auf "Fertig" für das "Probleme"-Fenster
        fertig_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Fertig')]")))
        fertig_button.click()
        print("'Probleme'-Fenster geschlossen. Bot ist jetzt im Chat aktiv.")

        # --- SCHRITT 5: NACHRICHTEN IN EINER SCHLEIFE SENDEN ---
        while True:
            try:
                # Nachrichtentext definieren
                message_to_send = f"Hallo zusammen! Viele Grüße von {bot_name}."
                
                # Nachrichtenfeld finden
                message_field = wait.until(EC.presence_of_element_located((By.NAME, "message")))
                
                # Nachricht eingeben und mit ENTER absenden
                message_field.send_keys(message_to_send)
                message_field.send_keys(Keys.RETURN)
                print(f"Nachricht gesendet: '{message_to_send}'")
                
                # Warte eine Minute (60 Sekunden)
                print("Warte 60 Sekunden bis zur nächsten Nachricht...")
                time.sleep(60)

            except Exception as loop_error:
                print(f"Fehler in der Nachrichtenschleife: {loop_error}")
                driver.save_screenshot('error_in_loop.png')
                break # Bricht die Schleife ab, um einen Neustart auszulösen

    except Exception as e:
        print(f"Ein schwerwiegender Fehler ist aufgetreten: {e}")
        print("Erstelle einen Screenshot des Fehlers: 'error_screenshot.png'")
        driver.save_screenshot('error_screenshot.png') # Macht ein Bild vom Fehler
    
    finally:
        driver.quit()
        print("Browser wurde geschlossen. Bereite Neustart vor.")

if __name__ == "__main__":
    while True:
        start_bot()
        print("Bot wird in 15 Sekunden neu gestartet...")
        time.sleep(15)
