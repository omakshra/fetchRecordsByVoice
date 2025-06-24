function switchSection(sectionId) {
    document.querySelectorAll('.tab, .section').forEach(el => el.classList.remove('active'));

    const tab = document.querySelector(`.tab[onclick*="${sectionId}"]`);
    const content = document.getElementById(sectionId);

    if (tab) tab.classList.add('active');
    else console.warn(`No tab found for: ${sectionId}`);

    if (content) content.classList.add('active');
    else console.warn(`No section found with id="${sectionId}"`);
}


function renderTableRows(data, tbody, fields, highlightTerm = "") {
    tbody.innerHTML = "";

    if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan='${fields.length}'>No matching records found</td></tr>`;
        return;
    }

    const highlightRegex = highlightTerm
        ? new RegExp(`(${escapeRegExp(highlightTerm)})`, "gi")
        : null;

    let firstRow;

    data.forEach(item => {
        const row = tbody.insertRow();

        fields.forEach(field => {
            const value = item[field] || item[field.toLowerCase()] || "";
            const cell = row.insertCell();
            if (highlightRegex) {
                cell.innerHTML = String(value).replace(highlightRegex, "<mark>$1</mark>");
            } else {
                cell.textContent = value;
            }
        });

        if (!firstRow) firstRow = row;
    });

    if (firstRow) {
        firstRow.classList.add("auto-highlight");
        firstRow.scrollIntoView({ behavior: "smooth", block: "center" });
    }
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
// Update searchCitizen to accept filters
function searchCitizen(filters = {}) {
    // Build query string from filters object or fallback to input value
    let query = filters.query || document.getElementById("citizenSearchInput").value.trim();

    // Also allow specific fields like name, age, governmentId
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    for (const key of ['name', 'age', 'governmentId', 'address']) {
        if (filters[key]) params.append(key, filters[key]);
    }

    fetch(`/Records?handler=SearchCitizens&${params.toString()}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("citizenTableBody");
            const fields = ['name', 'age', 'address', 'governmentId'];
            renderTableRows(data, tbody, fields, query);
        })
        .catch(err => console.error("❌ Citizen search failed:", err));
}

// Fixed searchCriminal
function searchCriminal(filters = {}) {
    const query = filters.query || document.getElementById("criminalSearchInput").value.trim();

    const params = new URLSearchParams();
    if (query) params.append('query', query);
    for (const key of ['name', 'crime', 'governmentId']) {
        if (filters[key]) params.append(key, filters[key]);
    }

    fetch(`/Records?handler=SearchCriminals&${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById("criminalTableBody");

            data.forEach(c => {
                if (c.dateArrested) {
                    c.dateArrested = new Date(c.dateArrested).toLocaleDateString();
                }
            });

            const fields = ['name', 'crime', 'dateArrested', 'governmentId'];
            renderTableRows(data, tbody, fields, query);
        })
        .catch(err => console.error("❌ Criminal search failed:", err));
}

// Modified sendCommand to switch tab and call search with filters
function sendCommand() {
    const command = document.getElementById("commandInput").value.trim();
    if (!command) {
        alert("Please enter a command");
        return;
    }

    fetch('http://localhost:5000/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
    })
        .then(res => res.json())
        .then(data => {
            console.log("✅ Flask says:", data.message);
            document.getElementById("status").textContent = JSON.stringify(data, null, 2);

            const moduleMap = {
                "citizens": "citizen",
                "criminals": "criminal"
            };

            const module = data.module?.toLowerCase();
            const sectionId = moduleMap[module] || 'citizen'; // fallback to citizen

            if (!sectionId) {
                console.warn("❗ Unknown module:", module);
                return;
            }

            switchSection(sectionId);

            const entities = data.entities || {};
            const filters = {};

            // Copy relevant filters from entities with lowercase keys
            for (const key in entities) {
                filters[key.toLowerCase()] = Array.isArray(entities[key])
                    ? entities[key].join(" ")
                    : entities[key];
            }

            // Compose a query string for highlighting, joining all entity values
            filters.query = Object.values(filters).join(" ");

            // Update input and trigger filtered search with filters
            if (sectionId === "citizen") {
                document.getElementById("citizenSearchInput").value = filters.query;
                searchCitizen(filters);
            } else if (sectionId === "criminal") {
                document.getElementById("criminalSearchInput").value = filters.query;
                searchCriminal(filters);
            }
        })
        .catch(err => {
            console.error("❌ Command failed:", err);
            document.getElementById("status").textContent = "Error sending command.";
        });
}

const recordBtn = document.getElementById("recordBtn");
let recognition;

if (!('webkitSpeechRecognition' in window)) {
    if (recordBtn) {
        recordBtn.disabled = true;
        recordBtn.textContent = "🎤 Not Supported";
    }
} else {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        recordBtn.textContent = "🎤 Listening...";
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("commandInput").value = transcript;
        sendCommand(); // Call the function to send to Flask
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        recordBtn.textContent = "🎤 Start Recording";
    };

    recognition.onend = () => {
        recordBtn.textContent = "🎤 Start Recording";
    };

    recordBtn.onclick = () => {
        recognition.start();
    };
}


// Run on page load: check query param ?tab=...
window.onload = function () {
    const params = new URLSearchParams(window.location.search);
    const tab = params.get('tab') || 'citizen'; // default to citizen
    switchSection(tab);
};

