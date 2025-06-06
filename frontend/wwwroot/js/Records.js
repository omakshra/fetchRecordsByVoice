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
    document.querySelector(`.tab[onclick*="${section}"]`).classList.add('active');
    document.getElementById(section).classList.add('active');
}
function searchCitizen() {
    const query = document.getElementById("citizenSearchInput").value;

    fetch(`/Records?handler=SearchCitizens&query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            console.log("✅ Filtered data:", data); // Debug check

            const tbody = document.getElementById("citizenTableBody");
            tbody.innerHTML = "";

            if (!data || data.length === 0) {
                tbody.innerHTML = "<tr><td colspan='4'>No records found</td></tr>";
                return;
            }

            data.forEach(c => {
                tbody.innerHTML += `
                    <tr>
                        <td>${c.name}</td>
                        <td>${c.age}</td>
                        <td>${c.address}</td>
                        <td>${c.governmentId}</td>
                    </tr>`;
            });
        })
        .catch(error => console.error("❌ Fetch failed:", error));
}

function searchCriminal() {
    const query = document.getElementById("criminalSearchInput").value;

    fetch(`/Records?handler=SearchCriminals&query=${encodeURIComponent(query)}`)

        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById("criminalTableBody");
            tbody.innerHTML = "";

            if (data.length === 0) {
                tbody.innerHTML = "<tr><td colspan='4'>No matching criminals found</td></tr>";
                return;
            }

            data.forEach(c => {
                const formattedDate = new Date(c.dateArrested).toLocaleDateString();
                tbody.innerHTML += `
                    <tr>
                        <td>${c.name}</td>
                        <td>${c.crime}</td>
                        <td>${formattedDate}</td>
                        <td>${c.governmentId}</td>
                    </tr>`;
            });
        })
        .catch(err => console.error("❌ Criminal search failed:", err));
}


// Run on page load: check query param ?tab=...
window.onload = function () {
    const params = new URLSearchParams(window.location.search);
    const tab = params.get('tab') || 'citizen'; // default to citizen
    switchSection(tab);
};

