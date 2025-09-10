import sys
import os
import json
import subprocess
import threading
from time import sleep
from asyncio import run
from dotenv import dotenv_values

from Frontend.GUI import (
    GraphicalUserInterface, SetAssistantStatus, ShowTextToScreen, TempDirectoryPath,
    SetMicrophoneStatus, AnswerModifier, QueryModifier, GetMicrophoneStatus, GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.Email import check_emails

# --- Initial Setup ---
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")
DefaultMessage = f'''{Username}: Hello {Assistantname}, How are you?\n{Assistantname}: Welcome {Username}. I am doing well. How may I help you?'''
Functions = ["open", "close", "play", "system", "content", "google search", "Youtube", "spotify"]

# --- Helper Functions ---

def ShowDefaultChatIfNoChats():
    chat_log_path = r'Data\ChatLog.json'
    try:
        with open(chat_log_path, "r", encoding='utf-8') as f:
            content = f.read()
        if len(content) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write("")
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)
    except FileNotFoundError:
        with open(chat_log_path, 'w', encoding='utf-8') as f:
            f.write("[]")
        ShowDefaultChatIfNoChats()

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatlogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = "User" if entry["role"] == "user" else "Assistant"
        formatted_chatlog += f"{role}: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username)
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname)

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as db_file:
            data = db_file.read()
        if len(data) > 0:
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as resp_file:
                resp_file.write(data)
    except FileNotFoundError:
        print("Database.data not found, skipping showing chats on GUI.")

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatlogIntegration()
    ShowChatsOnGUI()

# --- Core Logic ---

def MainExecution():
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    if not Query: return

    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)

    print(f"\nDecision : {Decision}\n")

    # Check for "check email" command
    if any("check email" in d.lower() for d in Decision):
        SetAssistantStatus("Checking Email...")
        email_summary = check_emails()
        ShowTextToScreen(f"{Assistantname}: {email_summary}")
        TextToSpeech(email_summary)
        return

    # Check for Image Generation
    for queries in Decision:
        if "generate " in queries.lower():
            with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
                file.write(f'{queries},True')
            try:
                subprocess.Popen([sys.executable, r'Backend\ImageGenration.py'])
                confirmation_message = f"Okay, generating an image of {queries.replace('generate image', '').strip()}."
                ShowTextToScreen(f"{Assistantname}: {confirmation_message}")
                TextToSpeech(confirmation_message)
            except Exception as e:
                print(f"Error starting ImageGenration.py: {e}")
            return

    # Check for Automation Tasks
    if any(any(d.lower().startswith(f) for f in Functions) for d in Decision):
        run(Automation(list(Decision)))
        return

    # Handle Chat/Search queries
    is_general = any(d.startswith("general") for d in Decision)
    is_realtime = any(d.startswith("realtime") for d in Decision)
    merged_query = " and ".join([d.split(" ", 1)[1] for d in Decision if d.startswith("general") or d.startswith("realtime")])

    if is_realtime:
        Answer = RealtimeSearchEngine(QueryModifier(merged_query))
    elif is_general:
        Answer = ChatBot(QueryModifier(merged_query))
    else:
        Answer = ChatBot(QueryModifier(Query))

    ShowTextToScreen(f"{Assistantname}: {Answer}")
    SetAssistantStatus("Answering...")
    TextToSpeech(Answer)

    if any("exit" in d for d in Decision):
        TextToSpeech("Okay, Bye!")
        os._exit(0)

# --- Threading and Main Loop ---

def FirstThread():
    # REMOVED: Wake word logic has been taken out.
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        else:
            if "Available..." not in GetAssistantStatus():
                SetAssistantStatus("Available...")
            sleep(0.1)

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    InitialExecution()

    thread_backend = threading.Thread(target=FirstThread, daemon=True)
    thread_backend.start()

    SecondThread()
