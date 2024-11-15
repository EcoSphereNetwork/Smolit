#!/bin/bash
# -*- coding: utf-8 -*-
# ========================================================#
# This file is a part of Smolit package                   #
# Website: **Smolitux**                                   #
# GitHub:  https://github.com/eco-sphere-network/smolitux #
# MIT License                                             #
# Created By  : Sam Schimmelpfennig                       #
# Updated Date: 28.10.2024 10:00:00                       #
# ========================================================#

import tkinter as tk
import asyncio
from tkinter import Toplevel, Text, Button, END, Frame, Label
from agents.core.multi_agent_system import MultiAgentSystem
import subprocess

# Configuration for local LM Studio server
API_URL_BASE = "http://localhost:1234/v1/"
API_KEY = "lm_studio"

class SimpleAssistantApp:
    def __init__(self):
        # Initialize main icon window
        self.root = tk.Tk()
        self.root.geometry("50x50")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.title("Smolit Desktop-Icon")

        # Initialize multi-agent system
        self.agent_system = MultiAgentSystem(
            api_key=API_KEY,
            api_base=API_URL_BASE
        )

        # Create icon button
        self.icon_button = tk.Button(self.root, text="🤖", font=("Arial", 14), bg='#15aaff')
        self.icon_button.pack(expand=True, fill='both')
        self.icon_button.bind("<Double-Button-1>", lambda event: self.open_chat_window())

        # Close button
        close_button = Button(self.root, text="X", command=self.close_application, width=2)
        close_button.pack(side=tk.BOTTOM)

        # Enable dragging
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.root.x = event.x
        self.root.y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.root.x
        y = self.root.winfo_pointery() - self.root.y
        self.root.geometry(f"+{x}+{y}")

    def open_chat_window(self):
        if hasattr(self, 'chat_window') and self.chat_window.winfo_exists():
            self.chat_window.lift()
            return

        self.chat_window = Toplevel(self.root)
        self.chat_window.title("Smolit")
        self.chat_window.wm_attributes("-topmost", True)
        self.chat_window.geometry("400x600")  # Slightly larger window

        # Header
        head_frame = Frame(self.chat_window, bg='#15aaff')
        toggle_btn = Button(head_frame, text='☰', bg='#15aaff', fg='white',
                          font=('Bold', 20),
                          activebackground='#15aaff', activeforeground='white',
                          command=self.toggle_menu)
        toggle_btn.pack(side=tk.LEFT)

        title_lb = tk.Label(head_frame, text='Smolit AI', bg='#15aaff', fg='white',
                          font=('Bold', 20))
        title_lb.pack(side=tk.LEFT)
        head_frame.pack(side=tk.TOP, fill=tk.X)

        # Chat area
        self.response_area = Text(self.chat_window, wrap="word", state="disabled", 
                                bg="#f0f0f0", height=20)
        self.response_area.pack(expand=True, fill="both", padx=5, pady=(5, 0))

        # Input area
        self.user_input = Text(self.chat_window, height=4, bg="#ffffff")
        self.user_input.pack(expand=True, fill="both", padx=5, pady=(5, 5))

        # Send button
        send_button = Button(self.chat_window, text="Send", command=self.send_message,
                           bg='#15aaff', fg='white')
        send_button.pack(side='left', padx=(5, 5), pady=5)

        self.user_input.bind("<Return>", lambda event: (self.send_message(), "break"))

    def toggle_menu(self):
        if hasattr(self, 'menu_frame') and self.menu_frame.winfo_exists():
            self.menu_frame.destroy()
            return
        
        self.menu_frame = Frame(self.chat_window, bg='#15aaff')
        
        buttons_info = [
            ("Chat", 20, lambda: self.toggle_menu()),
            ("Knowledge", 80, lambda: self.show_knowledge_page()),
            ("Settings", 140, lambda: self.show_settings_page()),
            ("Help", 200, lambda: self.show_help_page()),
        ]

        for text, y, command in buttons_info:
            btn = Button(self.menu_frame, text=text,
                        font=('Bold', 20), bd=0,
                        bg='#15aaff', fg='white',
                        activebackground='#15aaff',
                        activeforeground='white',
                        command=command)
            btn.place(x=20, y=y)

        window_height = self.chat_window.winfo_height()
        self.menu_frame.place(x=0, y=50, height=window_height - 50, width=200)

    async def process_message(self, user_input):
        """Process message using multi-agent system."""
        return await self.agent_system.process_input(user_input)

    def send_message(self):
        user_input = self.user_input.get("1.0", END).strip()
        if not user_input:
            return

        self.display_message("You", user_input)
        self.user_input.delete("1.0", END)

        # Create and run asyncio event loop for processing
        async def process():
            response = await self.process_message(user_input)
            self.root.after(0, lambda: self.display_message("Assistant", response))

        asyncio.run(process())

    def display_message(self, sender, message):
        """Display message in response area."""
        self.response_area.config(state="normal")
        self.response_area.insert(END, f"{sender}: {message}\n\n")
        self.response_area.config(state="disabled")
        self.response_area.see(END)

    def show_knowledge_page(self):
        """Show the knowledge base management page."""
        # TODO: Implement knowledge base management UI
        pass

    def show_settings_page(self):
        """Show the settings page."""
        # TODO: Implement settings UI
        pass

    def show_help_page(self):
        """Show the help page."""
        # TODO: Implement help UI
        pass

    def close_application(self):
        """Close the application completely."""
        self.root.destroy()

    def run(self):
        """Run the Tkinter main loop."""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    app = SimpleAssistantApp()
    app.run()

