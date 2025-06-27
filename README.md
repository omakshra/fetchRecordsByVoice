Problem Statement-
In public safety domains like law enforcement, firefighting, and traffic control, quick access to records is essential for timely decision-making. Traditional Record Management Systems (RMS) rely on manual input, which can be slow or impractical when officers are on the move or handling emergencies. This creates a need for a voice-activated interface that allows hands-free, natural language access to records, improving efficiency and response times in the field.
//
Proposed Solution-
A voice-enabled search feature was integrated into a simulated police records module. The system processes spoken natural language commands to extract both user intent and multiple relevant entities—such as names, government IDs, and address—which are then mapped into the existing search workflow. This allows for accurate and dynamic retrieval of citizen and criminal records based on contextual input. The solution supports moderately complex queries and enhances hands-free usability. While currently applied to the police module, the design is scalable and can be extended to other domains within a public RMS, such as fire and traffic departments.
//
System Workflow--
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
Technology Stack-
1. Frontend
* **ASP.NET Core Razor Pages**
  Used to build the user interface and handle server-side logic, including data binding, model validation, and database operations.
* **JavaScript (ES6+)**
  Manages client-side functionality such as:
  * Dynamically displaying search results in tables.
  * Making asynchronous requests to backend APIs without reloading the page.
  * Capturing voice input using the Web Speech API.
  * Supporting advanced search filters and updating the UI based on user interactions.
* **HTML5 and CSS3**
  Provides the structure and styling for a responsive and user-friendly interface.
2. Backend
* **Flask (Python)**
  Acts as a lightweight backend service responsible for:
  * Receiving voice commands from the frontend.
  * Converting speech to text.
  * Extracting key information (like names, dates, IDs) from the text using NLP techniques.
  * Returning structured query data that the frontend uses to search records.
* **Python NLP Tools**
  Utilized for identifying important details and understanding the context in voice commands.
3. Database
* **Microsoft SQL Server**
  Stores citizen and criminal records. The application accesses it through Entity Framework Core, which simplifies querying and updating the database.
4. Integration and Communication
* **RESTful API Design**
  Facilitates loosely coupled communication between frontend and backend components:
  * Stateless HTTP endpoints following REST conventions.
  * JSON is used as the data interchange format for commands, search filters, and query results.
  * Asynchronous fetch requests ensure non-blocking UI updates and real-time responsiveness.
* **Speech Recognition and NLP Pipeline**
  The audio input captured on the frontend is sent to the Flask service where:
  * Speech recognition converts audio into text.
  * NLP processes the text to identify user intent and extract multiple entities simultaneously.
  * The structured output is relayed back to the frontend, which translates it into query parameters for existing search APIs.

//
Key Features-
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
