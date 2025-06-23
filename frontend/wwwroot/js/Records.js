function switchSection(targetId) {
    const sections = document.querySelectorAll('.section');
    const tabs = document.querySelectorAll('.tab');

    sections.forEach(s => s.classList.remove('active'));
    tabs.forEach(t => t.classList.remove('active'));

    document.getElementById(targetId).classList.add('active');
    event.target.classList.add('active');
}
function switchSection(section) {
    document.querySelectorAll('.tab, .section').forEach(el => el.classList.remove('active'));

    const tab = document.querySelector(`.tab[onclick*="${section}"]`);
    const content = document.getElementById(section);

    if (tab) tab.classList.add('active');
    else console.warn(`No tab found for: ${section}`);

    if (content) content.classList.add('active');
    else console.warn(`No section found with id="${section}"`);
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
            tbody.innerHTML = "";

            if (!data || data.length === 0) {
                tbody.innerHTML = "<tr><td colspan='4'>No records found</td></tr>";
                return;
            }

            data.forEach(c => {
                tbody.innerHTML += `
                    <tr>
                        <td>${c.name || c.Name}</td>
                        <td>${c.age || c.Age}</td>
                        <td>${c.address || c.Address}</td>
                        <td>${c.governmentId || c.GovernmentId}</td>
                    </tr>`;
            });
        })
        .catch(err => console.error("❌ Citizen search failed:", err));
}

// Same for searchCriminal
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
            tbody.innerHTML = "";

            if (data.length === 0) {
                tbody.innerHTML = "<tr><td colspan='4'>No matching criminals found</td></tr>";
                return;
            }

            data.forEach(c => {
                const formattedDate = c.dateArrested ? new Date(c.dateArrested).toLocaleDateString() : '';
                tbody.innerHTML += `
                    <tr>
                        <td>${c.name || c.Name}</td>
                        <td>${c.crime || c.Crime}</td>
                        <td>${formattedDate}</td>
                        <td>${c.governmentId || c.GovernmentId}</td>
                    </tr>`;
            });
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

            // Map plural to singular section IDs
            const moduleMap = {
                "citizens": "citizen",
                "criminals": "criminal"
            };

            const module = data.module?.toLowerCase();
            const sectionId = moduleMap[module];

            if (sectionId) {
                switchSection(sectionId);

                // Auto-fill search input and trigger search
                // Auto-fill search input and trigger search
                const entities = data.entities || {};
                let queryParts = [];

                if (entities.name) queryParts.push(entities.name);
                if (entities.governmentid) queryParts.push(entities.governmentid);
                if (entities.address) queryParts.push(entities.address);
                if (entities.age) queryParts.push(entities.age);
                if (entities.crime) queryParts.push(entities.crime);
                if (entities.formattedDate) queryParts.push(entities.formattedDate);
                let query = queryParts.join(" ");


                if (sectionId === "citizen") {
                    document.getElementById("citizenSearchInput").value = query;
                    searchCitizen();
                } else if (sectionId === "criminal") {
                    document.getElementById("criminalSearchInput").value = query;
                    searchCriminal();
                }
            } else {
                console.warn("❗ Unknown module:", module);
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

