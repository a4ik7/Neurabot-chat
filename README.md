NeuraBot
A desktop chatbot built with Python's standard library only — no external APIs, no paid services.
Created by arik.
What it actually does
NeuraBot is a pattern-matching chatbot, not a machine-learning model. It works like this:
Every question-and-answer pair is stored in a local SQLite database.
When you type a message, it compares your text against known patterns using difflib similarity scoring.
The best match's response is returned. If a response gets picked often, it's tracked as more "popular."
You can manually add new Q&A pairs at any time — the bot doesn't learn on its own from ordinary conversation, but it does grow its knowledge base as you teach it.
There's no neural network, no external AI, no internet connection required. Everything runs offline.
Project structure
neurabot-chat/
├── app.py             ← Run this — Tkinter GUI for the chatbot
├── brain.py            ← Matching logic + SQLite-backed knowledge base
└── requirements.txt    ← Dependencies
Note: chatbot_memory.db (the knowledge database) is not included in this repo — it's created automatically the first time you run app.py, and it's your local chat data, not source code.
Setup
pip install -r requirements.txt
python app.py
Teaching NeuraBot new answers
In the chat box, type:
learn: capital of japan | The capital of Japan is Tokyo.
Format is always learn: <question/pattern> | <answer>. This gets saved to the local database and reused for similar future questions.
Features
Real-time chat GUI (Tkinter)
Local, persistent knowledge base (SQLite)
Knowledge base viewer, search, and delete
Full chat history log
License / Attribution
© 2026 arik. Built from scratch using Python's standard library.
