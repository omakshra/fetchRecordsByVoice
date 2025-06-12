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

# -------- CONFIGURE SQL SERVER CONNECTION --------
DATABASE_URL = (
    "mssql+pyodbc://@localhost/PoliceRMS"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
    "&Encrypt=no"
)
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

# Load synonym map
with open(os.path.join(os.path.dirname(__file__), "module_synonyms.json")) as f:
    synonym_map = json.load(f)
synonym_to_module = {syn.lower(): module.lower() for module, syns in synonym_map.items() for syn in [module] + syns}

# Load SpaCy model
def load_spacy_model():
    try:
        return spacy.load("en_core_web_md")
    except OSError:
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

# Label normalization
ENTITY_LABEL_MAP = {
    "gpe": "location",
    "person": "name",
    "org": "organization",
    "date": "date",
    "time": "time",
    "cardinal": "age",
    "phone": "phone_number",
    "email": "email"
}

def get_sample_values(table, column, limit=50):
    query = text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL")
    with engine.connect() as conn:
        result = conn.execute(query).fetchmany(limit)
    return [str(row[0]) for row in result if row[0]]

def build_dynamic_patterns():
    patterns = []
    for table in inspector.get_table_names():
        patterns.append({"label": "MODULE", "pattern": table.lower()})
        for col in inspector.get_columns(table):
            samples = get_sample_values(table, col['name'])
            for val in samples:
                if val and len(str(val)) > 1:
                    patterns.append({"label": col['name'].upper(), "pattern": val.lower()})
    return patterns

def add_generic_patterns():
    return [
        {"label": "PHONE", "pattern": [{"TEXT": {"REGEX": r"\d{3}-\d{3}-\d{4}"}}]},
        {"label": "EMAIL", "pattern": [{"TEXT": {"REGEX": r".+@.+\..+"}}]},
        {"label": "DATE", "pattern": [{"TEXT": {"REGEX": r"\d{1,2}/\d{1,2}/\d{2,4}"}}]},
        {"label": "NAME", "pattern": [{"TEXT": {"REGEX": r"^[A-Z][a-z]+$"}}]},
    ]

# Add patterns to NER (entity ruler) - keep overwrite_ents=False to keep SpaCy NER too
if "entity_ruler" in nlp.pipe_names:
    nlp.remove_pipe("entity_ruler")
ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": False})
ruler_patterns = build_dynamic_patterns() + add_generic_patterns()
ruler.add_patterns(ruler_patterns)

def extract_intent(text):
    text = text.lower()
    if any(x in text for x in ['search', 'find', 'lookup', 'display', 'show', 'get', 'fetch', 'list']):
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
    doc = nlp(text)
    # Direct match
    for table in table_names_lower:
        if table in text:
            return table
    # Exact or fuzzy synonym match
    for word in text.split():
        if word in synonym_to_module:
            return synonym_to_module[word]
        matches = difflib.get_close_matches(word, synonym_to_module.keys(), n=1, cutoff=0.8)
        if matches:
            return synonym_to_module[matches[0]]
    # Semantic similarity for module names
    for table in table_names_lower:
        table_doc = nlp(table)
        sim_scores = [token.similarity(table_doc) for token in doc if token.has_vector and table_doc.has_vector]
        if sim_scores and max(sim_scores) >= 0.7:
            return table
    # Fuzzy fallback
    fuzzy_matches = difflib.get_close_matches(text, table_names_lower, n=1, cutoff=0.75)
    if fuzzy_matches:
        return fuzzy_matches[0]
    return "general"

def fix_gpe_to_person(ents):
    fixed_ents = []
    for ent in ents:
        if ent.label_ == "GPE" and ent.text.istitle() and len(ent.text.split()) == 1:
            fixed_ents.append((ent.text, "PERSON"))
        else:
            fixed_ents.append((ent.text, ent.label_))
    return fixed_ents

def fuzzy_match_entity_to_db(entity_text, candidates, cutoff=0.7):

    if not candidates:
        return None
    # Use difflib first for quick match
    matches = difflib.get_close_matches(entity_text.lower(), [c.lower() for c in candidates], n=1, cutoff=cutoff)
    if matches:
        return matches[0]
    # If no difflib match, fallback to SpaCy similarity
    entity_doc = nlp(entity_text)
    best_score = 0
    best_match = None
    for candidate in candidates:
        candidate_doc = nlp(candidate)
        if entity_doc.has_vector and candidate_doc.has_vector:
            score = entity_doc.similarity(candidate_doc)
            if score > best_score and score >= cutoff:
                best_score = score
                best_match = candidate
    return best_match

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get("command", "").strip()
    if not command:
        return jsonify({"error": "No command provided"}), 400

    doc = nlp(command)
    # Fix GPEs that look like persons
    fixed_entities = fix_gpe_to_person(doc.ents)

    # Get DB tables and their columns
    table_names = inspector.get_table_names()
    table_column_map = {
        table: [col['name'].lower() for col in inspector.get_columns(table)]
        for table in table_names
    }

    # Step 1: find module from entities or command text
    module = None
    for text, label in fixed_entities:
        if label.upper() == "MODULE" and text.lower() in table_names:
            module = text.lower()
            break
    if not module:
        module = extract_module(command, table_names)

    # Step 2: collect all possible DB values for fuzzy matching per column for the detected module
    module_db_values = []
    if module in table_column_map:
        for col in table_column_map[module]:
            module_db_values.extend(get_sample_values(module, col, limit=50))

    # Step 3: extract entities with fuzzy matching against DB where possible
    entities = {}
    for ent_text, ent_label in fixed_entities:
        raw_label = ent_label.lower()
        if raw_label == "module":
            continue

        # Normalize label if possible
        norm_label = ENTITY_LABEL_MAP.get(raw_label, raw_label)

        # Fuzzy match entity text to DB values if possible (except for generic labels like date/time/phone/email)
        if norm_label not in ['date', 'time', 'phone_number', 'email']:
            # Try fuzzy match against module DB values
            matched_value = fuzzy_match_entity_to_db(ent_text, module_db_values)
            if matched_value:
                ent_text = matched_value  # Replace with matched DB value

        # Merge entities if multiple values for same label
        if norm_label in entities:
            if isinstance(entities[norm_label], list):
                if ent_text not in entities[norm_label]:
                    entities[norm_label].append(ent_text)
            else:
                if entities[norm_label] != ent_text:
                    entities[norm_label] = [entities[norm_label], ent_text]
        else:
            entities[norm_label] = ent_text

    # Step 4: extract intent
    intent = extract_intent(command)

    response = {
        "message": f"Command processed: '{command}'",
        "intent": intent,
        "module": module,
        "entities": entities
    }
    return jsonify(response)

if __name__ == '__main__':
    print("Server starting...")
    app.run(debug=True)
