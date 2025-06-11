from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, inspect, text
import spacy
import difflib
import json
import os
from spacy.pipeline import EntityRuler

app = Flask(__name__)
CORS(app)

# -------- CONFIGURE YOUR SQL SERVER CONNECTION HERE --------
DATABASE_URL = (
    "mssql+pyodbc://@localhost/PoliceRMS"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
    "&Encrypt=no"
)

# Create SQLAlchemy engine and inspector
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)
# Load synonym map from JSON file
with open(os.path.join(os.path.dirname(__file__), "module_synonyms.json")) as f:
    synonym_map = json.load(f)

# Create reverse lookup map for quick access
synonym_to_module = {}
for module, syns in synonym_map.items():
    synonym_to_module[module.lower()] = module.lower()  # direct match
    for syn in syns:
        synonym_to_module[syn.lower()] = module.lower()

# Load SpaCy English model
nlp = spacy.load("en_core_web_md")

def map_column_to_entity(col_name):
    col_name = col_name.lower()
    if any(x in col_name for x in ['name']):
        return "PERSON"
    if any(x in col_name for x in ['id', 'govt_id', 'ssn', 'number']):
        return "GOV_ID"  # better label for ID numbers
    if any(x in col_name for x in ['date', 'dob', 'timestamp']):
        return "DATE"
    if any(x in col_name for x in ['location', 'address', 'city']):
        return "LOCATION"
    return None


def get_sample_values(table, column, limit=50):
    query = text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL")
    with engine.connect() as conn:
        result = conn.execute(query).fetchmany(limit)
    return [str(row[0]) for row in result if row[0]]

def build_dynamic_patterns():
    modules = inspector.get_table_names()
    patterns = []

    for table in modules:
        # Add the table name as a MODULE entity pattern
        patterns.append({"label": "MODULE", "pattern": table.lower()})

        columns = inspector.get_columns(table)
        for col in columns:
            col_name = col['name']
            entity_label = map_column_to_entity(col_name)
            if entity_label:
                sample_values = get_sample_values(table, col_name)
                # Add sample values as entity patterns
                for val in sample_values:
                    # Avoid patterns with empty or very short values
                    if val and len(val) > 1:
                        patterns.append({"label": entity_label, "pattern": val.lower()})

    return patterns

# Build and add EntityRuler with dynamic patterns
patterns = build_dynamic_patterns()
ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": True})
ruler.add_patterns(patterns)

def extract_intent(text):
    text = text.lower()
    if any(x in text for x in ['search', 'find', 'lookup', 'display', 'show', 'get', 'fetch']):
        return "search"
    if any(x in text for x in ['add', 'insert', 'create']):
        return "add"
    if any(x in text for x in ['update', 'modify', 'change']):
        return "update"
    if any(x in text for x in ['delete', 'remove']):
        return "delete"
    return "unknown"
def extract_module(text, table_names):
    text = text.lower()

    # Step 1: Check if any table name is a substring in the command
    for table in table_names:
        if table.lower() in text:
            return table.lower()

    # Step 2: Check against synonym map
    for word in text.split():
        if word in synonym_to_module:
            return synonym_to_module[word]

    # Step 3: Use semantic similarity fallback if model supports it
    doc = nlp(text)
    best_match = "general"
    best_score = 0.7  # minimum similarity threshold

    for table in table_names:
        table_doc = nlp(table.lower())
        # Compute similarity between the table name and each token in the command
        similarities = [token.similarity(table_doc) for token in doc if token.has_vector and table_doc.has_vector]
        if similarities:
            max_sim = max(similarities)
            if max_sim > best_score:
                best_score = max_sim
                best_match = table.lower()

    return best_match



@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get("command", "").strip()

    if not command:
        return jsonify({"error": "No command provided"}), 400

    doc = nlp(command)
    entities = {}

    # Get all DB tables once
    table_names = inspector.get_table_names()

    # Step 1: Try to find module from recognized entities (MODULE label)
    module = None
    for ent in doc.ents:
        if ent.label_ == "MODULE":
            module = ent.text.lower()
            break

    # Step 2: If no module was found from entities, use fuzzy matching
    if not module:
        module = extract_module(command, table_names)

    # Step 3: Extract all other entities (excluding MODULE)
    for ent in doc.ents:
        label = ent.label_
        text = ent.text

        # Prioritize EntityRuler, but fall back to spaCy's built-in PERSON detection
        if label == "PERSON" or label.lower() in ["person", "gov_id", "date", "location"]:
            entities.setdefault(label.lower(), []).append(text)
        elif label != "MODULE":
            entities.setdefault(label.lower(), []).append(text)

    # Extract intent
    intent = extract_intent(command)

    # Response
    response = {
        "message": f"Command processed: '{command}'",
        "intent": intent,
        "module": module,
        "entities": entities
    }

    return jsonify(response)

if __name__ == '__main__':
    print(f"Loaded {len(patterns)} dynamic entity patterns from your DB schema.")
    app.run(debug=True)
