document.addEventListener("DOMContentLoaded", function() {
    fetchUserCounselData();

    const sortSelect = document.querySelector('.lists-header select');
    sortSelect.addEventListener('change', function() {
        fetchUserCounselData(this.value);
    });

    const searchBar = document.getElementById('search-bar');
    searchBar.addEventListener('input', function() {
        fetchUserCounselData('latest', this.value.trim());
    });
});
  
function fetchUserCounselData(sortOrder = 'latest', searchTerm = '') {
    fetch('/user_counsel_view_data')
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          console.error(data.error);
        } else {
          if (searchTerm) {
            data = data.filter(item => item.co_name.includes(searchTerm));
          }
          if (sortOrder === 'latest') {
            data.sort((a, b) => new Date(b.consulting_day) - new Date(a.consulting_day));
          } else {
            data.sort((a, b) => new Date(a.consulting_day) - new Date(b.consulting_day));
          }
          populateConsultantList(data);
          if (data.length > 0) {
            populateCounselDetails(data[0]); // Default to the first entry
          }
        }
      })
      .catch(error => console.error('Error fetching data:', error));
}
  
function populateConsultantList(data) {
    const consultantList = document.getElementById('consultant-list');
    consultantList.innerHTML = '';
  
    data.forEach((item, index) => {
      const listElement = document.createElement('a');
      listElement.className = 'list';
      listElement.href = '#';
      listElement.dataset.index = index;
  
      const listText = document.createElement('div');
      listText.className = 'list-text';
  
      const listName = document.createElement('span');
      listName.className = 'list-name';
      listName.textContent = `제목: ${item.consulting_title}`;
  
      const listDetail = document.createElement('div');
      listDetail.className = 'list-detail';
  
      const consultantName = document.createElement('p');
      consultantName.textContent = `상담사: ${item.co_name}`;
  
      const consultingDay = document.createElement('p');
      consultingDay.textContent = `상담시간: ${formatDate(item.consulting_day)}`;
  
      listDetail.appendChild(consultantName);
      listDetail.appendChild(consultingDay);
      listText.appendChild(listName);
      listText.appendChild(listDetail);
      listElement.appendChild(listText);
  
      listElement.addEventListener('click', (e) => {
        e.preventDefault();
        populateCounselDetails(item);
      });
  
      consultantList.appendChild(listElement);
    });
}
  
function populateCounselDetails(details) {
    const counselPaper = document.getElementById('counsel-paper');
    counselPaper.innerHTML = '';
  
    const listElement = document.createElement('div');
    listElement.className = 'list';
  
    const listText = document.createElement('div');
    listText.className = 'list-text';
  
    const listTitle = document.createElement('span');
    listTitle.className = 'list-title';
    listTitle.textContent = details.consulting_title;
  
    const counselName = document.createElement('div');
    counselName.className = 'counsel-section';
    counselName.id = 'counsel-name';
    counselName.innerHTML = `<span>상담사: ${details.co_name}</span>`;
  
    const counselContent = document.createElement('div');
    counselContent.className = 'counsel-section';
    counselContent.innerHTML = `<span><strong>상담 내용</strong></span><p>${details.consulting_content}</p>`;
  
    const counselResult = document.createElement('div');
    counselResult.className = 'counsel-section';
    counselResult.innerHTML = `<span><strong>상담 결과</strong></span><p>${details.consulting_result}</p>`;
  
    listText.appendChild(listTitle);
    listText.appendChild(counselName);
    listText.appendChild(counselContent);
    listText.appendChild(counselResult);
    listElement.appendChild(listText);
  
    counselPaper.appendChild(listElement);
}
  
function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dayNames = ['일', '월', '화', '수', '목', '금', '토'];
    const dayName = dayNames[date.getDay()];
    return `${year}-${month}-${day}(${dayName})`;
}
