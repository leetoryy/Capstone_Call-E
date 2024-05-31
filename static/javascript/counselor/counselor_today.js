function initialize() {
    loadTimelineData();
}

function loadTimelineData() {
    $.getJSON("/counselor_today_data", function(today_data) {
        const timelineContainer = document.getElementById('timeline-main-container');
        timelineContainer.innerHTML = ''; 

        if (today_data.length === 0) {
            const noDataElement = document.createElement('div');
            noDataElement.classList.add('no-data');
            noDataElement.textContent = '상담 일정이 존재하지 않습니다';
            timelineContainer.appendChild(noDataElement);
        } else {
            today_data.forEach(function(item) {
                const timelineElement = document.createElement('div');
                timelineElement.classList.add('timeline-item', 'xyz'); 

                timelineElement.innerHTML = `
                    <span class="timeline-time">${item.start_time} - ${item.end_time}</span>
                    <span class="timeline-content">${item.name}과의 상담</span>
                `;
                timelineContainer.appendChild(timelineElement);
            });
        }
    });
}

// 초기화 함수 실행
initialize();
