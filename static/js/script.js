function filterTable() {
    let filter = document.getElementById("searchInput").value.toUpperCase();
    let table = document.querySelector(".bug-table");
    
    if (!table) return;
    
    let rows = table.querySelector("tbody").rows;
    
    for (let i = 0; i < rows.length; i++) {
        let row = rows[i];
        let text = row.innerText || row.textContent;
        
        if (text.toUpperCase().indexOf(filter) > -1) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    }
}

// Optional: Clear search on page load
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = '';
    }
});