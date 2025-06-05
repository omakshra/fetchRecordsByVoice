function switchSection(targetId) {
    const sections = document.querySelectorAll('.section');
    const tabs = document.querySelectorAll('.tab');

    sections.forEach(s => s.classList.remove('active'));
    tabs.forEach(t => t.classList.remove('active'));

    document.getElementById(targetId).classList.add('active');
    event.target.classList.add('active');
}
