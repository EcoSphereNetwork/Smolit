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
from tkinter import Toplevel, Text, Button, END, Frame, Label, ttk, messagebox, filedialog
from agents.core.multi_agent_system import MultiAgentSystem
from agents.core.config import Config, LLMEndpoint
import subprocess
import sys
import aiohttp
from openhands_client import OpenHandsClient

# Ensure Python 3
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

class SimpleAssistantApp:
    def __init__(self):
        # Initialize configuration
        self.config = Config()
        self.openhands_client = OpenHandsClient()
        self.instance_responses = {}
        
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
            ("Smolit-Hands", 140, lambda: self.show_smolit_hands_page()),
            ("Settings", 200, lambda: self.show_settings_page()),
            ("Help", 260, lambda: self.show_help_page()),
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

    def show_smolit_hands_page(self):
        """Show the Smolit-Hands Framework page."""
        if hasattr(self, 'smolit_hands_window') and self.smolit_hands_window.winfo_exists():
            self.smolit_hands_window.lift()
            return

        self.smolit_hands_window = Toplevel(self.chat_window)
        self.smolit_hands_window.title("Smolit-Hands Framework")
        self.smolit_hands_window.geometry("800x600")

        # Main container with grid layout
        main_container = Frame(self.smolit_hands_window)
        main_container.pack(expand=True, fill="both", padx=5, pady=5)

        # Supervisor tile (2x size)
        supervisor_frame = Frame(main_container, bg='#15aaff', relief="raised", bd=1)
        supervisor_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        Label(supervisor_frame, text="Supervisor", bg='#15aaff', fg='white', font=("TkDefaultFont", 14)).pack(pady=5)
        self.supervisor_text = Text(supervisor_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.supervisor_text.pack(expand=True, fill="both", padx=5, pady=5)

        # Container for OpenHands instances
        self.instances_container = Frame(main_container)
        self.instances_container.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Bottom section
        bottom_frame = Frame(main_container)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Input area
        self.hands_input = Text(bottom_frame, height=3)
        self.hands_input.pack(side=tk.LEFT, expand=True, fill="both", padx=(0, 5))

        # Buttons frame
        buttons_frame = Frame(bottom_frame)
        buttons_frame.pack(side=tk.RIGHT)

        Button(buttons_frame, text="Send", command=self.send_to_supervisor,
               bg='#15aaff', fg='white').pack(side=tk.TOP, pady=2)
        Button(buttons_frame, text="📎", command=self.attach_file,
               bg='#15aaff', fg='white').pack(side=tk.TOP, pady=2)
        Button(buttons_frame, text="+", command=self.add_openhands_instance,
               bg='#15aaff', fg='white').pack(side=tk.TOP, pady=2)

        # Configure grid weights
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        # Initialize with two default OpenHands instances
        self.add_openhands_instance()
        self.add_openhands_instance()

    def add_openhands_instance(self):
        """Add a new OpenHands instance tile."""
        if not hasattr(self, 'instance_count'):
            self.instance_count = 0
        
        instance_frame = Frame(self.instances_container, bg='#f0f0f0', relief="raised", bd=1)
        row = self.instance_count // 2
        col = self.instance_count % 2
        instance_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        Label(instance_frame, text=f"OpenHands {self.instance_count + 1}", 
              bg='#f0f0f0').pack(pady=5)
        
        instance_text = Text(instance_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        instance_text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Store the text widget reference
        self.instance_responses[self.instance_count] = instance_text
        
        self.instance_count += 1
        
        # Configure grid weights for the container
        self.instances_container.grid_columnconfigure(0, weight=1)
        self.instances_container.grid_columnconfigure(1, weight=1)

    def send_to_supervisor(self):
        """Send message to the Supervisor Agent."""
        message = self.hands_input.get("1.0", tk.END).strip()
        if not message:
            return
            
        self.supervisor_text.config(state=tk.NORMAL)
        self.supervisor_text.insert(tk.END, f"You: {message}\n")
        self.supervisor_text.config(state=tk.DISABLED)
        self.hands_input.delete("1.0", tk.END)
        
        # Process message asynchronously
        async def process():
            try:
                response = await self.openhands_client.send_to_supervisor(message)
                self.root.after(0, lambda: self.handle_supervisor_response(response))
            except Exception as e:
                self.root.after(0, lambda: self.display_error(f"Error: {str(e)}"))

        asyncio.run(process())

    def handle_supervisor_response(self, response: dict):
        """Handle the response from the Supervisor Agent."""
        if 'error' in response:
            self.display_error(response['error'])
            return
            
        message = response.get('response', '')
        self.supervisor_text.config(state=tk.NORMAL)
        self.supervisor_text.insert(tk.END, f"Supervisor: {message}\n")
        self.supervisor_text.config(state=tk.DISABLED)
        self.supervisor_text.see(tk.END)

        # Update instance responses if any
        for instance_id, instance_msg in response.get('instance_messages', {}).items():
            self.update_instance_response(int(instance_id), instance_msg)

    def update_instance_response(self, instance_id: int, message: str):
        """Update the response text for a specific OpenHands instance."""
        if instance_id not in self.instance_responses:
            return
            
        text_widget = self.instance_responses[instance_id]
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, f"Response: {message}\n")
        text_widget.config(state=tk.DISABLED)
        text_widget.see(tk.END)

    def attach_file(self):
        """Handle file attachment."""
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
            
        async def upload():
            try:
                file_id = await self.openhands_client.upload_file(file_path)
                self.root.after(0, lambda: self.handle_file_upload(file_id))
            except Exception as e:
                self.root.after(0, lambda: self.display_error(f"Upload error: {str(e)}"))

        asyncio.run(upload())

    def handle_file_upload(self, file_id: str):
        """Handle successful file upload."""
        if not file_id:
            self.display_error("File upload failed")
            return
            
        self.hands_input.insert(tk.END, f" [File: {file_id}] ")

    def display_error(self, message: str):
        """Display error message in supervisor text area."""
        self.supervisor_text.config(state=tk.NORMAL)
        self.supervisor_text.insert(tk.END, f"Error: {message}\n")
        self.supervisor_text.config(state=tk.DISABLED)
        self.supervisor_text.see(tk.END)

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










