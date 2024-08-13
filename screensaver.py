import flet as ft
from notion_client import Client
import time, threading, asyncio
from datetime import datetime


def main(page: ft.Page):
    page.window.full_screen = True
    page.window.frameless = True
    page.bgcolor = ft.colors.BLACK
    page.padding = 20
    to_do = []

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key:
            page.window_destroy()

    def get_tasks():
        notion = Client(auth="Your Notion API key")
        page_id = 'Notion page\'s ID which has your to-do list'
        page = notion.pages.retrieve(page_id=page_id)
        blocks = notion.blocks.children.list(block_id=page_id)

        indent = ' ' * 5
        for block in blocks['results']:
            if block['type'] == 'to_do' and not block['to_do']['checked'] and block['to_do']['rich_text'][0]['plain_text'].strip() != '':
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
    
    def update_header():
        today_time = datetime.now()
        hour_time = today_time.hour
        if hour_time <= 12:
            display_title.value = "Good Morning"
        elif hour_time > 12 and hour_time <= 15:
            display_title.value = "Good Afternoon"
        elif hour_time > 15 and hour_time <= 24:
            display_title.value = "Good Evening"
        page.update()

    def update_time():
        while True:
            time_display.value = time.strftime("%H:%M:%S")
            page.update()
            time.sleep(1)   

    threading.Thread(target=get_tasks, daemon=True).start()
    threading.Thread(target=update_time, daemon=True).start()
    threading.Thread(target=update_header, daemon=True).start()
    
    page.on_keyboard_event = on_keyboard
    page.add(
        ft.Container(
            image_src= "Add path to image",
            image_opacity= 0.5,
            image_fit= ft.ImageFit.FILL,
            expand= True,
            content= ft.Container(
                ft.Container(
                    ft.Row([
                            ft.Container(content=display_tasks, expand=5, padding=10),
                            ft.Container(content=ft.Column([display_countdown], alignment=ft.MainAxisAlignment.END), expand=5, padding=10, alignment=ft.alignment.bottom_center),
                            ft.Container(content=ft.Column([time_display], alignment=ft.MainAxisAlignment.CENTER), expand=5, alignment=ft.alignment.top_center),
                        ], expand=True, 
                        ),
                ),
                ft.Container(
                    content= ft.Row([display_title], alignment=ft.MainAxisAlignment.CENTER),
                    alignment= ft.alignment.bottom_center,
                    ), 
            )
        ),
    )
    page.update()

if __name__ == "__main__":  
    ft.app(target=main)
