from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, inspect, text
import spacy
import difflib
import json
import os
import requests
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
    # Use the column name itself as the label (uppercase)
    return col_name.strip().upper()

def get_sample_values(table, column, limit=50):
    query = text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL")
    with engine.connect() as conn:
        result = conn.execute(query).fetchmany(limit)
    return [str(row[0]) for row in result if row[0]]

def build_dynamic_patterns():
    modules = inspector.get_table_names()
    patterns = []
    for table in modules:
        patterns.append({"label": "MODULE", "pattern": table.lower()})
        columns = inspector.get_columns(table)
        for col in columns:
            col_name = col['name']
            entity_label = map_column_to_entity(col_name)
            # Add the column name itself as a pattern (e.g., "age")
            patterns.append({"label": entity_label, "pattern": col_name.lower()})
            # Sample values (e.g., 60, "male", etc.)
            sample_values = get_sample_values(table, col_name)
            for val in sample_values:
                if val and len(str(val)) > 1:
                    patterns.append({"label": entity_label, "pattern": str(val).lower()})
    return patterns
# Build and add EntityRuler with dynamic patterns
patterns = build_dynamic_patterns()
ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": True})
ruler.add_patterns(patterns)

def extract_intent(text):
    text = text.lower()
    if any(x in text for x in ['search', 'find', 'lookup', 'display', 'show', 'get', 'fetch','list']):
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
    table_names_lower = [t.lower() for t in table_names]
    # Step 1: Direct substring match against table names
    for table in table_names_lower:
        if table in text:
            return table
    # Step 2: Exact synonym match against each word
    for word in text.split():
        if word in synonym_to_module:
            return synonym_to_module[word]
    # Step 2b: Fuzzy synonym match on each word in the text
    words = text.split()
    synonym_keys = list(synonym_to_module.keys())
    for word in words:
        matches = difflib.get_close_matches(word, synonym_keys, n=1, cutoff=0.8)
        if matches:
            return synonym_to_module[matches[0]]
    # Step 3a: Semantic similarity using spaCy on table names
    doc = nlp(text)
    best_sem_match = "general"
    best_sem_score = 0.7
    for table in table_names_lower:
        table_doc = nlp(table)
        similarities = [token.similarity(table_doc) for token in doc if token.has_vector and table_doc.has_vector]
        if similarities:
            max_sim = max(similarities)
            if max_sim > best_sem_score:
                best_sem_score = max_sim
                best_sem_match = table
    # Step 3b: Fuzzy matching on table names
    fuzzy_matches = difflib.get_close_matches(text, table_names_lower, n=1, cutoff=0.8)
    best_fuzzy_match = fuzzy_matches[0] if fuzzy_matches else "general"
    # Decide which is better
    if best_sem_match != "general":
        return best_sem_match
    elif best_fuzzy_match != "general":
        return best_fuzzy_match
    else:
        return "general"

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
    # Build a map of table → column names for filtering
    table_column_map = {
        table: [col['name'].lower() for col in inspector.get_columns(table)]
        for table in table_names
    }
    # Step 3: Extract all other entities (excluding MODULE)
    for ent in doc.ents:
        label = ent.label_.lower()
        value = ent.text.lower()
        # Skip MODULE entities
        if label == "module":
            continue
        # Skip column name being used as its own value
        if module in table_column_map and value in table_column_map[module]:
            continue
        entities.setdefault(label, []).append(ent.text)
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
