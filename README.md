**Abstract / Executive Summary**
In public safety sectors such as law enforcement, firefighting, and traffic control, timely access to digital records is crucial for informed decision-making during critical operations. However, traditional Record Management Systems (RMS) often rely on manual input and navigation, which can hinder efficiency—especially when personnel are in the field or under pressure. This project addresses that challenge by implementing a voice-enabled search interface that allows users to retrieve citizen and criminal records using natural language voice commands. The system integrates frontend speech recognition, a Python-based Flask backend for NLP processing (using tools like spaCy and regular expressions), and a .NET Razor Pages module for data filtering and presentation. The solution intelligently extracts multiple entities (e.g., names, crimes, dates, locations) from voice input, supports fuzzy matching for error tolerance, and dynamically filters SQL Server-based records in real-time. The result is a hands-free, intelligent, and extendable system that improves speed, accuracy, and usability in public safety environments.
//
**Problem Statement-**
In public safety domains like law enforcement, firefighting, and traffic control, quick access to records is essential for timely decision-making. Traditional Record Management Systems (RMS) rely on manual input, which can be slow or impractical when officers are on the move or handling emergencies. This creates a need for a voice-activated interface that allows hands-free, natural language access to records, improving efficiency and response times in the field.
//
**Proposed Solution-**
A voice-enabled search feature was integrated into a simulated police records module. The system processes spoken natural language commands to extract both user intent and multiple relevant entities—such as names, government IDs, and address—which are then mapped into the existing search workflow. This allows for accurate and dynamic retrieval of citizen and criminal records based on contextual input. The solution supports moderately complex queries and enhances hands-free usability. While currently applied to the police module, the design is scalable and can be extended to other domains within a public RMS, such as fire and traffic departments.
//
**System Workflow-**
1. **Voice Command Initiation**
   The user activates the voice input by clicking a microphone button on the UI. This triggers the `webkitSpeechRecognition` engine built into the browser, which begins listening for spoken input.
2. **Speech Recognition and Text Capture**
   Once the user finishes speaking, the browser’s speech recognition engine transcribes the spoken audio into text. This text is automatically inserted into the command input field and sent to the Python backend (`/api/command`) via a POST request.
3. **Natural Language Processing in Python**
   The Flask backend receives the command string and performs the following:
   * **Intent Detection**: Determines the user's intention, such as searching or looking up records.
   * **Entity Extraction**: Identifies structured information such as:
     * Name, age, address, government ID (for citizens)
     * Name, crime type, arrest date, government ID (for criminals)
   * **Module Identification**: Matches keywords to a module using a `module_synonyms` mapping file. For example, "suspect" maps to the "criminals" module.
4. **Client-Side Module Switching and Filtering**
   The backend responds with:
   * The identified module (e.g., `citizen` or `criminal`)
   * A dictionary of extracted entities
     On the frontend:
   * The relevant UI section/tab is auto-switched using `switchSection()`
   * A JavaScript filter object is constructed from extracted entities
5. **Data Query via Razor Page Handler**
   Based on the module, the appropriate AJAX search function (`searchCitizen()` or `searchCriminal()`) is triggered.
   These functions:
   * Format query parameters from extracted entities
   * Send a request to Razor Page handlers (`OnGetSearchCitizensAsync` or `OnGetSearchCriminalsAsync`) using the `?handler=SearchX` endpoint
6. **Backend Filtering Logic** (C#)
   On the server:
   * The `ApplicationDbContext` queries the database using LINQ and `EF.Functions.Like()` for partial matches
   * If multiple fields are present (e.g., name + age), combined filters are applied
   * If no specific filters are found, a fallback generic search is used via a `query` parameter
7. **Data Rendering on Frontend**
   The filtered results are returned as JSON. JavaScript functions render the data in HTML tables dynamically:
   * Highlighting is applied to matching terms
   * If results are found, the first match is auto-scrolled into view and highlighted
   * If no matches are found, a message is displayed within the table
//
**Technology Stack-**

1. **Frontend**
* **ASP.NET Core Razor Pages**
  Builds the UI and handles server-side logic including data binding, validation, and database operations.
* **JavaScript (ES6+)**
  Manages client-side functionality such as:
  * Dynamically displaying search results in tables.
  * Making asynchronous requests to backend APIs without reloading the page.
  * Capturing voice input using the Web Speech API.
  * Supporting advanced search filters and updating the UI based on user interactions.
* **HTML5 and CSS3**
  Provides responsive layout and styling for a user-friendly interface.
2. **Backend**
* **Flask (Python)**
  Lightweight service that:
  * Receives voice commands via RESTful POST requests.
  * Converts speech to text.
  * Extracts key information (names, dates, IDs) using NLP.
  * Returns structured query data for frontend searching.
* **Python NLP Tools**
  Utilized to parse and interpret voice commands:
  * **spaCy**: Performs Named Entity Recognition (NER), tokenization, and POS tagging for entities like PERSON, DATE, and LOCATION.
  * **Regular Expressions (regex)**: Detects government ID patterns, numeric ages, and classifies keywords to modules.
  * **Custom Synonym Mapping**: Resolves synonyms (e.g., “suspect” → “criminals”) for better understanding of varied user language.
3. **Database**
* **Microsoft SQL Server**
  Stores citizen and criminal records, accessed via Entity Framework Core for simplified data querying and updates.
4. **Integration and Communication**
* **RESTful API Design**
  Enables loose coupling between frontend and backend using stateless HTTP endpoints and JSON data exchange.
* **Speech Recognition and NLP Pipeline**
  1. Audio captured on frontend is sent to Flask backend.
  2. Speech recognition converts audio to text.
  3. spaCy and regex extract intents and entities into a structured dictionary.
  4. JSON response containing `module` and `entities` is sent back for frontend filtering and query handling.
//
**Key Features-**
### 1. 🎙️ **Hands-Free Voice Search**
Users can **speak naturally** to query records, eliminating the need for typing or manual input — ideal for fast, on-the-move scenarios like law enforcement or emergency response.
> **Example:**
> User says: *"Find all criminals arrested on July 15, 2023 with government ID 12345"*
> The system captures the voice, converts it to text, and extracts:
>
> * Module: **Criminals**
> * Date Arrested: **July 15, 2023**
> * Government ID: **12345**
---
### 2. 🧠 **Intelligent Multi-Entity Extraction and Combined Filtering**
Our system can identify **multiple details** within a single command—such as names, dates, ages, addresses, crimes, and IDs—and **combine all these extracted entities to filter records precisely**. This multi-entity filtering enables highly accurate and context-aware searches from complex natural language queries.
> **Example:**
> Command: *"Show me citizens named Anna, aged 30, living in Chicago with government ID A789"*
> Extracted entities:
> * Name: **Anna**
> * Age: **30**
> * Address: **Chicago**
> * Government ID: **A789**
>   The search applies all these filters simultaneously, ensuring results match all specified criteria for precise outcomes.
---
### 3. 🔎 **Fuzzy Matching for Robust Searches**
The system uses fuzzy logic to handle **imperfect inputs**—such as mispronunciations or typos—ensuring relevant records are still found.
> **Example:**
> Spoken query: *"Find citizen John Do"*
> Even if the user says "Do" instead of "Doe", fuzzy matching helps retrieve records for **"John Doe"**.
---
### 4. 🔄 **Automatic Module Switching Based on User Intent**
The backend identifies whether the query refers to **citizens** or **criminals** by detecting keywords and switches the UI tab accordingly for a seamless experience.
---
### 5. ⚡ **Real-Time Filtered Results with Highlighted Matches**
Results are returned instantly and displayed dynamically, with matched terms visually highlighted and the first result automatically focused.
---
### 6. 🗣️ **No Additional Software Required**
Built on browser-native speech recognition, the system requires no app installation or special hardware — just click the microphone and start talking.
---
### 7. 🧩 **Modular and Easily Extendable**
Though designed for police records, the architecture supports easy integration of other public safety departments like **firefighters** and **traffic enforcement** with minimal changes.
---
//
**Implementation Details**
This section outlines the full working pipeline—from voice input capture to AI-based entity extraction and final database filtering—highlighting the integration between frontend and backend components.
---
### **1. Frontend Voice Capture and Processing**
* Users initiate a search by clicking the **microphone button** on the UI.
* The **browser-native Web Speech API (`webkitSpeechRecognition`)** listens to spoken input and transcribes it to text in real-time.
* Once speech ends:
  * The transcribed text is **automatically filled into a search input field**.
  * It is then sent to the Python Flask backend via a **POST request** to the `/api/command` endpoint.
---
### **2. Backend NLP Processing (Flask + Python)**
This is the AI-driven core of the system, where natural language is interpreted and structured into meaningful query data.
#### 🛠️ **Flask as the AI Gateway**
* Flask receives transcribed speech as a POST request containing a simple JSON body:
  ```json
  {
    "command": "Find citizens named Alex from New York aged 35"
  }
  ```
* It routes this input into an NLP processing pipeline and returns a structured response.
---
### **3. AI and NLP Pipeline Breakdown**
#### 🔍 A. **Intent Detection**
* A **rule-based system** detects the user’s intention (e.g., search, lookup).
* It looks for **action verbs** like “find”, “show”, “search” to trigger filtering logic.
* It also detects which module (e.g., citizens or criminals) the query is related to.
#### 🧠 B. **Named Entity Recognition (NER) with spaCy**
* **spaCy** is used to detect structured data from free-text input:
  * `PERSON` → Names
  * `DATE` → Arrest or birth dates
  * `GPE` → Locations (e.g., cities, states)
* Example:
  ```text
  Input: "Find criminals named Mark arrested on March 15 in Boston"
  Output:
  {
    "name": "Mark",
    "crime": "unknown",
    "dateArrested": "March 15",
    "location": "Boston"
  }
  ```
#### 🧮 C. **Regex for Custom Entities**
* Regex complements spaCy for detecting:
  * `Age`: `\bage[d]? ?(\d{1,2})\b`
  * `Government IDs`: Alphanumeric patterns
  * `Custom keywords`: Like “gov ID”, “ID12345”
#### 🔄 D. **Synonym Mapping and Keyword Classification**
* A predefined `module_synonyms` dictionary handles alternate terminology:
  * “offender”, “suspect” → `"criminals"`
  * “person”, “resident” → `"citizens"`
* This enables **robust understanding of informal or varied speech patterns**.
---
### **4. Multi-Entity Extraction and Filtering**
* The system supports **multiple entity extraction** in one command:
  * Example: “Show citizens named Anna aged 30 from Chicago with ID A789”
  * Extracted into:
    ```json
    {
      "module": "citizens",
      "entities": {
        "name": "Anna",
        "age": "30",
        "address": "Chicago",
        "governmentId": "A789"
      }
    }
    ```
* All entities are stored in a Python dictionary, which is passed to the frontend for filtering.
---
### **5. JSON Response Construction**
* The backend returns a structured response:
  ```json
  {
    "module": "criminals",
    "entities": {
      "name": "Mark",
      "crime": "robbery",
      "dateArrested": "2023-05-15"
    },
    "message": "Entities successfully extracted."
  }
  ```
### **6. Frontend Module Switching and Query Triggering**
* On receiving the response:
  * The frontend automatically **switches tabs** to the appropriate module (`citizens` or `criminals`).
  * Constructs a **search filter object** using the returned entities.
  * Triggers the respective AJAX call:
    * `searchCitizen()` or `searchCriminal()`
  * Sends query parameters to the corresponding Razor Page handler.
---
### **7. Server-Side Query and Filtering (ASP.NET Core)**
* Razor Page handlers (`OnGetSearchCitizensAsync`, `OnGetSearchCriminalsAsync`) receive the query.
* Using **Entity Framework Core (EF Core)** and **LINQ**, the backend:
  * Performs **fuzzy matching** with `EF.Functions.Like()` for partial/inexact matches.
  * Applies **multi-entity filtering** — e.g., name + age + ID.
  * Falls back to a generic search if no entities are detected.
---
### **8. Dynamic Result Rendering on Frontend**
* Returned results (JSON) are:
  * Rendered into **HTML tables dynamically**.
  * **Matched terms are highlighted** for visibility.
  * The **first record is auto-scrolled and highlighted** for user focus.
  * If no matches are found, a **“No Results Found”** message is displayed.
---
✅ Final Notes
This end-to-end implementation enables hands-free, intelligent, and multi-faceted searches using real-world natural language input.
It combines the power of modern NLP (spaCy + regex) with a responsive, modular UI powered by ASP.NET Core and JavaScript.
//
  
RASA + spaCy, EntityRuler, regex
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IMPROVEMENTS-
1. Decouple Schema Extraction
schema_cache/
├── tables.json
├── entity_patterns.json

2. Use Environment Config for DB Connection
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DB_URL")

3.Add Logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Loaded {len(patterns)} entity patterns.")

4. Fallback to spaCy's Default NER
You’ve used EntityRuler only, but if a name like "Ram" isn’t in DB samples, fallback to spaCy's model NER

5. Centralize and Expand module_synonyms.json
This is a great idea. In production:
Move it to a shared config folder
Regularly expand it based on user input and logs
Add a script or interface for admins to update synonyms easily

6. Unit Test Your NLP Logic
Split out your NLP functions (extract_module, extract_intent, etc.) and write unit tests for them. 

7. assuming DB table names = modules
Create a schema_config.json. Use this for both synonym resolution and query construction — more stable than relying on introspection.

8. No Separation Between Intent Processing and Query Building
Split it into:
NLP Layer: Extracts intent, entities, module.
Query Builder Layer: Builds real queries using schema_config + business logic.


📂 A sample folder structure for a production version?

🧪 Unit test examples?

🔁 Schema sync code with cache support?


search for john
find John Doe
find Jhn De
search for maple street
Find citizen living at Maple street
show all criminals charged with theft
list people involved in murder in criminal records
Get crimes by ddd in criminal record
get all citizen records whose age is 20
find citizen named John De who is 20 years old 
find citizen record for John Doe with government id 223000
find citizen record for John Doe with address scsd
