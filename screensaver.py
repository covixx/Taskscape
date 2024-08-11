import flet as ft
from notion_client import Client
import time, threading, asyncio

"""TODO: mouse click quit
Async load
Rmv border around header
Make header and tasks immutable
"""

def main(page: ft.Page):
    page.window.full_screen = True
    page.window.frameless = True
    page.bgcolor = ft.colors.BLACK
    page.padding = 20
    to_do = []

    def on_keyboard(e:ft.KeyboardEvent):
        if e.key:
            page.window_close()
    def get_tasks():
        notion = Client(auth="Your API key here")
        #You can get your API key by creating a new Integration for your Notion account
        page_id = 'Your Notion page ID here'
        #The page ID is the last 32 digits in the page's URL
        page = notion.pages.retrieve(page_id=page_id)
        blocks = notion.blocks.children.list(block_id=page_id)
        
        for block in blocks['results']:
            if block['type'] == 'to_do':
                to_do.append({
                    'text': block['to_do']['rich_text'][0]['plain_text']
            })
                
        display_tasks.value = '\n'.join(str(task['text']) for task in to_do)
        page.update()

    display_title = ft.TextField(
        value="Tasks Left",
        text_align=ft.TextAlign.CENTER,
        color= 'grey',
        text_size= '50'
    )
    display_tasks = ft.TextField(
        multiline=True,
        shift_enter=True,
        color=ft.colors.WHITE,
        expand=True,
        text_align=ft.TextAlign.LEFT,
        border=ft.InputBorder.NONE,
        cursor_color='white',
        text_size= '30',
    )
    time_display = ft.Text(
        value = "",
        color = ft.colors.WHITE,
        size= 60,
        weight= ft.FontWeight.BOLD,
    )
    def update_time():
        while True: 
            time_display.value = time.strftime("%H:%M:%S")
            page.update()
            time.sleep(1)
    
    threading.Thread(target=get_tasks, daemon=True).start()
    threading.Thread(target=update_time, daemon=True).start()
    page.on_keyboard_event = on_keyboard
    page.add(
        display_title,
        ft.Row(
            [
                ft.Container(
                    content=display_tasks,
                    expand=5,
                    padding=10,
                ), 
                ft.Container(
                    content=ft.Column([time_display], alignment=ft.MainAxisAlignment.CENTER),
                    expand=5,
                    alignment=ft.alignment.top_center,
                )
            ],
            expand= True
        )
    )
    page.update()
    
ft.app(target=main)
