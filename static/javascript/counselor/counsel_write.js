document.getElementById("counselingForm").addEventListener("submit", function (event) {
  event.preventDefault(); // Prevent default form submission

  // Get form values
  var childName = document.getElementById("childName").value;
  var counselorName = document.getElementById("counselorName").value;
  var counselingDate = document.getElementById("counselingDate").value;
  var counselingNotes = document.getElementById("counselingNotes").value;

  // Do something with the form data (e.g., save to database, display in a console)
  console.log("아동 이름:", childName);
  console.log("상담자 이름:", counselorName);
  console.log("상담 날짜:", counselingDate);
  console.log("상담 내용:", counselingNotes);

  // Clear the form after submission
  document.getElementById("counselingForm").reset();
});

// 셀렉트 옵션
document.addEventListener("DOMContentLoaded", function () {
  const wrapper = document.querySelector(".wrapper"),
    selectBtn = wrapper.querySelector(".select-btn"),
    searchInp = wrapper.querySelector("input"),
    options = wrapper.querySelector(".options"),
    allOptions = Array.from(options.children); // 모든 옵션을 배열로 복사

  // options에서 클릭 이벤트 처리
  options.addEventListener("click", function (event) {
    const target = event.target;
    if (target.tagName === "LI") {
      updateName(target);
    }
  });

  // 선택된 항목의 값을 input과 button에 반영
  function updateName(selectedLi) {
    searchInp.value = "";
    selectBtn.firstElementChild.innerText = selectedLi.textContent; // 표시된 텍스트로 버튼을 업데이트
    wrapper.classList.remove("active"); // active 클래스를 제거하여 목록을 숨김
  }

  // 입력창에 키보드 입력 이벤트 추가
  searchInp.addEventListener("keyup", function () {
    const searchWord = searchInp.value.trim().toLowerCase(); // 검색어를 소문자로 변환하고 양쪽 공백 제거
    const filteredOptions = allOptions.filter((option) => option.textContent.toLowerCase().startsWith(searchWord));
    options.innerHTML = ""; // 현재 목록을 비움
    filteredOptions.forEach((option) => {
      options.appendChild(option); // 필터링된 옵션들을 다시 추가
    });
    if (filteredOptions.length === 0) {
      options.innerHTML = '<p style="margin-top: 10px;">Oops! No option found</p>';
    }
  });

  // select button 클릭 이벤트 처리
  selectBtn.addEventListener("click", () => wrapper.classList.toggle("active")); // 목록 표시/숨김 토글
});
