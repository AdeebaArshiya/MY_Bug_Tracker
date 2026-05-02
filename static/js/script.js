document.addEventListener('DOMContentLoaded', function() {
    // 1. Render Project Health Chart
    const ctx = document.getElementById('priorityChart');
    if (ctx) {
        const stats = window.bugStats || { high: 0, medium: 0, low: 0 };
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [stats.high, stats.medium, stats.low],
                    backgroundColor: ['#fb7185', '#fbbf24', '#2dd4bf'],
                    borderWidth: 0
                }]
            },
            options: { cutout: '75%', plugins: { legend: { display: false } } }
        });
    }

    // 2. Real-time Search Filter
    const search = document.getElementById('searchInput');
    if (search) {
        search.addEventListener('keyup', function() {
            const term = search.value.toLowerCase();
            document.querySelectorAll('#bugTableBody tr').forEach(row => {
                row.style.display = row.innerText.toLowerCase().includes(term) ? '' : 'none';
            });
        });
    }
});