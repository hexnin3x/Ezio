## 🛡 Ezio – A Jarvis-Inspired AI Voice Assistant

![Ezio Assistant Demo](Frontend/Graphics/jarvis.gif)

Ezio is a desktop-based AI assistant that brings the futuristic vibe of Jarvis right to your PC.
It doesn’t just obey – it listens, understands, and assists you with tasks like launching apps, searching the web, checking emails, managing media, and even generating content or images on the fly.

Unlike your typical command-based bots, Ezio feels more like a companion—capable of holding conversations and remembering context.

## ✨ Features

🖥 Application Management
Quickly open/close apps like Chrome, Spotify, or any program installed on your PC.

🌐 Web & Media Control
Perform Google searches, YouTube lookups, or even play a song/video directly.

📧 Email Assistant
Get notified of unread Gmail messages and receive clear, summarized updates.

📝 Content Generation
Generate articles, notes, or summaries on demand and save them as text files.

💬 Conversational AI
Talk naturally with Ezio—conversations are remembered (context tracking via JSON logs).

🎨 AI Image Generation
Create images from text prompts instantly. Perfect for quick concepts or fun ideas.

### 🛠 Tech Stack

Python 3.9+

PyQt5 → Desktop GUI

Groq API → Ultra-fast AI responses

pywhatkit → Web automation

AppOpener → Application control

### 🚀 Installation

Clone the repository:

bash
git clone https://github.com/hexnin3x/Ezio
cd jarvis-ai
Set up a virtual environment:

bash

## Windows

python -m venv venv
.\venv\Scripts\activate

## Linux/Mac

python3 -m venv venv
source venv/bin/activate
Install dependencies:

bash
pip install -r Requirements.txt
Configure environment variables:

bash

# Copy example file

cp .env.example .env
Edit .env with your API keys and config.

## ▶️ Usage

Run Ezio with:

bash
python main.py
Once running, you can:

Say “Open Spotify” → App launches immediately

Say “Search Assassin’s Creed lore on Google” → Results pop up

Say “Generate an image of a futuristic jet” → AI artwork appears

## 🤝 Contributing

Contributions are welcome! 🎉
Feel free to fork, open issues, or submit PRs.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fnumpy%2Fnumpy%2Fmain%2Fpyproject.toml&style=flat-square)](http://www.gnu.org/licenses/agpl-3.0)
