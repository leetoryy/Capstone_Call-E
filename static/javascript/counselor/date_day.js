// 요일 버튼을 활성화하는 함수
function setActiveDayButton(day) {
    const dayButtons = document.querySelectorAll(".day");
    // index가 아닌 버튼의 텍스트 내용으로 판별하도록 변경
    dayButtons.forEach((button) => {
      if (button.textContent.includes(day)) {
        button.classList.add("active");
      } else {
        button.classList.remove("active");
      }
    });
  }
  
  // 오늘 날짜와 요일을 설정하는 함수
  function setCurrentDate() {
    const currentDateElement = document.getElementById("current-date");
    const currentDayElement = document.getElementById("current-day");
    const date = new Date();
    const day = date.getDay();
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const dayOfMonth = date.getDate();
    const dayNames = ["일", "월", "화", "수", "목", "금", "토"];
  
    currentDayElement.textContent = `오늘 ${dayNames[day]}요일`; // 수정된 텍스트 콘텐츠
    currentDateElement.textContent = `${year}.${month < 10 ? `0${month}` : month}.${dayOfMonth < 10 ? `0${dayOfMonth}` : dayOfMonth}`;
  
    setActiveDayButton(dayNames[day]); // 함수 호출에 dayNames[day] 문자열을 전달
  }
  
  // 페이지 로드 시 함수 실행
  document.addEventListener("DOMContentLoaded", setCurrentDate);
  