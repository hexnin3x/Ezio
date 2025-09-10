import asyncio
import os
import subprocess
import webbrowser
from typing import List

import keyboard
import requests
from AppOpener import close, open as appopen
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from groq import Groq
from pywhatkit import playonyt
from pywhatkit import search as pywhatkit_search
from rich import print

# --- 1. INITIALIZATION & CONFIGURATION ---
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk F2VmSb YwPhnf", "pclqee", "tw-data-text tw-text-small tw-ta",
           "IZ6rdc", "O5uR6d LTKOO", "VLGz6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
           "LwFkKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SP226b"]
client = Groq(api_key=GroqAPIKey)
messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('USERNAME', 'User')}. You are a content writer."}]

# --- 2. CORE AUTOMATION FUNCTIONS ---

def GoogleSearch(topic: str):
    print(f"Searching Google for: '{topic}'")
    pywhatkit_search(topic)
    return True

def YouTubeSearch(topic: str):
    print(f"Searching YouTube for: '{topic}'")
    webbrowser.open(f"https://www.youtube.com{topic.replace(' ', '+')}")
    return True

def PlayYoutube(query: str):
    print(f"Playing on YouTube: '{query}'")
    playonyt(query)
    return True

def PlaySpotify(query: str):
    print(f"Searching Spotify for: '{query}'")
    webbrowser.open(f"spotify:search:{query}")
    return True

def OpenApp(app_name: str):
    app_name = app_name.lower()
    if 'youtube' in app_name:
        webbrowser.open("https://www.youtube.com")
        return True
    if 'google' in app_name:
        webbrowser.open("https://www.google.com")
        return True
    if 'spotify' in app_name:
        appopen("spotify", match_closest=True)
        return True
    try:
        appopen(app_name, match_closest=True, output=False)
        return True
    except Exception:
        GoogleSearch(app_name)
        return True

def CloseApp(app_name: str):
    print(f"Attempting to close: '{app_name}'")
    try:
        if "chrome" in app_name.lower():
            os.system("taskkill /f /im chrome.exe")
        else:
            close(app_name, match_closest=True, output=False)
        return True
    except Exception:
        return False

def System(command: str):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
    }
    action = actions.get(command.lower().strip())
    if action:
        action()
        return True
    return False

def Content(topic: str):
    print(f"Generating content for: '{topic}'")
    os.makedirs("Data", exist_ok=True)
    messages.append({"role": "user", "content": topic})
    completion = client.chat.completions.create(
        model="llama3-70b-8192", messages=SystemChatBot + messages, max_tokens=2048,
    )
    answer = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    file_path = os.path.join("Data", f"{topic.lower().replace(' ', '_')}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(answer)
    subprocess.Popen(['notepad.exe', file_path])
    return True

# --- 3. ASYNCHRONOUS EXECUTION ENGINE ---

async def TranslateAndExecute(commands: List[str]):
    tasks = []
    command_map = {
        "play on spotify": PlaySpotify,
        "play": PlayYoutube,
        "open": OpenApp,
        "close": CloseApp,
        "content": Content,
        "google search": GoogleSearch,
        "Youtube": YouTubeSearch,
        "system": System,
    }
    for command in commands:
        command_found = False
        for keyword, func in command_map.items():
            if command.lower().startswith(keyword):
                argument = command[len(keyword):].strip()
                tasks.append(asyncio.to_thread(func, argument))
                print(f"Executing '{keyword}' with argument: '{argument}'")
                command_found = True
                break
        if not command_found:
            print(f"No Function Found for: {command}")
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def Automation(commands: list[str]):
    print("\n--- Starting Automation Sequence ---")
    await TranslateAndExecute(commands)
    print("--- Automation Sequence Finished ---\n")