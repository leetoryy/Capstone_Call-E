document.addEventListener("DOMContentLoaded", function () {
    let allData = [];

    fetch("/counsel_view_data")
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                console.error("Error:", data.error);
            } else {
                allData = data;
                renderTable(allData);
            }
        })
        .catch((error) => {
            console.error("Error fetching data:", error);
        });

    document.getElementById("journal-list").addEventListener("click", function (e) {
        const targetRow = e.target.closest("tr");
        if (targetRow) {
            const childId = targetRow.dataset.childId;
            const consultingDay = targetRow.dataset.consultingDay;
            window.location.href = `/counsel_view_edit?child_id=${childId}&consulting_day=${consultingDay}`;
        }
    });

    const searchIcon = document.getElementById("searchIcon");
    searchIcon.addEventListener("click", function () {
        const searchInput = document.getElementById("searchInput");
        const searchTerm = searchInput.value.toLowerCase();
        const dateInput = document.getElementById("dateInput").value;

        const filteredData = allData.filter(item => {
            const matchesName = searchTerm ? item.child_name.toLowerCase().includes(searchTerm) : true;
            const matchesDate = dateInput ? item.consulting_day === dateInput : true;
            return matchesName && matchesDate;
        });

        renderTable(filteredData);

        if (filteredData.length === 0) {
            displayNoDataMessage();
        }
    });

    const dateInput = document.getElementById("dateInput");
    dateInput.addEventListener("change", function () {
        const selectedDate = dateInput.value;
        const searchInput = document.getElementById("searchInput").value.toLowerCase();

        const filteredData = allData.filter(item => {
            const matchesName = searchInput ? item.child_name.toLowerCase().includes(searchInput) : true;
            const matchesDate = selectedDate ? item.consulting_day === selectedDate : true;
            return matchesName && matchesDate;
        });

        renderTable(filteredData);

        if (filteredData.length === 0) {
            displayNoDataMessage();
        }
    });

    const refreshIcon = document.getElementById("refresh");
    refreshIcon.addEventListener("click", function () {
        dateInput.value = '';
        document.getElementById("searchInput").value = '';
        renderTable(allData);
    });
});

function renderTable(data) {
    const tableBody = document.getElementById("journal-list");
    tableBody.innerHTML = "";
    if (data.length === 0) {
        displayNoDataMessage();
        return;
    }
    data.forEach((item) => {
        const row = document.createElement("tr");
        row.dataset.childId = item.child_id;
        row.dataset.consultingDay = item.consulting_day;
        row.innerHTML = `
            <td class="text-center">${item.consulting_title}</td>
            <td class="text-center">${item.child_name}</td>
            <td class="text-center">${item.survey_consulting}</td>
            <td class="text-center">${item.consulting_day}</td>
        `;
        tableBody.appendChild(row);
    });
}

function displayNoDataMessage() {
    const tableBody = document.getElementById("journal-list");
    const messageRow = document.createElement("tr");
    const messageCell = document.createElement("td");
    messageCell.colSpan = 4;  // Adjust this number based on the number of columns in your table
    messageCell.className = "text-center";
    messageCell.textContent = "상담 일지가 존재하지 않습니다.";
    messageRow.appendChild(messageCell);
    tableBody.appendChild(messageRow);
}

function sortTable(columnIndex) {
    var table,
        rows,
        switching,
        i,
        x,
        y,
        shouldSwitch,
        dir,
        switchcount = 0;
    table = document.querySelector(".table-fill");
    switching = true;
    dir = "asc";

    while (switching) {
        switching = false;
        rows = table.rows;

        for (i = 1; i < rows.length - 1; i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("td")[columnIndex];
            y = rows[i + 1].getElementsByTagName("td")[columnIndex];

            if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
        }

        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}
