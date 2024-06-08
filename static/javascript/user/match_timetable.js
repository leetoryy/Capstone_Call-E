document.addEventListener("DOMContentLoaded", function () {
    let selectedBlocks = {
        "월요일": 0,
        "화요일": 0,
        "수요일": 0,
        "목요일": 0,
        "금요일": 0
    };

    let selectedTimes = [];
    const co_id = document.getElementById('co_id').value; // 상담사의 co_id를 가져옴

    function handleCellClick(event) {
        if (event.target.tagName === "TD" && !event.target.classList.contains("unselectable")) {
            toggleSelect(event.target);
            event.preventDefault();
        }
    }

    function toggleSelect(cell) {
        const dayHeader = cell.closest('table').querySelectorAll('thead th');
        const dayIndex = Array.from(cell.parentNode.children).indexOf(cell);
        const day = dayHeader[dayIndex].innerText;

        const time = cell.parentElement.children[0].innerText;

        if (time === '12:00') {
            alert("12시는 선택할 수 없습니다.");
            return;
        }

        if (cell.classList.contains("selected")) {
            cell.classList.remove("selected");
            selectedBlocks[day]--;
            selectedTimes = selectedTimes.filter(item => !(item.day_of_week === day && item.start_time === time));
        } else {
            if (selectedBlocks[day] < 2) {
                cell.classList.add("selected");
                selectedBlocks[day]++;
                const endTime = calculateEndTime(time);
                selectedTimes.push({ day_of_week: day, start_time: time, end_time: endTime });
            } else {
                alert("하루에 최대 2시간까지만 상담을 진행할 수 있습니다.");
            }
        }
    }

    function calculateEndTime(startTime) {
        const [hour, minute] = startTime.split(':').map(Number);
        const endTime = new Date(0, 0, 0, hour + 1, minute).toTimeString().slice(0, 5);
        return endTime;
    }

    function submitSelection(endpoint) {
        fetch(`${endpoint}/${co_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ selectedTimes })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("상담 시간이 성공적으로 처리되었습니다.");
                window.location.href = "/user_home"; 
            } else if (data.require_confirmation) {
                if (confirm(data.message)) {
                    confirmChangeSelection();
                }
            } else {
                alert(data.message || "상담 시간 처리에 실패하였습니다. 다시 시도해 주세요.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function confirmChangeSelection() {
        fetch(`/confirm_change_selection/${co_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ selectedTimes })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("상담 시간이 성공적으로 변경되었습니다.");
                window.location.href = "/user_home";
            } else {
                alert("상담 시간 변경에 실패하였습니다. 다시 시도해 주세요.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    const cells = document.querySelectorAll(".timetable td");
    cells.forEach((cell) => {
        cell.addEventListener("click", handleCellClick);
    });

    document.querySelector(".btn-check.apply").addEventListener("click", () => submitSelection('/submit_selection'));
    document.querySelector(".btn-check.change").addEventListener("click", () => submitSelection('/change_selection'));
});
