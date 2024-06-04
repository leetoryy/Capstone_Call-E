// static/javascript/user/match_timetable.js
document.addEventListener("DOMContentLoaded", function () {
    let isMouseDown = false;
  
    function handleMouseDown(event) {
        if (event.target.tagName === "TD" && !event.target.classList.contains("unselectable")) {
            isMouseDown = true;
            event.target.classList.toggle("selected");
            event.preventDefault();
        }
    }
  
    function handleMouseOver(event) {
        if (isMouseDown && event.target.tagName === "TD" && !event.target.classList.contains("unselectable")) {
            event.target.classList.toggle("selected");
        }
    }
  
    function handleMouseUp() {
        isMouseDown = false;
    }
  
    const cells = document.querySelectorAll(".timetable td");
    cells.forEach((cell) => {
        cell.addEventListener("mousedown", handleMouseDown);
        cell.addEventListener("mouseover", handleMouseOver);
    });
  
    document.addEventListener("mouseup", handleMouseUp);
  
    // Add unselectable class to 12:00 time slots
    const twelvePMCells = document.querySelectorAll(".timetable tr:nth-child(4) td");
    twelvePMCells.forEach(cell => {
        cell.classList.add("unselectable");
    });
  });
  