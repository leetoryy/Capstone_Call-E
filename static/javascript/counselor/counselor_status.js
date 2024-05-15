function initialize() {
  loadData("상담 대기");
}

function loadData(status) {
  const tabs = document.querySelectorAll(".status-tab button");
  tabs.forEach((tab) => {
    if (tab.textContent === status) {
      tab.classList.add("active");
    } else {
      tab.classList.remove("active");
    }
  });

  // 임시 데이터
  const data = {
    "상담 대기": [
      { name: "나아동", mbti: "ENFP", type: "발달 상담", status: "상담 대기", contact: "010-0000-0000" },
      { name: "장아동", mbti: "ENTP", type: "발달 상담", status: "상담 대기", contact: "010-0000-0000" },
    ],
    "상담 중": [{ name: "유아동", mbti: "ESFP", type: "발달 상담", status: "상담 중", contact: "010-0000-0000" }],
    "상담 완료": [{ name: "이아동", mbti: "ESFP", type: "발달 상담", status: "상담 완료", contact: "010-0000-0000" }],
  };

  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";

  data[status].forEach((consultation) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${consultation.name}</td>
                        <td>${consultation.mbti}</td>
                        <td>${consultation.type}</td>
                        <td>${consultation.status}</td>
                        <td>${consultation.contact}</td>`;
    tbody.appendChild(tr);
  });
}
