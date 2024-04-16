"""Main bot module to find new flats posted on the same day at the Schwarzes Brett Bremen."""

import smtplib
import ssl
import os
import json
import time
from email.mime.text import MIMEText
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

# Get environment variables
load_dotenv()
APP_PASSWORD_GMAIL = os.getenv('APP_PASSWORD_GMAIL')
SENDER = os.getenv('SENDER')
RECIPIENTS = json.loads(os.environ['RECIPIENTS'])

def send_email(flat_name: str, link: str):
    """Function sending an email from gmail with the flat link & offer title"""

    msg = MIMEText(link)
    msg['Subject'] = "AP Finder: " + flat_name
    msg['From'] = SENDER
    msg['To'] = ', '.join(RECIPIENTS)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp_server:
        smtp_server.login(SENDER, APP_PASSWORD_GMAIL)
        smtp_server.sendmail(SENDER, RECIPIENTS, msg.as_string())
    print("Mail sent!")

def look_for_apartments():
    """Function actually looking for flats"""
    # JSON known flats file
    KNOWN_FLATS_FILE = 'knownflats.json'
    if os.path.isfile(KNOWN_FLATS_FILE):
        with open(KNOWN_FLATS_FILE, "r", encoding="utf-8") as file:
            known_flats = json.load(file)
    else:
        known_flats = []
        with open(KNOWN_FLATS_FILE, "w", encoding="utf-8") as file:
            json.dump(known_flats, file, indent=4)

    # Web part

    driver = webdriver.Chrome()

    driver.get("https://schwarzesbrett.bremen.de/verkauf-angebote/rubrik/wohnung-mietangebote-verkauf.html")

    driver.implicitly_wait(2.0)

    latest_flats_posted_element = driver.find_element(By.CSS_SELECTOR, ".content_list.eintraege_list")
    today_flatlist = latest_flats_posted_element.find_elements(by=By.CSS_SELECTOR, value="* > a")

    for flat in today_flatlist:
        link_to_flat = flat.get_attribute("href")
        if link_to_flat not in known_flats:
            known_flats.append(link_to_flat)

            with open(KNOWN_FLATS_FILE, "w", encoding="utf-8") as file:
                json.dump(known_flats, file, indent=4)

            flat_title_list = flat.text.split()[:-1] # Necessary to remove date from title of flat
            flat_title = " ".join(flat_title_list)

            send_email(flat_title, link_to_flat)

    driver.quit()

look_for_apartments()
schedule.every(10).minutes.do(look_for_apartments)

while True:
    schedule.run_pending()
    time.sleep(1)
