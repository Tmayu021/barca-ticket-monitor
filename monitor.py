from playwright.sync_api import sync_playwright
import requests
import time
import os


URL = "https://www.fcbarcelona.com/en/tickets/football/regular/champions-league/roundof16?_gl=1*1ggnfxj*_gcl_au*MTk5NTYzNzEwMS4xNzcwNTQxOTQ2"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHECK_INTERVAL = 1200
# CHECK_INTERVAL = 300



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
            "section:has-text('Basic')"
        ).first

        grid_text = ticket_grid.inner_text().upper()

        # print("---- TICKET GRID TEXT ----")
        # print(grid_text)
        # print("--------------------------")

        available = False
        basic_block = ""
        
        if "BASIC" in grid_text and len(grid_text) > 200:
    
            # get text near BASIC card
            basic_block = grid_text.split("BASIC")[1][:200]
        
            # state change detection
            if (
                "LET ME KNOW" not in basic_block
                and
                "TEMPORARILY UNAVAILABLE" not in basic_block
            ):                
                print("Basic state changed — LET ME KNOW removed")
                available = True
       
        # print(f"Available = {available}")

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
                "FC Barcelona BASIC tickets may be AVAILABLE — BUY NOW"
            )
            alert_sent = True

        if not available:
            alert_sent = False

    except Exception as e:
        print("ERROR:", e)

    time.sleep(CHECK_INTERVAL)












