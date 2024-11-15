#!/bin/bash
# -*- coding: utf-8 -*-
# ========================================================#
# This file is a part of Smolit package            #
# Website: **Smolitux**                                   #
# GitHub:  https://github.com/eco-sphere-network/smolitux #
# MIT License                                             #
# Created By  : Sam Schimmelpfennig                       #
# Updated Date: 28.10.2024 10:00:00                       #
# ========================================================#

# Define the model URL and local file name
MODEL_URL="https://huggingface.co/jartine/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile"
MODEL_FILE="TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile"
LOG_FILE="llama_server.log"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if the model file already exists
if [ ! -f "$MODEL_FILE" ]; then
    log "Downloading LlamaFile model..."
    wget $MODEL_URL | tee -a "$LOG_FILE"
else
    log "LlamaFile model already exists."
fi

# Make the LlamaFile executable
chmod +x $MODEL_FILE

# Start the LlamaFile server
log "Starting LlamaFile server..."
./$MODEL_FILE --server --nobrowser &
SERVER_PID=$!

# Function to stop the server on exit
cleanup() {
    log "Stopping LlamaFile server..."
    kill $SERVER_PID
}

trap cleanup EXIT

# Wait for the server to start and check if it's running
log "Waiting for LlamaFile server to start..."
for i in {1..10}; do
    sleep 2  # Wait for 2 seconds before checking
    if curl -s http://localhost:8080 > /dev/null; then
        log "LlamaFile server is running."
        break
    fi
    log "Waiting for server to start..."
done

if ! curl -s http://localhost:8080 > /dev/null; then
    log "Failed to start LlamaFile server. Exiting."
    exit 1
fi

# Monitor system resources while the server is running (optional)
log "Monitoring system resources (Press Ctrl+C to stop)..."

# Function to display running processes and their elapsed time
function display_processes() {
    echo "Current Processes:"
    ps -eo pid,etime,comm | grep -E "$SERVER_PID|$MODEL_FILE" | tee -a "$LOG_FILE"
}

# Run the process display function every 5 seconds in the background
while true; do
    display_processes
    sleep 5  # Adjust this interval as needed
done &

# Wait indefinitely for the server to run
wait $SERVER_PID

# After exiting, stop monitoring (the while loop will be terminated automatically)
kill %1  # Kill the process displaying current processes
log "Resource monitoring stopped."