document.addEventListener("DOMContentLoaded", function () {
  var calendarEl = document.getElementById("calendar");
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,timeGridDay",
    },
    editable: false, // 수정 비활성화
    selectable: false, // 선택 비활성화
    selectMirror: false, // 선택 미러링 비활성화
    dayMaxEvents: true,
    select: function (arg) {
      // 선택 기능 비활성화
    },
    eventClick: function (arg) {
      // 클릭 이벤트 비활성화
    },
  });
  calendar.render();
});
