document.addEventListener('DOMContentLoaded', initialize);

// URL에서 특정 쿼리 파라미터 값을 추출하는 함수 정의
function getQueryParameter(param) {
  var urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

function initialize() {
  loadData("상담 대기");
}

function loadData(status) {
  const tabs = document.querySelectorAll(".status-tab button");
  tabs.forEach((tab) => {
    if (tab.textContent.trim() === status) {
      tab.classList.add("active");
    } else {
      tab.classList.remove("active");
    }
  });

  fetch('/counselor_home_data')
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        console.error(data.error);
        return;
      }

      console.log('Received Data:', data); // 데이터를 확인하기 위해 콘솔 로그 추가

      const filteredData = data.filter(consultation => consultation.status === status);
      const tbody = document.getElementById("table-body");
      tbody.innerHTML = "";

      if (filteredData.length === 0) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        
        td.colSpan = 6; // 버튼 열을 추가했으므로 colspan을 6으로 변경
        td.classList.add("text-center");
        td.textContent = "상담 일정이 존재하지 않습니다.";
        tr.appendChild(td);
        tbody.appendChild(tr);
      } else {
        filteredData.forEach((consultation) => {
          const tr = document.createElement("tr");
          tr.innerHTML = `<td>${consultation.name}</td>
                          <td>${consultation.mbti}</td>
                          <td>${consultation.type}</td>
                          <td>${consultation.status}</td>
                          <td>${consultation.contact}</td>
                          <td>${consultation.code}</td>`;
          tr.addEventListener('click', () => {
            var socket = io();
            console.log('Selected Child Name:', consultation.name);
            socket.emit("start_counseling", { childName: consultation.name, code: consultation.code }); 
            const coID = getQueryParameter('counselor_id'); // URL에서 co_id 가져오기
            window.open(`/chat?counselor_id=${encodeURIComponent(coID)}`, "_blank"); // 새 창에서 URL에 co_id 포함하여 chat 페이지를 엽니다.
            //window.open("/chat", "_blank");
            
          });
          tbody.appendChild(tr);
        });
      }
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}
