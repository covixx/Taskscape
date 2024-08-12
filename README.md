# Taskscape
A simple script that takes your Notion notebook's to-do list and converts it into your screensaver

![image](https://github.com/user-attachments/assets/c00d8a13-dd76-498d-a8c9-f44bb7a18e0d)

How to run: 
Download the script, and provide your API key and Page ID in the script. 

Next, run the following command: PyInstaller --onefile screensaver.py

Rename the .exe produced to .src, and place it in your System32 folder. 

Finally, select screensaver in your Screensavers options. 

The script does also scrape your Ticktick Focus Time because Ticktick doesn't support Focus Time in its API, but you can comment out / delete the update_countdown() function and the Playwright initialisation to remove that functionality. 

