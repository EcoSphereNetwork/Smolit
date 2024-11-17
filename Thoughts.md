

**Ein Chatbot mit Multiagent Setup mit Llama-Index und Langchain:**

Language: Python

Chatbot_Backend:

Libraies:
            Langchain
            LLamafile
            OpenAI
            Wisper
            Coqi
            Texttospeech[KaljaB]
            Speechtotext[KoljaB]

- User 
      - Chatbot
            - {CLI}In/Out
            - {GUI}In/Out
            - {Tts + Stt}In/Out
            

Agent_Backend:

Libraries:
            Llama_Index
            Langchain

- User
      - Chatbot
            - Concierge
                  - Supervisor:     [Team]/:
                              - RAG[TeamLeader]
                              - CodeGenerator[TeamLeader]
                              - CriticalRewiev[TeamLeader]

UserInput_____________ChatBot______
                                   \
                                    \_______________multi-agent-concierge_________________
                                    /______________/_____________________\____________________\
                                   /              /                       \                    \
                   _______________/      ________/_______                 _\______________      \_______________________
                  supervisor-agent        supervisor-agent                 supervisor-agent              supervisor-agent     
      _________________/______________________    \________________             \________________          \_________________                     
      [Team: RAG CodeGenerator CriticalRewiev]    [Team: RAG CG CR]             [Team: RAG CG CR]           [Team: RAG CG CR]



**Agent Setup and communication pipeline:**
User chat with chatbot
chatbot pieps userinput to the multi-agent-concierge
the Concierge should split the Task into multiple "first_step_sub-tasks" and send the first_step_sub-tasks to the langchain supervisor.
The Langchain Supervisor should choose, witch Team should execut witch task.

Pipeline:
User - Chatbot - Concierge - Supervisoir - Team
Chatbot: User, Concierge
Concierge: Chatbot, Supervisor
Supervisor: Concierge, Teams
Team: Supervisor, TeamLeaders

There are several different Teams, for spezialiced Tasks:

React_Team:Coding:Frontend
Vue_Team:Coding:Frontend
HTML_Team:Coding:Frontend
CSS_Team:Coding:Frontend
Java_Team:Coding:Frontend/Backend?
TypeScript_Team:Coding:Frontend/Backend?
Python_Team:Coding:Backend

