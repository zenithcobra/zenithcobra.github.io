document.addEventListener("DOMContentLoaded", () => {
    const modalOverlay = document.getElementById("modal-overlay");
    const inlineContent = document.getElementById("inline-content");

    // Function to load content into the modal
    function loadContent(url) {
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load content from ${url}`);
                }
                return response.text();
            })
            .then(data => {
                // Insert the content as HTML
                inlineContent.innerHTML = data;

                // Show the modal
                modalOverlay.hidden = false;
            })
            .catch(error => {
                console.error("Error loading content:", error);
                inlineContent.innerHTML = "<p>Error loading content.</p>";
                modalOverlay.hidden = false;
            });
    }

    // Event listener for links with data-load attribute
    document.querySelectorAll("[data-load]").forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
            const url = link.getAttribute("data-load");
            loadContent(url);
        });
    });

    // Close modal functionality
    document.querySelector(".modal-close").addEventListener("click", () => {
        modalOverlay.hidden = true;
        inlineContent.innerHTML = ""; // Clear content when closing
    });
});