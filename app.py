"""
=============================================================
  SELF-LEARNING CHATBOT — MAIN APPLICATION (GUI)
=============================================================
  Project Title : NeuraBot - Self-Learning AI Chatbot
  Created By    : arik
  Description   : Beautiful Tkinter GUI for NeuraBot. The
                  chatbot learns from every conversation,
                  stores memory in a local SQLite database,
                  and requires zero internet or paid APIs.
=============================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import datetime
import os
import sys

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))
from brain import get_response, save_log, get_chat_log, get_all_knowledge, delete_knowledge, init_db

# ─────────────────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────────────────
BG_DARK    = "#0f0f1a"
BG_PANEL   = "#1a1a2e"
BG_CARD    = "#16213e"
ACCENT     = "#00d4ff"
ACCENT2    = "#7b2ff7"
USER_CLR   = "#00d4ff"
BOT_CLR    = "#a259ff"
SYS_CLR    = "#ffd700"
TEXT_CLR   = "#e0e0e0"
DIM_CLR    = "#888899"
BTN_CLR    = "#0a3d62"
BTN_HOV    = "#1e5f9f"
INPUT_BG   = "#1e1e3a"
ENTRY_BG   = "#252545"
RED_CLR    = "#ff4757"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_SUB    = ("Segoe UI", 10)
FONT_MSG    = ("Consolas", 11)
FONT_INPUT  = ("Segoe UI", 12)
FONT_BTN    = ("Segoe UI", 10, "bold")
FONT_LABEL  = ("Segoe UI", 9)
FONT_SMALL  = ("Segoe UI", 8)


class NeuraBotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        init_db()
        self.title("NeuraBot — Self-Learning AI Chatbot | arik")
        self.geometry("1000x680")
        self.minsize(800, 550)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        self._build_ui()
        self._show_welcome()

    # ──────────────────────────────────────────────────────
    #  UI BUILDER
    # ──────────────────────────────────────────────────────
    def _build_ui(self):
        # ── TOP HEADER ──
        header = tk.Frame(self, bg=BG_PANEL, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="🤖", font=("Segoe UI Emoji", 26),
                 bg=BG_PANEL, fg=ACCENT).pack(side="left", padx=(18, 6), pady=10)

        title_frame = tk.Frame(header, bg=BG_PANEL)
        title_frame.pack(side="left", pady=8)
        tk.Label(title_frame, text="NeuraBot", font=("Segoe UI", 18, "bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(anchor="w")
        tk.Label(title_frame, text="Self-Learning AI  •  Created by arik",
                 font=FONT_SMALL, bg=BG_PANEL, fg=DIM_CLR).pack(anchor="w")

        # Status dot
        self.status_dot = tk.Label(header, text="● ONLINE", font=("Segoe UI", 9, "bold"),
                                   bg=BG_PANEL, fg="#2ecc71")
        self.status_dot.pack(side="right", padx=20)

        # ── NAV TABS ──
        nav = tk.Frame(self, bg=BG_DARK)
        nav.pack(fill="x", padx=0)

        self.pages = {}
        self.nav_btns = {}
        btn_defs = [("💬  Chat", "chat"), ("📚  Knowledge Base", "knowledge"), ("📜  Chat History", "history"), ("ℹ️  About", "about")]
        for label, key in btn_defs:
            b = tk.Button(nav, text=label, font=FONT_BTN,
                          bg=BG_PANEL, fg=TEXT_CLR,
                          relief="flat", bd=0, padx=18, pady=8,
                          activebackground=ACCENT2, activeforeground="white",
                          cursor="hand2",
                          command=lambda k=key: self._switch_page(k))
            b.pack(side="left")
            self.nav_btns[key] = b

        # ── PAGE CONTAINER ──
        self.page_frame = tk.Frame(self, bg=BG_DARK)
        self.page_frame.pack(fill="both", expand=True)

        self._build_chat_page()
        self._build_knowledge_page()
        self._build_history_page()
        self._build_about_page()

        self._switch_page("chat")

    def _switch_page(self, key):
        for k, frame in self.pages.items():
            frame.pack_forget()
            self.nav_btns[k].configure(bg=BG_PANEL, fg=TEXT_CLR)
        self.pages[key].pack(fill="both", expand=True)
        self.nav_btns[key].configure(bg=ACCENT2, fg="white")

        if key == "knowledge":
            self._refresh_knowledge()
        if key == "history":
            self._refresh_history()

    # ──────────────────────────────────────────────────────
    #  CHAT PAGE
    # ──────────────────────────────────────────────────────
    def _build_chat_page(self):
        frame = tk.Frame(self.page_frame, bg=BG_DARK)
        self.pages["chat"] = frame

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            frame, wrap="word", font=FONT_MSG,
            bg=BG_CARD, fg=TEXT_CLR,
            relief="flat", bd=0,
            padx=14, pady=10,
            state="disabled",
            cursor="arrow",
            spacing1=4, spacing3=4
        )
        self.chat_display.pack(fill="both", expand=True, padx=12, pady=(10, 4))

        self.chat_display.tag_configure("user",    foreground=USER_CLR, font=("Consolas", 11, "bold"))
        self.chat_display.tag_configure("bot",     foreground=BOT_CLR,  font=("Consolas", 11))
        self.chat_display.tag_configure("system",  foreground=SYS_CLR,  font=("Segoe UI", 9, "italic"))
        self.chat_display.tag_configure("time",    foreground=DIM_CLR,  font=("Segoe UI", 8))
        self.chat_display.tag_configure("teach",   foreground="#2ecc71", font=("Consolas", 11))

        # Typing indicator
        self.typing_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.typing_var, font=("Segoe UI", 9, "italic"),
                 bg=BG_DARK, fg=DIM_CLR).pack(anchor="w", padx=14)

        # Input area
        input_frame = tk.Frame(frame, bg=BG_PANEL, pady=10)
        input_frame.pack(fill="x", padx=12, pady=(0, 10))

        self.user_input = tk.Entry(input_frame, font=FONT_INPUT,
                                   bg=ENTRY_BG, fg=TEXT_CLR,
                                   insertbackground=ACCENT,
                                   relief="flat", bd=0)
        self.user_input.pack(side="left", fill="x", expand=True, ipady=10, padx=(10, 6))
        self.user_input.bind("<Return>", lambda e: self._send_message())
        self.user_input.focus()

        tk.Button(input_frame, text="Send ➤", font=FONT_BTN,
                  bg=ACCENT2, fg="white",
                  relief="flat", bd=0, padx=18, pady=6,
                  activebackground="#5a1fc7",
                  cursor="hand2",
                  command=self._send_message).pack(side="left", padx=(0, 6))

        tk.Button(input_frame, text="🗑 Clear", font=FONT_BTN,
                  bg=BTN_CLR, fg=TEXT_CLR,
                  relief="flat", bd=0, padx=12, pady=6,
                  cursor="hand2",
                  command=self._clear_chat).pack(side="left", padx=(0, 10))

        # Quick tip bar
        tip = tk.Label(frame,
                       text="💡 Tip: Teach me with:  learn: your question | your answer",
                       font=FONT_SMALL, bg=BG_DARK, fg=DIM_CLR)
        tip.pack(anchor="w", padx=16, pady=(0, 6))

    def _append_chat(self, role: str, text: str):
        self.chat_display.configure(state="normal")
        now = datetime.datetime.now().strftime("%H:%M")

        if role == "user":
            self.chat_display.insert("end", f"\n  You  [{now}]\n", "time")
            self.chat_display.insert("end", f"  ▶  {text}\n", "user")
        elif role == "bot":
            tag = "teach" if text.startswith("✅") else "bot"
            self.chat_display.insert("end", f"\n  NeuraBot  [{now}]\n", "time")
            self.chat_display.insert("end", f"  🤖  {text}\n", tag)
        elif role == "system":
            self.chat_display.insert("end", f"\n  ⚙  {text}\n", "system")

        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _send_message(self):
        msg = self.user_input.get().strip()
        if not msg:
            return
        self.user_input.delete(0, "end")
        self._append_chat("user", msg)
        save_log("user", msg)
        self.typing_var.set("  NeuraBot is thinking...")
        self.update_idletasks()
        threading.Thread(target=self._get_bot_reply, args=(msg,), daemon=True).start()

    def _get_bot_reply(self, msg):
        import time
        time.sleep(0.4)
        reply = get_response(msg)
        save_log("bot", reply)
        self.after(0, lambda: self._append_chat("bot", reply))
        self.after(0, lambda: self.typing_var.set(""))

    def _clear_chat(self):
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        self._show_welcome()

    def _show_welcome(self):
        self._append_chat("system", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._append_chat("system", "Welcome to NeuraBot — Self-Learning AI Chatbot")
        self._append_chat("system", "Created by arik")
        self._append_chat("system", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._append_chat("bot", "Hello! I'm NeuraBot 🤖 I learn from every conversation. Ask me anything or teach me something new!")

    # ──────────────────────────────────────────────────────
    #  KNOWLEDGE BASE PAGE
    # ──────────────────────────────────────────────────────
    def _build_knowledge_page(self):
        frame = tk.Frame(self.page_frame, bg=BG_DARK)
        self.pages["knowledge"] = frame

        tk.Label(frame, text="📚 Knowledge Base",
                 font=("Segoe UI", 16, "bold"), bg=BG_DARK, fg=ACCENT).pack(pady=(16, 2), anchor="w", padx=18)
        tk.Label(frame, text="All patterns NeuraBot has learned. You can delete any entry.",
                 font=FONT_LABEL, bg=BG_DARK, fg=DIM_CLR).pack(anchor="w", padx=18)

        # Search bar
        sf = tk.Frame(frame, bg=BG_DARK)
        sf.pack(fill="x", padx=18, pady=8)
        tk.Label(sf, text="Search:", font=FONT_LABEL, bg=BG_DARK, fg=TEXT_CLR).pack(side="left")
        self.kb_search = tk.Entry(sf, font=FONT_INPUT, bg=ENTRY_BG, fg=TEXT_CLR,
                                  insertbackground=ACCENT, relief="flat", bd=0)
        self.kb_search.pack(side="left", fill="x", expand=True, ipady=6, padx=8)
        self.kb_search.bind("<KeyRelease>", lambda e: self._refresh_knowledge())
        tk.Button(sf, text="🔄 Refresh", font=FONT_BTN, bg=BTN_CLR, fg=TEXT_CLR,
                  relief="flat", bd=0, padx=10, pady=4,
                  cursor="hand2", command=self._refresh_knowledge).pack(side="left")

        # Treeview
        cols = ("ID", "Pattern", "Response Preview", "Hits", "Added On")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=BG_CARD, fieldbackground=BG_CARD,
                        foreground=TEXT_CLR, rowheight=28,
                        font=("Consolas", 10))
        style.configure("Custom.Treeview.Heading",
                        background=BG_PANEL, foreground=ACCENT,
                        font=("Segoe UI", 10, "bold"))
        style.map("Custom.Treeview", background=[("selected", ACCENT2)])

        self.kb_tree = ttk.Treeview(frame, columns=cols, show="headings",
                                    style="Custom.Treeview")
        for col, w in zip(cols, [40, 220, 320, 50, 130]):
            self.kb_tree.heading(col, text=col)
            self.kb_tree.column(col, width=w, anchor="w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.kb_tree.yview)
        self.kb_tree.configure(yscroll=sb.set)
        self.kb_tree.pack(fill="both", expand=True, padx=18, pady=(4, 0), side="left")
        sb.pack(side="right", fill="y", pady=(4, 0), padx=(0, 18))

        tk.Button(frame, text="🗑  Delete Selected", font=FONT_BTN,
                  bg=RED_CLR, fg="white", relief="flat", bd=0,
                  padx=14, pady=6, cursor="hand2",
                  command=self._delete_selected).pack(pady=10)

    def _refresh_knowledge(self):
        query = self.kb_search.get().lower() if hasattr(self, "kb_search") else ""
        for row in self.kb_tree.get_children():
            self.kb_tree.delete(row)
        for kid, pattern, response, hits, added in get_all_knowledge():
            preview = response[:60] + "..." if len(response) > 60 else response
            if query and query not in pattern.lower() and query not in response.lower():
                continue
            self.kb_tree.insert("", "end", iid=str(kid),
                                 values=(kid, pattern, preview, hits, added or "—"))

    def _delete_selected(self):
        sel = self.kb_tree.selection()
        if not sel:
            messagebox.showinfo("NeuraBot", "Please select a row to delete.")
            return
        if messagebox.askyesno("Delete?", f"Delete {len(sel)} selected knowledge entry/entries?"):
            for iid in sel:
                delete_knowledge(int(iid))
            self._refresh_knowledge()

    # ──────────────────────────────────────────────────────
    #  CHAT HISTORY PAGE
    # ──────────────────────────────────────────────────────
    def _build_history_page(self):
        frame = tk.Frame(self.page_frame, bg=BG_DARK)
        self.pages["history"] = frame

        tk.Label(frame, text="📜 Chat History",
                 font=("Segoe UI", 16, "bold"), bg=BG_DARK, fg=ACCENT).pack(pady=(16, 2), anchor="w", padx=18)
        tk.Label(frame, text="Full log of all conversations stored locally on your computer.",
                 font=FONT_LABEL, bg=BG_DARK, fg=DIM_CLR).pack(anchor="w", padx=18)

        self.history_box = scrolledtext.ScrolledText(
            frame, wrap="word", font=("Consolas", 10),
            bg=BG_CARD, fg=TEXT_CLR, relief="flat", bd=0,
            padx=12, pady=8, state="disabled"
        )
        self.history_box.pack(fill="both", expand=True, padx=18, pady=10)
        self.history_box.tag_configure("user", foreground=USER_CLR, font=("Consolas", 10, "bold"))
        self.history_box.tag_configure("bot",  foreground=BOT_CLR)
        self.history_box.tag_configure("ts",   foreground=DIM_CLR, font=("Segoe UI", 8))

        tk.Button(frame, text="🔄 Refresh History", font=FONT_BTN,
                  bg=BTN_CLR, fg=TEXT_CLR, relief="flat", bd=0,
                  padx=14, pady=6, cursor="hand2",
                  command=self._refresh_history).pack(pady=(0, 10))

    def _refresh_history(self):
        logs = get_chat_log(200)
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        for role, message, ts in logs:
            self.history_box.insert("end", f"[{ts}]  ", "ts")
            tag = "user" if role == "user" else "bot"
            prefix = "You     : " if role == "user" else "NeuraBot: "
            self.history_box.insert("end", f"{prefix}{message}\n", tag)
        self.history_box.configure(state="disabled")
        self.history_box.see("end")

    # ──────────────────────────────────────────────────────
    #  ABOUT PAGE
    # ──────────────────────────────────────────────────────
    def _build_about_page(self):
        frame = tk.Frame(self.page_frame, bg=BG_DARK)
        self.pages["about"] = frame

        card = tk.Frame(frame, bg=BG_CARD, padx=40, pady=30)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="🤖", font=("Segoe UI Emoji", 52), bg=BG_CARD).pack()
        tk.Label(card, text="NeuraBot", font=("Segoe UI", 28, "bold"),
                 bg=BG_CARD, fg=ACCENT).pack()
        tk.Label(card, text="Self-Learning AI Chatbot", font=("Segoe UI", 13),
                 bg=BG_CARD, fg=DIM_CLR).pack(pady=(2, 20))

        info = [
            ("👤 Created By",  "arik"),

            ("🐍 Language",    "Python (Tkinter + SQLite)"),
            ("🌐 API Used",    "None — 100% Offline"),
            ("🔒 Data Storage","Local SQLite Database"),
            ("🧠 Learning",    "Pattern Matching + Memory DB"),
        ]
        for label, value in info:
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{label}:", font=("Segoe UI", 11, "bold"),
                     bg=BG_CARD, fg=DIM_CLR, width=18, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Segoe UI", 11),
                     bg=BG_CARD, fg=TEXT_CLR).pack(side="left")

        tk.Label(card, text="\n© 2026 arik — All Rights Reserved",
                 font=FONT_SMALL, bg=BG_CARD, fg=DIM_CLR).pack(pady=(20, 0))


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = NeuraBotApp()
    app.mainloop()
