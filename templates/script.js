// site/script.js

document.addEventListener('DOMContentLoaded', () => {
    console.log("PoolPower script loaded.");

    // Find all buttons/links that initiate a pool action
    // We'll add a specific class or data attribute to these in the generated HTML
    // Let's assume the Python script adds a class like 'initiate-pool-btn'
    // and data attributes like data-deal-id, data-item-name, data-whatsapp-number
    const initiatePoolButtons = document.querySelectorAll('.initiate-pool-btn');

    initiatePoolButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent the default link behavior

            const dealId = button.dataset.dealId;
            const itemName = button.dataset.itemName;
            const whatsappNumber = button.dataset.whatsappNumber; // Get PoolPower number from data attribute

            // --- Step 1: Prompt user for quantity ---
            // Using prompt is basic; a modal would be better for UI.
            // For MVP, prompt is quick and functional.
            let quantity = prompt(`How many units of "${itemName}" (${dealId}) do you need?\n\nEnter quantity:`);

            // --- Step 2: Validate input (basic) ---
            quantity = parseInt(quantity); // Convert input to an integer

            if (isNaN(quantity) || quantity <= 0) {
                alert("Please enter a valid quantity greater than zero.");
                return; // Stop the process if input is invalid
            }

            // --- Step 3: Construct the specific WhatsApp message ---
            // Ensure the message is URL-encoded
            const message = `Hi PoolPower, I want to join/create a pool for ${itemName} (${dealId}). I need ${quantity} units.`;
            const encodedMessage = encodeURIComponent(message);

            // --- Step 4: Generate the wa.me link ---
            const whatsappLink = `https://wa.me/${whatsappNumber}?text=${encodedMessage}`;

            // --- Step 5: Redirect to WhatsApp ---
            window.open(whatsappLink, '_blank'); // Open in a new tab/window
        });
    });

    // Optional: Add more client-side JS here later for filtering, sorting, etc.
    // Example: Basic filtering by Deal ID or Item Name
    // const searchInput = document.getElementById('deal-search'); // Assuming you add a search input in HTML
    // if (searchInput) {
    //     searchInput.addEventListener('input', (event) => {
    //         const searchTerm = event.target.value.toLowerCase();
    //         document.querySelectorAll('.deal-item').forEach(dealElement => {
    //             const textContent = dealElement.textContent.toLowerCase();
    //             if (textContent.includes(searchTerm)) {
    //                 dealElement.style.display = ''; // Show the deal
    //             } else {
    //                 dealElement.style.display = 'none'; // Hide the deal
    //             }
    //         });
    //     });
    // }
});
