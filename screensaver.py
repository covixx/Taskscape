import flet as ft
from notion_client import Client
import time, threading, asyncio
from datetime import datetime
from playwright.async_api import async_playwright

"""
TODO: 
    - [ ]  look into splashscreen to buffer out load time, and load everything at once
    - [ ]  look into splashscreen - comb_script hints for pyinstaller and load everything during that screen
    - [ ]  look into ignoring empty to-do boxes, script breaks if todo empty
    - [ ]  Try to optimise scrsvr runtime
    - [ ]  if not possible try to allow key_exit b4 and during launch

BUG: 
    - [ ]  look into ignoring empty to-do boxes, script breaks if todo empty
"""
def main(page: ft.Page):
    page.window.full_screen = True
    page.window.frameless = True
    page.bgcolor = ft.colors.BLACK
    page.padding = 20
    to_do = []

    path_profile = r'C:\Users\Vaibhav\AppData\Roaming\Mozilla\Firefox\Profiles\nchscwx1.Selenium'

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key:
            page.window_destroy()

    def get_tasks():
        notion = Client(auth="secret_pNLHXopzc5clPNX989JX6jlZTXJoGsxjNYulSKppduD")
        page_id = '6591607777dd4718aaf59cbcb70b19d1'
        page = notion.pages.retrieve(page_id=page_id)
        blocks = notion.blocks.children.list(block_id=page_id)

        indent = ' ' * 5
        for block in blocks['results']:
            if block['type'] == 'to_do' and not block['to_do']['checked']:
                to_do.append({
                    'text': block['to_do']['rich_text'][0]['plain_text']})
                if block['has_children']:
                    sub_blocks = notion.blocks.children.list(block_id=block['id'])
                    i = 0
                    for sub_block in sub_blocks['results']:
                        i += 1
                        if sub_block['type'] == 'to_do' and not sub_block['to_do']['checked']:
                            to_do.append({'text': f" {indent}{i}. " + sub_block['to_do']['rich_text'][0]['plain_text']})   
                
        display_tasks.value = '\n\n'.join(str(task['text']) for task in to_do)
        page.update()

    display_title = ft.Text(
        value="",
        text_align=ft.TextAlign.CENTER,
        color='grey',
        size=30,
        weight=ft.FontWeight.BOLD,
    )

    display_tasks = ft.TextField(
        shift_enter=True,
        color=ft.colors.WHITE,
        expand=True,
        border=ft.InputBorder.NONE,
        cursor_color='white',
        text_size='15',
    )

    time_display = ft.Text(
        value="",
        color=ft.colors.WHITE,
        size=120,
        weight=ft.FontWeight.BOLD,
    )
    
    display_countdown = ft.Text(
        value="",
        color=ft.colors.GREY,
        size=40,
        weight=ft.FontWeight.BOLD,
    )

    def update_header():
        today_time = datetime.now()
        hour_time = today_time.hour
        if hour_time <= 12:
            display_title.value = "Good Morning V"
        elif hour_time > 12 and hour_time <= 15:
            display_title.value = "Good Afternoon V"
        elif hour_time > 15 and hour_time <= 24:
            display_title.value = "Good Evening V"
        page.update()

    def update_time():
        while True:
            time_display.value = time.strftime("%H:%M:%S")
            page.update()
            time.sleep(1)    

    async def calc_countdown():
        async with async_playwright() as p:
            browser = await p.firefox.launch_persistent_context(
                user_data_dir=path_profile,
                headless=True,
                args=[
            '--disable-extensions',
            '--disable-gpu',
            '--disable-software-rasterizer'
                ]
            )
            page_browser = browser.pages[0] if browser.pages else await browser.new_page()

            await page_browser.goto('https://ticktick.com/webapp/#statistics/pomo', wait_until='networkidle')
            print("Page loaded. Waiting for 1 second...")
            await page_browser.wait_for_timeout(1000)
            while True:
                try:
                    selectors = [
                        "//p[contains(text(), 'h') and contains(text(), 'm')]",
                        "//div[contains(@class, 'pomodoro-statistics')]//p"
                    ]

                    time_get = None
                    for selector in selectors:
                        try:
                            element = await page_browser.wait_for_selector(selector, timeout=5000)
                            if element:
                                time_get = await element.inner_text()
                                print(f"Found element with selector: {selector}")
                                break
                        except Exception as e:
                            print(f"Selector {selector} failed: {e}")

                    if time_get is None:
                        raise Exception("Could not find the time element with any selector")

                    parts = time_get.replace('h', ' ').replace('m', ' ').split()
                    hours = parts[0] if len(parts) >= 1 else '0'
                    minutes = parts[1] if len(parts) >= 2 else '0'
                    msg = f"Focus Time: {hours:>2}h {minutes:>2}m"
                    display_countdown.value = msg
                    page.update()
                except Exception as e:
                    print(f"Error updating countdown: {e}")
                await asyncio.sleep(60)  # Update every minute

    def run_async_tasks():
        asyncio.run(calc_countdown())

    #Threading each function to run API and scraping simultaneously 
    threading.Thread(target=run_async_tasks, daemon=True).start()
    threading.Thread(target=get_tasks, daemon=True).start()
    threading.Thread(target=update_time, daemon=True).start()
    threading.Thread(target=update_header, daemon=True).start()
    
    page.on_keyboard_event = on_keyboard
    page.add(
        ft.Row([display_title], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row(
            [
                ft.Container(content=display_tasks, expand=5, padding=10),
                ft.Container(content=ft.Column([display_countdown], alignment=ft.MainAxisAlignment.END), expand=5, padding=10, alignment=ft.alignment.bottom_center),
                ft.Container(content=ft.Column([time_display], alignment=ft.MainAxisAlignment.CENTER), expand=5, alignment=ft.alignment.top_center),
            ],
            expand=True
        )
    )
    page.update()

if __name__ == "__main__":  # Wait for splash screen to finish
    ft.app(target=main)
