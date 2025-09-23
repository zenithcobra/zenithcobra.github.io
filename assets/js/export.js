document.addEventListener("DOMContentLoaded", () => {
    // Add event listener to the Export button
    const exportButton = document.querySelector(".export-table");
    exportButton.addEventListener("click", exportTableToCSV);

    function exportTableToCSV() {
        // Find the table currently displayed in the modal
        const table = document.querySelector("#inline-content table");
        if (!table) {
            alert("No table found to export!");
            return;
        }

        // Extract table data
        const rows = Array.from(table.rows);
        const csvContent = rows
            .map(row => {
                const cells = Array.from(row.cells);
                return cells.map(cell => `"${cell.textContent.trim()}"`).join(",");
            })
            .join("\n");

        // Create a Blob and trigger download
        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "exported_table.csv";
        a.click();
        URL.revokeObjectURL(url);
    }
});