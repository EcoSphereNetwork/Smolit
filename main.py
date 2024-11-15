#!/usr/bin/env python3
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
from tkinter import Toplevel, Text, Button, END, Frame, Label, ttk, messagebox
from agents.core.multi_agent_system import MultiAgentSystem
from agents.core.config import Config, LLMEndpoint
import subprocess
import sys

# Ensure Python 3
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

class SimpleAssistantApp:
    def __init__(self):
        # Initialize configuration
        self.config = Config()
        
        # Initialize main icon window
        self.root = tk.Tk()
        self.root.geometry("50x50")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.title("Smolit Desktop-Icon")

        # Initialize multi-agent system with active endpoint
        self._initialize_agent_system()

        # Create icon button
        self.icon_button = tk.Button(
            self.root, 
            text="🤖", 
            font=("TkDefaultFont", 14),
            bg='#15aaff'
        )
        self.icon_button.pack(expand=True, fill='both')
        self.icon_button.bind("<Double-Button-1>", self.open_chat_window)

        # Close button
        close_button = Button(
            self.root, 
            text="X", 
            command=self.close_application, 
            width=2
        )
        close_button.pack(side=tk.BOTTOM)

        # Enable dragging
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def _initialize_agent_system(self):
        """Initialize the multi-agent system with current endpoint."""
        endpoint = self.config.get_active_endpoint()
        if endpoint.type == "llama" and not self.config.start_llama_server():
            messagebox.showerror("Error", "Failed to start Llama server")
            sys.exit(1)
            
        self.agent_system = MultiAgentSystem(
            api_key=endpoint.api_key,
            api_base=endpoint.api_base
        )

    def start_move(self, event):
        self.root.x = event.x
        self.root.y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.root.x
        y = self.root.winfo_pointery() - self.root.y
        self.root.geometry(f"+{x}+{y}")

    def open_chat_window(self, event=None):
        if hasattr(self, 'chat_window') and self.chat_window.winfo_exists():
            self.chat_window.lift()
            return

        self.chat_window = Toplevel(self.root)
        self.chat_window.title("Smolit")
        self.chat_window.wm_attributes("-topmost", True)
        self.chat_window.geometry("400x600")

        # Header
        head_frame = Frame(self.chat_window, bg='#15aaff')
        toggle_btn = Button(
            head_frame, 
            text='☰', 
            bg='#15aaff', 
            fg='white',
            font=("TkDefaultFont", 20),
            activebackground='#15aaff', 
            activeforeground='white',
            command=self.toggle_menu
        )
        toggle_btn.pack(side=tk.LEFT)

        title_lb = Label(
            head_frame, 
            text='Smolit AI', 
            bg='#15aaff', 
            fg='white',
            font=("TkDefaultFont", 20)
        )
        title_lb.pack(side=tk.LEFT)

        # Add endpoint selector
        self.endpoint_var = tk.StringVar(value=self.config.config["active_endpoint"])
        endpoint_select = ttk.Combobox(
            head_frame,
            textvariable=self.endpoint_var,
            values=list(self.config.config["endpoints"].keys()),
            state="readonly",
            width=15
        )
        endpoint_select.pack(side=tk.RIGHT, padx=5)
        endpoint_select.bind('<<ComboboxSelected>>', self.change_endpoint)

        head_frame.pack(side=tk.TOP, fill=tk.X)

        # Chat area
        self.response_area = Text(
            self.chat_window, 
            wrap=tk.WORD, 
            state=tk.DISABLED, 
            bg="#f0f0f0", 
            height=20
        )
        self.response_area.pack(expand=True, fill="both", padx=5, pady=(5, 0))

        # Input area
        self.user_input = Text(
            self.chat_window, 
            height=4, 
            bg="#ffffff"
        )
        self.user_input.pack(expand=True, fill="both", padx=5, pady=(5, 5))

        # Send button
        send_button = Button(
            self.chat_window, 
            text="Send", 
            command=self.send_message,
            bg='#15aaff', 
            fg='white'
        )
        send_button.pack(side='left', padx=(5, 5), pady=5)

        # Bind Return key to send message
        self.user_input.bind("<Return>", lambda e: self.send_message())

    def change_endpoint(self, event=None):
        """Change the active endpoint and reinitialize the agent system."""
        selected = self.endpoint_var.get()
        if selected != self.config.config["active_endpoint"]:
            # Stop current Llama server if running
            if self.config.config["endpoints"][self.config.config["active_endpoint"]]["type"] == "llama":
                self.config.stop_llama_server()
            
            # Set new endpoint
            self.config.set_active_endpoint(selected)
            
            # Reinitialize agent system
            self._initialize_agent_system()
            
            self.display_message(
                "System", 
                f"Switched to {self.config.config['endpoints'][selected]['name']} endpoint"
            )

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
            btn = Button(
                self.menu_frame, 
                text=text,
                font=("TkDefaultFont", 20), 
                bd=0,
                bg='#15aaff', 
                fg='white',
                activebackground='#15aaff',
                activeforeground='white',
                command=command
            )
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
        self.response_area.config(state=tk.NORMAL)
        self.response_area.insert(END, f"{sender}: {message}\n\n")
        self.response_area.config(state=tk.DISABLED)
        self.response_area.see(END)

    def show_knowledge_page(self):
        """Show the knowledge base management page."""
        # TODO: Implement knowledge base management UI
        pass

    def show_settings_page(self):
        """Show the settings page."""
        settings_window = Toplevel(self.chat_window)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(settings_window)
        
        # Endpoints tab
        endpoints_frame = ttk.Frame(notebook)
        notebook.add(endpoints_frame, text="Endpoints")
        
        # List of endpoints
        endpoints_list = tk.Listbox(endpoints_frame, width=40, height=10)
        for name, endpoint in self.config.config["endpoints"].items():
            endpoints_list.insert(tk.END, f"{name} ({endpoint['type']})")
        endpoints_list.pack(pady=10)
        
        # Buttons frame
        btn_frame = ttk.Frame(endpoints_frame)
        ttk.Button(btn_frame, text="Add", command=self.add_endpoint).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", command=lambda: self.edit_endpoint(endpoints_list.get(tk.ACTIVE))).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove", command=lambda: self.remove_endpoint(endpoints_list.get(tk.ACTIVE))).pack(side=tk.LEFT, padx=5)
        btn_frame.pack(pady=5)
        
        notebook.pack(expand=True, fill="both")

    def add_endpoint(self):
        """Show dialog to add new endpoint."""
        dialog = Toplevel(self.root)
        dialog.title("Add Endpoint")
        dialog.geometry("300x400")
        
        ttk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Type:").pack(pady=5)
        type_var = tk.StringVar(value="openai")
        ttk.Radiobutton(dialog, text="OpenAI Compatible", variable=type_var, value="openai").pack()
        ttk.Radiobutton(dialog, text="Llama", variable=type_var, value="llama").pack()
        
        ttk.Label(dialog, text="API Base:").pack(pady=5)
        api_base_entry = ttk.Entry(dialog)
        api_base_entry.pack(pady=5)
        
        ttk.Label(dialog, text="API Key:").pack(pady=5)
        api_key_entry = ttk.Entry(dialog, show="*")
        api_key_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Model:").pack(pady=5)
        model_entry = ttk.Entry(dialog)
        model_entry.pack(pady=5)
        
        def save():
            endpoint = LLMEndpoint(
                name=name_entry.get(),
                type=type_var.get(),
                api_base=api_base_entry.get(),
                api_key=api_key_entry.get(),
                model=model_entry.get()
            )
            self.config.add_endpoint(endpoint)
            dialog.destroy()
            self.show_settings_page()
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=20)

    def edit_endpoint(self, endpoint_name):
        """Show dialog to edit existing endpoint."""
        if not endpoint_name:
            return
            
        name = endpoint_name.split(" (")[0]
        endpoint = self.config.config["endpoints"][name]
        
        dialog = Toplevel(self.root)
        dialog.title("Edit Endpoint")
        dialog.geometry("300x400")
        
        ttk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.insert(0, endpoint["name"])
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Type:").pack(pady=5)
        type_var = tk.StringVar(value=endpoint["type"])
        ttk.Radiobutton(dialog, text="OpenAI Compatible", variable=type_var, value="openai").pack()
        ttk.Radiobutton(dialog, text="Llama", variable=type_var, value="llama").pack()
        
        ttk.Label(dialog, text="API Base:").pack(pady=5)
        api_base_entry = ttk.Entry(dialog)
        api_base_entry.insert(0, endpoint["api_base"])
        api_base_entry.pack(pady=5)
        
        ttk.Label(dialog, text="API Key:").pack(pady=5)
        api_key_entry = ttk.Entry(dialog, show="*")
        api_key_entry.insert(0, endpoint["api_key"])
        api_key_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Model:").pack(pady=5)
        model_entry = ttk.Entry(dialog)
        model_entry.insert(0, endpoint["model"])
        model_entry.pack(pady=5)
        
        def save():
            new_endpoint = LLMEndpoint(
                name=name_entry.get(),
                type=type_var.get(),
                api_base=api_base_entry.get(),
                api_key=api_key_entry.get(),
                model=model_entry.get()
            )
            self.config.remove_endpoint(name)
            self.config.add_endpoint(new_endpoint)
            dialog.destroy()
            self.show_settings_page()
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=20)

    def remove_endpoint(self, endpoint_name):
        """Remove selected endpoint."""
        if not endpoint_name:
            return
            
        name = endpoint_name.split(" (")[0]
        if messagebox.askyesno("Confirm", f"Remove endpoint {name}?"):
            self.config.remove_endpoint(name)
            self.show_settings_page()

    def show_help_page(self):
        """Show the help page."""
        help_window = Toplevel(self.chat_window)
        help_window.title("Help")
        help_window.geometry("500x400")
        
        text = Text(help_window, wrap=tk.WORD)
        text.pack(expand=True, fill="both", padx=10, pady=10)
        
        help_content = """
        Smolit AI Assistant Help

        Available Commands:
        - Chat: Regular conversation with AI
        - Knowledge: Access and manage knowledge base
        - Settings: Configure LLM endpoints and other settings
        - Help: This help page

        Endpoints:
        - LM Studio: Local LLM using LM Studio
        - Llama: Local Llama server (auto-started when selected)
        - Custom: Add your own endpoints in Settings

        For more information, visit:
        https://github.com/eco-sphere-network/smolitux
        """
        
        text.insert("1.0", help_content)
        text.config(state=tk.DISABLED)

    def close_application(self):
        """Close the application completely."""
        self.config.stop_llama_server()
        self.root.destroy()

    def run(self):
        """Run the Tkinter main loop."""
        self.root.mainloop()

def main():
    """Main entry point with error handling."""
    try:
        app = SimpleAssistantApp()
        app.run()
    except Exception as e:
        import traceback
        print(f"Error starting application: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

