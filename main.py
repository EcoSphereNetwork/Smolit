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
from tkinter import Toplevel, Text, Button, END, Frame, Label
from agent import AgentExperts  # Import the AgentExperts class
import subprocess

# Configuration for local LM Studio server
API_URL_BASE = "http://localhost:1234/v1/"
API_KEY = "lm_studio"

class SimpleAssistantApp:
    def __init__(self):
        # Initialize main icon window
        self.root = tk.Tk()
        self.root.geometry("50x50")  # Adjust size for menu
        self.root.overrideredirect(True)  # Remove title bar
        self.root.wm_attributes("-topmost", True)  # Always on top
        self.root.title("Smolit Desktop-Icon")

        # Create an instance of AgentExperts
        self.agent_experts = AgentExperts()

        # Create icon button that opens chat window on double-click
        self.icon_button = tk.Button(self.root, text="🤖", font=("Arial", 14), bg='#15aaff')
        self.icon_button.pack(expand=True, fill='both')

        # Bind double-click event to open chat window
        self.icon_button.bind("<Double-Button-1>", lambda event: self.open_chat_window())

        # Close button to exit the application
        close_button = Button(self.root, text="X", command=self.close_application, width=2)
        close_button.pack(side=tk.BOTTOM)  # Place it at the bottom of the icon window

        # Enable dragging the icon window
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        # Store position on mouse press
        self.root.x = event.x
        self.root.y = event.y

    def do_move(self, event):
        # Move the window based on cursor position
        x = self.root.winfo_pointerx() - self.root.x
        y = self.root.winfo_pointery() - self.root.y
        self.root.geometry(f"+{x}+{y}")

    def open_chat_window(self):
        if hasattr(self, 'chat_window') and self.chat_window.winfo_exists():
            self.chat_window.lift()  # Bring existing chat window to front
            return

        # Create a new chat window
        self.chat_window = Toplevel(self.root)
        self.chat_window.title("Smolit")
        
        # Set topmost attribute to keep it above other windows
        self.chat_window.wm_attributes("-topmost", True)
        
        # Set geometry for chat window
        self.chat_window.geometry("300x500")

        head_frame = Frame(self.chat_window, bg='#15aaff')
        
        toggle_btn = Button(head_frame, text='☰', bg='#15aaff', fg='white',
                            font=('Bold', 20),
                            activebackground='#15aaff', activeforeground='white',
                            command=self.toggle_menu)
        toggle_btn.pack(side=tk.LEFT)

        title_lb = tk.Label(head_frame, text='Smolit', bg='#15aaff', fg='white',
                            font=('Bold', 20))
        title_lb.pack(side=tk.LEFT)

        head_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.response_area = Text(self.chat_window, wrap="word", state="disabled", bg="#f0f0f0", height=15)
        self.response_area.pack(expand=True, fill="both", padx=5, pady=(5, 0))

        self.user_input = Text(self.chat_window, height=3, bg="#ffffff")
        self.user_input.pack(expand=True, fill="both", padx=5, pady=(0, 5))

        send_button = Button(self.chat_window, text="Send", command=self.send_message)
        send_button.pack(side='left', padx=(5, 5), pady=5)

        self.user_input.bind("<Return>", lambda event: (self.send_message(), "break"))

    def toggle_menu(self):
        if hasattr(self, 'menu_frame') and self.menu_frame.winfo_exists():
            self.menu_frame.destroy()
            return
        
        self.menu_frame = Frame(self.chat_window, bg='#15aaff')
        
        buttons_info = [
            ("Home", 20, lambda: print("Home clicked")),
            ("PyGPT", 80, lambda: self.run_pygpt()),
            ("Temp2", 140, lambda: [self.show_temp2_page(), self.toggle_menu()]),  # Close menu and show Temp2 page
            ("Temp3", 200, lambda: print("Temp3 clicked")),
            ("Temp4", 260, lambda: print("Temp4 clicked")),
            ("Temp5", 320, lambda: print("Temp5 clicked")),
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

    def run_pygpt(self):
            """Check if pygpt instance is running and toggle or start it."""
            
            process_name = "pygpt"  # Adjust this based on the actual window title
            
            try:
                output = subprocess.check_output(["pgrep", "-f", process_name])
                if output:
                    print("Pygpt is already running. Bringing it to focus.")
                    return 
                
                else:
                    print("Starting new pygpt instance.")
                    subprocess.Popen(["pygpt"])  # Adjust this command as needed
                
            except Exception as e:
                print(f"Error checking pygpt instance: {e}")
                print("Starting new pygpt instance.")
                subprocess.Popen(["pygpt"])  # Adjust this command as needed

    def show_temp2_page(self):
       """Show the Temp2 page."""
       temp2_frame = Frame(self.chat_window)  # Create a new frame on top of chat window

       temp2_label = Label(temp2_frame, text="This is Temp2 Page!", font=("Arial", 24))
       temp2_label.pack(pady=20)

       temp2_frame.pack(fill="both", expand=True)  # Show the frame over the chat window

    def send_message(self):
        user_input = self.user_input.get("1.0", END).strip()

        if user_input:
            response = self.agent_experts.main_agent(user_input)

            self.display_message("You", user_input)
            self.user_input.delete("1.0", END)
            self.display_message("Assistant", response)

    def display_message(self, sender, message):
       """Display message in response area."""
       self.response_area.config(state="normal")
       self.response_area.insert(END, f"{sender}: {message}\n\n")
       self.response_area.config(state="disabled")
       self.response_area.see(END)

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
