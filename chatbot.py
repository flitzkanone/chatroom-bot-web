import time
import random
import threading
from flask import Flask
from selenium import webdriver
# ... (alle anderen imports bleiben gleich)
import os

# WICHTIG: Sage Selenium, dass es den virtuellen Bildschirm nutzen soll.
os.environ['DISPLAY'] = ':1'

# ... (Flask App Code bleibt unverändert) ...
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive and running!"
def keep_alive():
    app.run(host='0.0.0.0', port=8080)

WEBSITE_URL = "http://chatroom2000.de"

# --- WICHTIGE ÄNDERUNG HIER ---
chrome_options = Options()
# Die '--headless' Zeile wird ENTFERNT oder auskommentiert!
# chrome_options.add_argument("--headless") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Starte den Browser maximiert, damit wir im VNC alles sehen
chrome_options.add_argument("--start-maximized")

# ... (Der Rest deines Codes ab "def generate_random_name():" bleibt komplett unverändert) ...
