document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('journal-form').addEventListener('submit', async function (event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        try {
            const response = await fetch('/update_journal', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const result = await response.json();
                alert(result.message || "Error occurred");
            } else {
                const result = await response.json();
                alert(result.message);
                window.location.href = "/counsel_view"; // After updating, redirect to the view page
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An unexpected error occurred.");
        }
    });
});
