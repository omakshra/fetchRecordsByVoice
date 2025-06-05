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

// Run on page load: check query param ?tab=...
window.onload = function () {
    const params = new URLSearchParams(window.location.search);
    const tab = params.get('tab') || 'citizen'; // default to citizen
    switchSection(tab);
};