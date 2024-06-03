document.addEventListener("DOMContentLoaded", function () {
  let isMouseDown = false;

  function handleMouseDown(event) {
    if (event.target.tagName === "TD") {
      isMouseDown = true;
      event.target.classList.toggle("selected");
      event.preventDefault();
    }
  }

  function handleMouseOver(event) {
    if (isMouseDown && event.target.tagName === "TD") {
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
});
