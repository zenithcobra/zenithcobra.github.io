(function (window, document) {
    'use strict';

    // Selectors
    const modalBodySelector = '.modal-body';
    const checkedSectionId = 'checked-section';
    const checkedTableId = 'checked-table';

    // Create the "Checked" section dynamically
    function createCheckedSection() {
        const checkedSection = document.createElement('section');
        checkedSection.id = checkedSectionId;
        checkedSection.style.display = 'none'; // Initially hidden
        checkedSection.innerHTML = `
      <h2>Checked</h2>
      <table id="${checkedTableId}">
        <thead></thead>
        <tbody></tbody>
      </table>
    `;
        document.querySelector('#main .inner').appendChild(checkedSection);
    }

    // Show or hide the "Checked" section based on the number of rows
    function toggleCheckedSection() {
        const checkedSection = document.getElementById(checkedSectionId);
        const checkedTableBody = document.querySelector(`#${checkedTableId} tbody`);
        if (checkedTableBody && checkedTableBody.children.length > 0) {
            checkedSection.style.display = 'block';
        } else {
            checkedSection.style.display = 'none';
        }
    }

    //   // Add a row to the "Checked" section
    //   function addRowToCheckedSection(row) {
    //     const checkedTableBody = document.querySelector(`#${checkedTableId} tbody`);
    //     const clonedRow = row.cloneNode(true); // Clone the row
    //     clonedRow.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    //       checkbox.checked = false; // Uncheck the checkbox in the cloned row
    //       checkbox.disabled = true; // Disable the checkbox in the cloned row
    //     });
    //     checkedTableBody.appendChild(clonedRow);
    //     toggleCheckedSection();
    //   }
    // Add a row to the "Checked" section
    // Add a row to the "Checked" section
    // function addRowToCheckedSection(row) {
    //     const checkedTableBody = document.querySelector(`#${checkedTableId} tbody`);
    //     const clonedRow = row.cloneNode(true); // Clone the row

    //     // Uncheck and disable checkboxes in the cloned row
    //     clonedRow.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    //         checkbox.checked = false; // Uncheck the checkbox in the cloned row
    //         checkbox.disabled = true; // Disable the checkbox in the cloned row
    //     });

    //     // Append the cloned row to the checked table body
    //     checkedTableBody.appendChild(clonedRow);
    //     toggleCheckedSection();
    // }

    // Add a row to the "Checked" section
    function addRowToCheckedSection(row) {
        const checkedTableBody = document.querySelector(`#${checkedTableId} tbody`);
        const clonedRow = row.cloneNode(true); // Clone the row

        // Uncheck and disable checkboxes in the cloned row
        clonedRow.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
            checkbox.checked = false; // Uncheck the checkbox in the cloned row
            checkbox.disabled = true; // Disable the checkbox in the cloned row
        });

        // Add a border and background color to the row
        clonedRow.style.border = '1px solid #ccc'; // Add a border for readability
        clonedRow.style.backgroundColor = getRowBackgroundColor(); // Set background color based on theme
        clonedRow.style.color = getRowTextColor(); // Set text color based on theme

        // Append the cloned row to the checked table body
        checkedTableBody.appendChild(clonedRow);
        toggleCheckedSection();
    }

    // Get the background color based on the current theme
    function getRowBackgroundColor() {
        if (document.body.classList.contains('dark-mode')) {
            return '#000000'; // Black background for dark mode
        } else {
            return '#ffffff'; // White background for light mode
        }
    }

    // Get the text color based on the current theme
    function getRowTextColor() {
        if (document.body.classList.contains('dark-mode')) {
            return '#ffffff'; // White text for dark mode
        } else {
            return '#000000'; // Black text for light mode
        }
    }
    // Remove a row from the "Checked" section
    function removeRowFromCheckedSection(row) {
        const checkedTableBody = document.querySelector(`#${checkedTableId} tbody`);
        const rowId = row.dataset.rowId;
        const rows = checkedTableBody.querySelectorAll('tr');
        rows.forEach((checkedRow) => {
            if (checkedRow.dataset.rowId === rowId) {
                checkedTableBody.removeChild(checkedRow);
            }
        });
        toggleCheckedSection();
    }

    // Handle checkbox changes
    function handleCheckboxChange(event) {
        const checkbox = event.target;
        const row = checkbox.closest('tr');
        if (checkbox.checked) {
            addRowToCheckedSection(row);
        } else {
            removeRowFromCheckedSection(row);
        }
    }

    // Initialize the functionality
    function initCheckboxHandler() {
        createCheckedSection();

        const modalBody = document.querySelector(modalBodySelector);
        if (!modalBody) return;

        modalBody.addEventListener('change', (event) => {
            if (event.target.type === 'checkbox') {
                handleCheckboxChange(event);
            }
        });
    }

    // Run the initialization on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCheckboxHandler);
    } else {
        initCheckboxHandler();
    }
})(window, document);