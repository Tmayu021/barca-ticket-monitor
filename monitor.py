from playwright.sync_api import sync_playwright
import requests
import time
import os

URL = "https://www.fcbarcelona.com/en/tickets/football/regular/copa-del-rey/semifinals?int=WB_25-26_K1125-32&btm_source=WebBarca&btm_medium=HeroBannerTKT&btm_campaign=FUTMASC-SEMIFINALSCOPADELREY2526_EN_TKT_FUT_WW&_gl=1*18rygk7*_gcl_au*MTk5NTYzNzEwMS4xNzcwNTQxOTQ2"
KEYWORD = "Basic"


BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

#CHECK_INTERVAL = 1800  # CHECK EVERY 30 MINUTES
CHECK_INTERVAL = 300  # CHECK EVERY 5 MINUTES For Testing


def send_alert(message):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": message}
    )

def check_ticket():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)

        # wait for JS to fully load
        page.wait_for_timeout(8000)

        # Locate BASIC ticket block
        basic_section = page.locator("text=Basic").first

        if basic_section.count() == 0:
            browser.close()
            return False

        # look for active BUY button inside Basic section
        buy_button = basic_section.locator("text=LET ME KNOW")

        available = buy_button.count() > 0

        browser.close()

        return available


alert_sent = False

send_alert("Test alert — monitoring is running")

while True:
    try:
        available = check_ticket()

        if available and not alert_sent:
            send_alert("BASIC tickets AVAILABLE for COPA DEL REY — LET ME KNOW PHASE, DO NOT BUY NOW")
            alert_sent = True

        if not available:
            alert_sent = False

    except Exception as e:
        print("ERROR:", e)


    time.sleep(CHECK_INTERVAL)



