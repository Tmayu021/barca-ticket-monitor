from playwright.sync_api import sync_playwright
import requests
import time
import os

URL = "https://www.fcbarcelona.com/en/tickets/football/regular/copa-del-rey/semifinals?int=WB_25-26_K1125-32&btm_source=WebBarca&btm_medium=HeroBannerTKT&btm_campaign=FUTMASC-SEMIFINALSCOPADELREY2526_EN_TKT_FUT_WW&_gl=1*18rygk7*_gcl_au*MTk5NTYzNzEwMS4xNzcwNTQxOTQ2"
KEYWORD = "Basic"


BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHECK_INTERVAL = 1800  # CHECK EVERY 30 MINUTES
# CHECK_INTERVAL = 300  # CHECK EVERY 5 MINUTES For Testing


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

        # Anchor to ticket grid
        ticket_grid = page.locator("section:has-text('VIP Premium')")
       
        print("---- TICKET GRID CONTENT ----")
        print(ticket_grid.inner_text())
        print("------------------------------")
        
        # Locate BASIC card inside grid
        basic_section = ticket_grid.locator("div").filter(
            has=page.locator("text=Basic")
        ).first        
        basic_count = basic_section.count()

        if basic_count == 0:
            print("Basic section not found")
            browser.close()
            return False
            
        print("---- BASIC SECTION CONTENT ----")
        print(basic_section.inner_text())
        print("--------------------------------")
        
        # Check button inside Basic card
        buy_button = basic_section.locator("button:has-text('BUY TICKETS'):visible")
        buy_count = buy_button.count()

        available = buy_count > 0

        # print(f"Basic section count = {basic_count}")
        # print(f"Buy button count = {buy_count}")
        print(f"Available = {available}")

        browser.close()
        return available

alert_sent = False

# send_alert("Test alert — monitoring is running")

while True:
    try:
        available = check_ticket()

        if available and not alert_sent:
            send_alert("BASIC tickets AVAILABLE for COPA DEL REY, BUY NOW")
            alert_sent = True

        if not available:
            alert_sent = False

    except Exception as e:
        print("ERROR:", e)


    time.sleep(CHECK_INTERVAL)








