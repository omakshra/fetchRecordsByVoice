Feature 1: Voice-Based Record Fetching with Confirmation Prompt
This feature allows an officer to speak the name or case ID of a person, and the system fetches the related record. Before showing sensitive information, it confirms the identity with the officer through a voice prompt, preventing errors and improving data security.

Feature 2: Speech-Based Form Filling with Narration First + Guided Follow-Up
This feature lets the officer fill out an incident report through a conversation. 

Feature 3: Summarize Speech Input – Incident Dictation and Shift Summary
This feature allows officers to verbally describe an incident or summarize their shift at the end of the day. The system converts the spoken input into a concise, structured summary that can be saved or reviewed quickly, reducing manual reporting time.

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

🔹 Module 2: Incident Reporting
Page: Report.cshtml
Two modes:
Manual Form Entry
Date/time, officer name, location, involved persons, description
Voice-Based Entry
Officer is guided field-by-field
Speech input fills each field
Data is sent to Flask and saved

🔹 Module 3: Shift Summary Generation
Page: Summary.cshtml
Officer clicks mic button
Dictates entire shift summary
Flask processes and returns summarized version
Summary is stored or shown on screen

