document.addEventListener("DOMContentLoaded", () => {
    const modalOverlay = document.getElementById("modal-overlay");
    const inlineContent = document.getElementById("inline-content");
    const prevButton = document.querySelector(".prev-schedule");
    const nextButton = document.querySelector(".next-schedule");

    // Track the current schedule file
    let currentDate = null;

    // Function to load a schedule file
    function loadSchedule(date) {
        const filePath = `NHL_data/schedule/NHL_schedule_${date}.txt`;

        fetch(filePath)
            .then(response => {
                if (!response.ok) {
                    // If the file is not found, return a blank placeholder
                    console.warn(`Schedule for ${date} not found. Showing blank content.`);
                    return Promise.resolve(""); // Return an empty string as the content
                }
                return response.text();
            })
            .then(data => {
                inlineContent.innerHTML = data || `<p>No schedule available for ${date}.</p>`;
                currentDate = date; // Update the current date
                console.log(`Loaded schedule for ${date}`); // Debugging log
            })
            .catch(error => {
                console.error("Error loading schedule:", error);
                inlineContent.innerHTML = `<p>Error loading schedule for ${date}.</p>`;
            });
    }

    // Function to calculate the next or previous date
    function calculateDate(offset) {
        if (!currentDate) {
            console.error("Current date is not set.");
            return null;
        }
        const current = new Date(currentDate);
        current.setDate(current.getDate() + offset);
        return current.toISOString().split("T")[0]; // Format as YYYY-MM-DD
    }

    // Event listener for the "Previous" button
    prevButton.addEventListener("click", () => {
        const previousDate = calculateDate(-1);
        if (previousDate) {
            loadSchedule(previousDate);
        }
    });

    // Event listener for the "Next" button
    nextButton.addEventListener("click", () => {
        const nextDate = calculateDate(1);
        if (nextDate) {
            loadSchedule(nextDate);
        }
    });

    // Event listener for links with data-load attribute
    document.querySelectorAll("[data-load]").forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
            const url = link.getAttribute("data-load");

            // Extract the date from the file name if it's a schedule file
            const match = url.match(/NHL_schedule_(\d{4}-\d{2}-\d{2})\.txt/);
            if (match) {
                currentDate = match[1]; // Initialize currentDate when a schedule is loaded
                console.log(`Current date set to ${currentDate}`); // Debugging log
            } else {
                console.error("Could not extract date from URL:", url);
            }

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        console.warn(`Schedule for ${currentDate} not found. Showing blank content.`);
                        return Promise.resolve(""); // Return an empty string as the content
                    }
                    return response.text();
                })
                .then(data => {
                    inlineContent.innerHTML = data || `<p>No schedule available for ${currentDate}.</p>`;
                    modalOverlay.hidden = false;

                    // Set currentDate if it wasn't already set
                    if (!currentDate && match) {
                        currentDate = match[1];
                        console.log(`Fallback currentDate set to ${currentDate}`);
                    }
                })
                .catch(error => {
                    console.error("Error loading content:", error);
                    inlineContent.innerHTML = "<p>Error loading content.</p>";
                    modalOverlay.hidden = false;
                });
        });
    });

    // Set default currentDate to today's date if not initialized
    if (!currentDate) {
        const today = new Date();
        currentDate = today.toISOString().split("T")[0]; // Format as YYYY-MM-DD
        console.log(`Default currentDate set to ${currentDate}`);
    }

    // Close modal functionality
    document.querySelector(".modal-close").addEventListener("click", () => {
        modalOverlay.hidden = true;
        inlineContent.innerHTML = ""; // Clear content when closing
    });
});