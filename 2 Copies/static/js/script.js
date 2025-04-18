document.addEventListener("DOMContentLoaded", function() {
    const searchBox = document.getElementById("search");

    searchBox.addEventListener("keyup", function() {
        let filter = searchBox.value.toLowerCase();
        let events = document.querySelectorAll(".event-card");

        events.forEach(event => {
            let title = event.querySelector("h3").innerText.toLowerCase();
            if (title.includes(filter)) {
                event.style.display = "block";
            } else {
                event.style.display = "none";
            }
        });
    });
});
