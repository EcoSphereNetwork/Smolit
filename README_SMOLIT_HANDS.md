# Smolit-Hands Integration

This document describes the integration between Smolit and OpenHands Framework using LM-Studio for local LLM execution.

## Features

- Dedicated Smolit-Hands page in Smolit UI
- Supervisor Agent communication with multiple OpenHands instances
- File attachment support
- Dynamic creation of OpenHands instances
- Local LLM execution using LM-Studio

## Setup Instructions

1. Install Dependencies:
```bash
pip install -r requirements.txt
```

2. Configure LM-Studio:
- Download and install LM-Studio from https://lmstudio.ai/
- Load at least 3 different models:
  - One for Supervisor (port 1234)
  - One for OpenHands Instance 1 (port 1235)
  - One for OpenHands Instance 2 (port 1236)

3. Start Services:
```bash
# Start OpenHands services
cd ../Smolit-Hands_OpenHands
docker-compose -f docker-compose.lmstudio.yml up -d

# Start Smolit
cd ../Smolit
python main.py
```

## Usage

1. Launch Smolit
2. Click the menu button (☰)
3. Select "Smolit-Hands" from the menu
4. Use the Smolit-Hands interface:
   - Top section: Supervisor responses
   - Middle section: OpenHands instance responses
   - Bottom section: Input area with:
     - Text input field
     - Send button
     - File attachment button (📎)
     - Add instance button (+)

## Architecture

- **Smolit UI**: Main interface with Smolit-Hands page
- **OpenHands Client**: Handles communication with OpenHands services
- **Supervisor Agent**: Manages task delegation using LM-Studio
- **OpenHands Instances**: Execute specific tasks using dedicated LLMs

## Communication Flow

1. User sends message through Smolit UI
2. Message is sent to Supervisor Agent
3. Supervisor delegates tasks to OpenHands instances
4. Responses are displayed in respective tiles
5. File attachments are processed through the Supervisor

## Error Handling

- Connection errors are displayed in the Supervisor tile
- File upload failures show error messages
- Invalid instance IDs are handled gracefully

## Development

To modify or extend the integration:

1. OpenHands Client (`openhands_client.py`):
   - Handles API communication
   - Manages file uploads
   - Implements error handling

2. Smolit UI (`main.py`):
   - Smolit-Hands page implementation
   - Instance management
   - Response handling

3. Configuration:
   - LM-Studio endpoints in `config.lmstudio.toml`
   - Docker services in `docker-compose.lmstudio.yml`
