from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, inspect, text
import spacy
import difflib
import json
import os
import threading
import time
import logging
import rapidfuzz
from rapidfuzz import process, fuzz
import jellyfish
import usaddress
from spacy.tokens import Span
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
# -------- CONFIGURE SQL SERVER CONNECTION --------
DATABASE_URL = (
    "mssql+pyodbc://@localhost/PoliceRMS"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
    "&Encrypt=no"
)
cached_db_values = {}
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
    "gpe": "address",
    "location": "address",
    "facility": "address",
    "org": "location",  
    "organization": "address",
    "person": "name",
    "name": "name",
    "date": "date",
    "time": "time",
    "cardinal": "age",
    "phone": "phone_number",
    "email": "email",
    "governmentid": "governmentid",
    "govid": "governmentid"
}

# ---------------- PATTERN BUILDING -------------------
def get_sample_values(table, column, limit=50):
    query = text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL")
    with engine.connect() as conn:
        result = conn.execute(query).fetchmany(limit)
    return [str(row[0]) for row in result if row[0]]

def normalize_address(addr):
    # Lowercase, remove commas, normalize spaces
    return " ".join(addr.lower().replace(",", " ").split())

def normalize_us_address(addr):
    try:
        parsed = usaddress.tag(addr)[0]
        parts = [v.lower() for k, v in parsed.items()]
        return " ".join(parts)
    except usaddress.RepeatedLabelError:
        return addr.lower()

def refresh_cached_db_values():
    global cached_db_values
    cached_db_values = {}
    patterns = []

    for table in inspector.get_table_names():
        table_lower = table.lower()
        cached_db_values[table_lower] = {}
        patterns.append({"label": "MODULE", "pattern": table_lower})

        for col in inspector.get_columns(table):
            col_name_lower = col['name'].lower()
            samples = get_sample_values(table, col['name'])
            cached_db_values[table_lower][col_name_lower] = samples

            for val in samples:
                if val and len(str(val)) > 1:
                    val_norm = normalize_address(str(val))
                    # Add full normalized pattern
                    patterns.append({"label": col['name'].upper(), "pattern": val_norm})

                    # If it's likely an address column, add a few partials
                    if "address" in col_name_lower or "location" in col_name_lower:
                        parts = val_norm.split()
                        # Add only bigrams to avoid overloading patterns
                        for i in range(len(parts) - 1):
                            bigram = f"{parts[i]} {parts[i+1]}"
                            patterns.append({"label": col['name'].upper(), "pattern": bigram})

    # Keep name patterns generation unchanged
    patterns += get_name_patterns()

    return patterns


def get_name_patterns():
    name_patterns = []
    citizens_key = "citizens"
    if citizens_key in cached_db_values:
        for name in cached_db_values[citizens_key].get('name', []):
            if name and len(name.strip()) > 1:
                name_patterns.append({"label": "PERSON", "pattern": name.lower()})
    return name_patterns

def add_generic_patterns():
    return [
        {"label": "PHONE", "pattern": [{"TEXT": {"REGEX": r"\d{3}-\d{3}-\d{4}"}}]},
        {"label": "EMAIL", "pattern": [{"TEXT": {"REGEX": r".+@.+\..+"}}]},
        {"label": "DATE", "pattern": [{"TEXT": {"REGEX": r"\d{1,2}/\d{1,2}/\d{2,4}"}}, {"TEXT": {"REGEX": r"last week|today|yesterday|this month|this week"}}]},
        {"label": "GOVERNMENTID", "pattern": [{"TEXT": {"REGEX": r"CID\d{3,}"}}]},
        {"label": "LOCATION", "pattern": [{"LOWER": {"REGEX": r"\d+(st|nd|rd|th)\s+(avenue|street|road|blvd|lane)"}}]},
        {"label": "NAME", "pattern": [{"TEXT": {"REGEX": r"^[A-Z][a-z]+$"}}]},             
    ]

# Add patterns to NER (entity ruler) - keep overwrite_ents=False to keep SpaCy NER too
if "entity_ruler" in nlp.pipe_names:
    nlp.remove_pipe("entity_ruler")
ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": False})
ruler.add_patterns(refresh_cached_db_values() + add_generic_patterns())
# -------------------- AUTO REFRESH THREAD --------------------
def auto_refresh_cache(interval_minutes=10):
    while True:
        print("[AutoRefresh] Refreshing DB cache...")
        refresh_cached_db_values()
        time.sleep(interval_minutes * 60)

threading.Thread(target=auto_refresh_cache, daemon=True).start()

# ------------------ NLP UTILITIES ----------------
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
    doc = nlp(text)

    # Direct DB table match
    for table in table_names:
        if table.lower() in text:
            return table.lower()

    # Synonym or fuzzy match
    for token in doc:
        word = token.text.lower()
        if word in synonym_to_module:
            return synonym_to_module[word]

    # Fuzzy match with synonym keys
    for token in doc:
        matches = difflib.get_close_matches(token.text.lower(), synonym_to_module.keys(), n=1, cutoff=0.8)
        if matches:
            return synonym_to_module[matches[0]]

    # If still nothing, fallback to keyword-style guess (like 'fire', 'traffic')
    for token in doc:
        if token.pos_ == "NOUN":
            return token.text.lower()

    return "general"

def fix_gpe_to_person(ents):
    fixed_ents = []
    for ent in ents:
        if ent.label_ == "GPE" and ent.text.istitle() and len(ent.text.split()) == 1:
            fixed_ents.append((ent.text, "PERSON"))
        else:
            fixed_ents.append((ent.text, ent.label_))
    return fixed_ents

def clean_entity_text(text):
    stop_words = {"for", "in", "with", "the", "a", "an", "of"}
    tokens = text.lower().strip().split()
    filtered_tokens = [t for t in tokens if t not in stop_words]
    return " ".join(filtered_tokens).strip()

def fuzzy_match_entity_to_db(entity_text, candidates, cutoff=60):
    if not candidates:
        return None

    entity_text_lower = entity_text.lower().strip()
    address_keywords = ["street", "st", "avenue", "ave", "road", "rd", "lane", "ln", "blvd", "boulevard"]
    is_address = "," in entity_text_lower or any(word in entity_text_lower for word in address_keywords)

    if is_address:
        # Normalize address input and candidate values
        entity_norm = normalize_us_address(entity_text)
        candidates_norm = [normalize_us_address(c) for c in candidates]

        # Try token_set_ratio with normalized values
        match = process.extractOne(entity_norm, candidates_norm, scorer=fuzz.token_set_ratio, score_cutoff=cutoff)
        if match:
            idx = candidates_norm.index(match[0])
            return candidates[idx]

        # Fallback: partial string match
        for candidate, cand_norm in zip(candidates, candidates_norm):
            if entity_norm in cand_norm or cand_norm in entity_norm:
                return candidate

        # Last fallback: Jaro-Winkler similarity
        best_score = 0
        best_match = None
        for candidate, cand_norm in zip(candidates, candidates_norm):
            score = jellyfish.jaro_winkler_similarity(entity_norm, cand_norm)
            if score > best_score and score >= cutoff / 100:
                best_score = score
                best_match = candidate
        return best_match

    else:
        # Keep your name and other string logic intact
        candidates_lower = [c.lower() for c in candidates]
        match = process.extractOne(entity_text_lower, candidates_lower, scorer=fuzz.token_sort_ratio, score_cutoff=cutoff)
        if match:
            idx = candidates_lower.index(match[0])
            return candidates[idx]

        for candidate, cand_lower in zip(candidates, candidates_lower):
            if entity_text_lower in cand_lower or cand_lower in entity_text_lower:
                return candidate

        # Optional final fallback for names: Jaro-Winkler
        best_score = 0
        best_match = None
        for candidate in candidates:
            score = jellyfish.jaro_winkler_similarity(entity_text_lower, candidate.lower())
            if score > best_score and score >= cutoff / 100:
                best_score = score
                best_match = candidate
        return best_match

# -------------------- STRUCTURED QUERY --------------------
def build_structured_query(command):
    doc = nlp(command)

    # Merge adjacent PERSON/NAME tokens
    new_ents, skip = [], False
    ents = list(doc.ents)
    for i, ent in enumerate(ents):
        if skip:
            skip = False
            continue
        if i + 1 < len(ents):
            nxt = ents[i + 1]
            if ent.label_ in ("PERSON", "NAME") and nxt.label_ in ("PERSON", "NAME") and nxt.start == ent.end:
                new_ents.append(Span(doc, ent.start, nxt.end, label=ent.label_))
                skip = True
                continue
        new_ents.append(ent)
    doc.ents = tuple(new_ents)

    fixed_entities = fix_gpe_to_person(doc.ents)
    module = extract_module(command, inspector.get_table_names())
    module = module.lower()
    if module not in cached_db_values:
        module = "citizens"
    entities = {}

    print("\n🔎 Processing command:", command)
    print("Detected module:", module)
    print("Detected raw entities:", fixed_entities)

    for ent_text, ent_label in fixed_entities:
        norm_label = ENTITY_LABEL_MAP.get(ent_label.lower(), ent_label.lower())
        if norm_label == "module":
            continue
        cleaned_text = clean_entity_text(ent_text)
        if norm_label == "name" and any(addr_kw in cleaned_text for addr_kw in ["street", "avenue", "road", "lane", "ny", "st"]):
            norm_label = "address"
    
        corrected_value = cleaned_text

        print(f"\n→ Entity: '{ent_text}' (cleaned: '{cleaned_text}') as '{norm_label}'")

        if norm_label in ["name", "address"] and module in cached_db_values:
            module_columns = cached_db_values[module]
            print("Available columns:", list(module_columns.keys()))

            for col_name, values in module_columns.items():
                col_name_lower = col_name.lower()
                if norm_label in col_name_lower or col_name_lower in norm_label:
                    print(f"  Trying column '{col_name}', sample values:", values[:5])
                    match = fuzzy_match_entity_to_db(cleaned_text, values, cutoff=60)
                    print("    Fuzzy match result:", match)
                    if match:
                        corrected_value = match
                        print(f"✅ Corrected to '{corrected_value}' from column '{col_name}'")
                        break
            else:
                print(f"❌ No fuzzy match found for '{cleaned_text}' in columns for label '{norm_label}'")

        # Add to entities
        entities[norm_label] = corrected_value
        print(f"Stored entity '{norm_label}': '{corrected_value}'")

    print("🔁 Final entities:", entities)
    return {
        "message": f"Command processed: '{command}'",
        "intent": extract_intent(command),
        "module": module,
        "entities": entities
    }

 # -------------------- ROUTES --------------------
@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get("command", "").strip()
    if not command:
        return jsonify({"error": "No command provided"}), 400

    result = build_structured_query(command)
    return jsonify(result)

if __name__ == '__main__':
    print("Server starting...")
    app.run(debug=True)
