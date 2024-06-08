document.addEventListener('DOMContentLoaded', function () {
    fetchChildrenByDate();
});

async function fetchChildrenByDate() {
    const response = await fetch(`/get_children_by_date`);
    const result = await response.json();
    const children = result.children;
    const dateSelect = document.getElementById('counsel-date');
    const childSelect = document.getElementById('child-name');
    
    const dates = new Set(children.map(child => child[1]));

    dateSelect.innerHTML = '<option value="">상담 날짜</option>';
    dates.forEach(date => {
        const option = document.createElement('option');
        option.value = date;
        option.textContent = formatDate(new Date(date));
        dateSelect.appendChild(option);
    });

    dateSelect.addEventListener('change', () => {
        const selectedDate = dateSelect.value;
        const filteredChildren = children.filter(child => child[1] === selectedDate);

        childSelect.innerHTML = '<option value="">아동 이름</option>';
        filteredChildren.forEach(child => {
            const option = document.createElement('option');
            option.value = child[0];  // 아동 ID
            option.textContent = child[2];  // 아동 이름
            childSelect.appendChild(option);
        });
    });
}

async function fetchChildDetails() {
    const childId = document.getElementById('child-name').value;
    if (!childId) return;
    const response = await fetch(`/get_child_details?child_id=${childId}`);
    const details = await response.json();

    document.getElementById('counsel-field').value = details.survey_consulting;
    document.getElementById('mbti').value = details.child_mbti;
    document.getElementById('priority1').value = details.survey_priority_1;
    document.getElementById('priority2').value = details.survey_priority_2;
    document.getElementById('priority3').value = details.survey_priority_3;
    document.getElementById('priority4').value = details.survey_priority_4;
}

function formatDate(date) {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'short' };
    return new Intl.DateTimeFormat('ko-KR', options).format(date);
}

document.getElementById('journal-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const response = await fetch('/save_journal', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    if (response.status === 400) {  
        alert(result.message);
        event.target.reset();
    } else {
        alert(result.message);
        event.target.reset();
    }
});
