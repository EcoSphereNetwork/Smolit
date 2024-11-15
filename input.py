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

import os
import subprocess
import spacy
import json
import time
import requests
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_community.llms.llamafile import Llamafile

# Initialisierung von spaCy
nlp = spacy.blank("de")  # Deutsch als Beispiel

# Datei für die System-Prompts
PROMPT_FILE = "system_prompts.json"

# Gedächtnisinitialisierung
short_term_memory = ConversationBufferMemory(memory_key="history")
llm = None

# Funktion zum Starten des Llamafile-Servers
def start_llamafile_server():
    llamafile_name = "TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile"

    # Check if the Llamafile exists
    if not os.path.isfile(llamafile_name):
        print(f"{llamafile_name} nicht gefunden. Herunterladen...")
        
        # URL der Llamafile (hier ein Beispiel, bitte anpassen)
        url = "https://huggingface.co/jartine/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile"
        
        # Herunterladen der Llamafile
        subprocess.run(["wget", url])
        
        # Machen Sie die Datei ausführbar
        subprocess.run(["chmod", "+x", llamafile_name])
        
        print(f"{llamafile_name} wurde heruntergeladen und ist jetzt ausführbar.")
    else:
        print(f"{llamafile_name} ist bereits vorhanden.")
    
    # Starten des Llamafile-Servers im Servermodus
    print("Starte Llamafile-Server im Servermodus...")
    
    # Use shell=True to allow shell features like &
    process = subprocess.Popen(f"./{llamafile_name} --server --nobrowser &", shell=True)
    
    time.sleep(5)  # Wait for the server to fully start
    return process

# Funktion zur Initialisierung des LLMs mit dem Llamafile-Server
def initialize_llm():
    global llm
    try:
        llm = Llamafile(base_url="http://localhost:8080")  # Verbindung zum lokalen Server
        # Testverbindung
        response = llm.invoke("Hello, are you ready?")
        print("Llamafile-Server erfolgreich verbunden.")
    except requests.exceptions.ConnectionError:
        print("Verbindung zum Llamafile-Server fehlgeschlagen. Bitte stellen Sie sicher, dass der Server läuft.")
        llm = None

# Gedächtnisinitialisierung mit LLM
def initialize_memory():
    global long_term_memory
    if llm is not None:
        long_term_memory = ConversationSummaryMemory(memory_key="summary", llm=llm)
    else:
        long_term_memory = ConversationSummaryMemory(memory_key="summary")

def load_prompts():
    """Lädt die gespeicherten System-Prompts aus einer JSON-Datei."""
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_prompts(prompts):
    """Speichert die System-Prompts in einer JSON-Datei."""
    with open(PROMPT_FILE, 'w') as f:
        json.dump(prompts, f)

def select_or_create_prompt(prompts):
    """Ermöglicht dem Benutzer, einen bestehenden Prompt auszuwählen oder einen neuen zu erstellen."""
    if prompts:
        print("Verfügbare System-Prompts:")
        for idx, name in enumerate(prompts.keys()):
            print(f"{idx + 1}: {name}")

        choice = input("Wählen Sie einen Prompt (geben Sie die Nummer ein) oder 'n' für einen neuen Prompt: ")

        if choice.lower() == 'n':
            name = input("Geben Sie den Namen des neuen Prompts ein: ")
            prompt = input("Geben Sie den neuen System-Prompt ein: ")
            prompts[name] = prompt
            save_prompts(prompts)
            return prompt
        else:
            try:
                selected_index = int(choice) - 1
                selected_name = list(prompts.keys())[selected_index]
                return prompts[selected_name]
            except (ValueError, IndexError):
                print("Ungültige Auswahl. Ein neuer Prompt wird erstellt.")
                name = input("Geben Sie den Namen des neuen Prompts ein: ")
                prompt = input("Geben Sie den neuen System-Prompt ein: ")
                prompts[name] = prompt
                save_prompts(prompts)
                return prompt
    else:
        name = input("Keine vorhandenen Prompts gefunden. Geben Sie den Namen des neuen Prompts ein: ")
        prompt = input("Geben Sie den neuen System-Prompt ein: ")
        prompts[name] = prompt
        save_prompts(prompts)
        return prompt

def process_input(user_input, system_prompt):
    # Verarbeitung des Benutzerinputs mit spaCy
    spacy_output = nlp(user_input)

    # Kurzfristige Speicherung des Inputs mit ConversationBufferMemory
    short_term_memory.save_context({"input": user_input}, {"output": str(spacy_output)})

    # Langfristige Speicherung mit ConversationSummaryMemory (angepasst)
    if llm:
        long_term_memory.save_context({"input": user_input}, {"output": str(spacy_output)})
        
        # Anfrage an die Llamafile-API mit dem System-Prompt
        try:
            response = ""
            # Stream the response from Llamafile server
            print("Agent antwortet:")
            for chunk in llm.stream(f"{system_prompt}\n{spacy_output.text}"):
                print(chunk, end="", flush=True)
                response += chunk
            print()  # Line break after streaming output
        except requests.exceptions.ConnectionError:
            response = "Serverfehler: Verbindung zum Llamafile-Server nicht möglich."
    else:
        response = "Server nicht verfügbar. Der Llamafile-Server konnte nicht verbunden werden."

    # Protokollierung der Interaktion
    log_interaction(user_input, spacy_output.text, response)

    return response

def log_interaction(user_input, spacy_output, agent_response):
    print("=== Interaktion Protokoll ===")
    print(f"Benutzereingabe: {user_input}")
    print(f"spaCy Ausgabe: {spacy_output}")
    print(f"Agent Antwort: {agent_response}")
    print("==============================")

if __name__ == "__main__":
    # Start Llamafile-Server und initialisiere LLM
    server_process = start_llamafile_server()
    initialize_llm()  # Initialisiere den LLM-Client

    # Gedächtnis initialisieren
    initialize_memory()

    # Laden der gespeicherten Prompts
    prompts = load_prompts()

    # Auswahl oder Erstellung eines System-Prompts
    system_prompt = select_or_create_prompt(prompts)

    print("Willkommen beim AI-Agenten! Geben Sie 'exit' ein, um zu beenden.")
    
    while True:
        user_input = input("Bitte geben Sie Ihre Nachricht ein: ")
        
        if user_input.lower() == 'exit':
            break
        
        response = process_input(user_input, system_prompt)
        print(f"Agent: {response}")
    
    # Server beenden
    server_process.terminate()
    print("Llamafile-Server beendet.")
