from playwright.sync_api import sync_playwright
import requests
import time
import os


URL = "https://www.fcbarcelona.com/en/tickets/football/regular/laliga/fcbarcelona-celtadevigo"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHECK_INTERVAL = 1800


# -----------------------------
# TELEGRAM
# -----------------------------
def send_alert(message):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": message}
    )


# -----------------------------
# CHECK FUNCTION
# -----------------------------
def check_ticket():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        
        # Accept cookies if popup appears
        try:
            page.locator("button:has-text('Agree')").click(timeout=5000)
            print("Cookie popup accepted")
        except:
            pass

        # wait for dynamic content
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(8000)

        # ------------------------------------
        # Find ALL BUY buttons on page
        # ------------------------------------
        buy_buttons = page.locator(
            "button:has-text('BUY TICKETS'):visible"
        )

        total_buttons = buy_buttons.count()
        print(f"Total BUY buttons found = {total_buttons}")

        available = False

        # ------------------------------------
        # Check which card owns the button
        # ------------------------------------
        for i in range(total_buttons):

            button = buy_buttons.nth(i)

            # go up to card container
            card_text = button.locator(
                "xpath=ancestor::div[1]"
            ).inner_text().upper()

            print(f"\n--- BUTTON {i+1} CARD ---")
            print(card_text)

            # trigger only for Basic or Basic Plus
            if "BASIC" in card_text:
                print("Basic / Basic Plus available")
                available = True
                break

        print(f"Available = {available}")

        browser.close()
        return available


# -----------------------------
# MAIN LOOP
# -----------------------------
alert_sent = False

while True:

    try:
        available = check_ticket()

        if available and not alert_sent:
            send_alert(
                "FC Barcelona BASIC tickets AVAILABLE — BUY NOW"
            )
            alert_sent = True

        if not available:
            alert_sent = False

    except Exception as e:
        print("ERROR:", e)

    time.sleep(CHECK_INTERVAL)

