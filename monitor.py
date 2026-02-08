from playwright.sync_api import sync_playwright
import requests
import time
import os


# ==============================
# CONFIG
# ==============================

URL = "https://www.fcbarcelona.com/en/tickets/football/regular/laliga/fcbarcelona-celtadevigo"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHECK_INTERVAL = 1800   # 30 minutes
# CHECK_INTERVAL = 300  # use for testing


# ==============================
# TELEGRAM ALERT
# ==============================

def send_alert(message):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={
            "chat_id": CHAT_ID,
            "text": message
        }
    )


# ==============================
# MAIN CHECK FUNCTION
# ==============================

def check_ticket():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)

        # wait until ticket buttons are rendered
        page.locator("button:has-text('BUY TICKETS')").first.wait_for()

        # -------------------------------------------------
        # Anchor ONLY to ticket grid (important)
        # -------------------------------------------------
        ticket_grid = page.locator(
            "section:has(button:has-text('BUY TICKETS'))"
        ).first

        # -------------------------------------------------
        # Find BUY buttons only inside ticket grid
        # -------------------------------------------------
        buy_buttons = ticket_grid.locator(
            "button:has-text('BUY TICKETS'):visible"
        )

        available = False
        total_buttons = buy_buttons.count()

        print(f"BUY buttons detected in grid = {total_buttons}")

        # -------------------------------------------------
        # Check which card each BUY button belongs to
        # Trigger only for Basic / Basic Plus
        # -------------------------------------------------
        for i in range(total_buttons):

            button = buy_buttons.nth(i)

            # get parent card text
            card_text = button.locator(
                "xpath=ancestor::div[1]"
            ).inner_text().upper()

            if "BASIC" in card_text:
                print("Basic or Basic Plus BUY detected")
                available = True
                break

        print(f"Available = {available}")

        browser.close()
        return available


# ==============================
# MAIN LOOP
# ==============================

alert_sent = False

# send_alert("Monitoring started")  # optional startup test

while True:

    try:
        available = check_ticket()

        if available and not alert_sent:
            send_alert(
                "FC Barcelona tickets AVAILABLE (Basic / Basic Plus) — BUY NOW"
            )
            alert_sent = True

        if not available:
            alert_sent = False

    except Exception as e:
        print("ERROR:", e)

    time.sleep(CHECK_INTERVAL)
