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

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(8000)

        # -----------------------------
        # Locate ticket grid
        # -----------------------------
        ticket_grid = page.locator(
            "section:has-text('VIP Premium')"
        ).first

        grid_text = ticket_grid.inner_text().upper()

        print("---- TICKET GRID TEXT ----")
        print(grid_text)
        print("--------------------------")

        available = False
        
        basic_plus_block = ""
        if "BASIC PLUS" in grid_text:
            basic_plus_block = grid_text.split("BASIC PLUS")[1][:200]

            if "BUY TICKETS" in basic_plus_block:
                print("Basic Plus BUY detected")
                available = True

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





