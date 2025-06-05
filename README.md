Problem Statement
In critical or emergency situations, police officers require immediate access to case records to make timely decisions. Traditional record management systems rely on manual search methods, which can be slow and impractical when officers’ hands or attention are occupied. There is a need for a fast, voice-activated system that allows officers to retrieve records using simple voice commands, enabling quicker responses and improved operational efficiency in the field.
Problem Solution
The solution integrates a voice-activated record retrieval module into the existing Police RMS. Officers can quickly fetch case records by speaking a name or case ID. Speech recognition processes the commands, reducing manual input, while existing role-based controls ensure secure access to sensitive data.
System Workflow
1. Voice Input Capture
The system captures real-time voice input from the officer through a microphone-enabled interface.

2. Speech-to-Text Conversion
The live audio is sent to a Python backend where it is converted into text using a speech recognition engine.

3. Intent and Entity Extraction
The converted text is processed using NLP techniques to identify:
  - Intent (e.g., search, find, look up)
  - Entities (e.g., names, case IDs, dates)

4. Query Routing Logic
Based on identified keywords and context:
  - If the input includes terms like 'find', 'search', 'look' with a name or case ID, the system sends a request to the existing API to fetch person-related records.
  - If the input includes words like 'cases', 'reports', and a date, the system sends a request to the appropriate API to search records by date.

5. Structured Query Formation
The extracted data (entities + intent) is formed into a valid query format for backend APIs.

6. Data Retrieval and Display
The backend response is processed and displayed in a user-friendly interface, allowing hands-free viewing.
Technology Stack
Frontend
ASP.NET Core (Razor Pages) — A lightweight frontend to simulate the RMS UI, capture voice input, and display fetched records.

Backend (AI/ML Processing)
Flask (Python) — Handles real-time speech-to-text, NLP for intent/entity extraction, and query routing.

Database
SQL (SQLite/MySQL) — Stores mock records to simulate RMS data and support API testing.
Key Features
1. Voice-Based Record Retrieval (Criminal/Citizen Lookup)
  - Officers can retrieve records by speaking a name or case ID.
  - If multiple matches occur:
      - System prompts follow-ups like:
        - 'Can you confirm the Date of Birth?'
        - 'Do you know the address?'
      - Alternatively, fuzzy search lists all possible matches for selection.

2. Voice-Based Case Listing by Date
  - Officers can say:
      - 'Show me cases from May 15'
      - 'List all reports from last Monday'
  - System parses the date and returns matching records.

3. Predefined Voice Prompts (Sample Commands)
  - 'Find record for John Smith'
  - 'Search case ID 24589'
  
  
Module 1: Records Management
Page: Records.cshtml
Contains two sections:
🧾 Add Record Forms
Citizen Record Form: Name, age, address, ID
Criminal Record Form: Name, crime, date arrested, ID
Submit to Flask to insert into database
🎤 Voice-Based Record Fetch
Mic button
Officer speaks citizen/criminal name
Voice input is confirmed
Backend returns and displays the matching record

