document.addEventListener('DOMContentLoaded', function() {
  const resultTitle = document.querySelector('.js-resultTitle');
  const resultExplain = document.querySelector('.js-resultExplain');
  const mbtiImage = document.querySelector('.js-mbtiImage');
  const restartButton = document.querySelector('.js-restart');
  const matchButton = document.querySelector('.js-match');

  // URL에서 결과값 추출
  const urlParams = new URLSearchParams(window.location.search);
  const result = urlParams.get('result');
  
  // 결과
  if (result) {
    resultTitle.textContent = `당신의 MBTI는 "${result}" 입니다.`;
    // 유형별 설명
    switch (result) {
      case 'ISTJ':
        resultExplain.textContent = '바른 생활 어린이';
        mbtiImage.src = '/static/images/istj.png';
        break;
      case 'ISFJ':
        resultExplain.textContent = '예의 바른 어린이';
        mbtiImage.src = '/static/images/isfj.png';
        break;
      case 'INFJ':
        resultExplain.textContent = '우정 가득 어린이';
        mbtiImage.src = '/static/images/infj.png';
        break;
      case 'INTJ':
        resultExplain.textContent = '성숙한 어린이';
        mbtiImage.src = '/static/images/intj.png';
        break;
      case 'ISTP':
        resultExplain.textContent = '사교적인 어린이';
        mbtiImage.src = '/static/images/istp.png';
        break;
      case 'ISFP':
        resultExplain.textContent = '여유로운 어린이';
        mbtiImage.src = '/static/images/isfp.png';
        break;
      case 'INFP':
        resultExplain.textContent = '인정 많은 어린이';
        mbtiImage.src = '/static/images/infp.png';
        break;
      case 'INTP':
        resultExplain.textContent = '척척박사 어린이';
        mbtiImage.src = '/static/images/intp.png';
        break;
      case 'ESTP':
        resultExplain.textContent = '참견쟁이 어린이';
        mbtiImage.src = '/static/images/estp.png';
        break;
      case 'ESFP':
        resultExplain.textContent = '적극적인 어린이';
        mbtiImage.src = '/static/images/esfp.png';
        break;
      case 'ENFP':
        resultExplain.textContent = '변덕쟁이 어린이';
        mbtiImage.src = '/static/images/enfp.png';
        break;
      case 'ENTP':
        resultExplain.textContent = '개인주의 어린이';
        mbtiImage.src = '/static/images/entp.png';
        break;
      case 'ESTJ':
        resultExplain.textContent = '모범적인 어린이';
        mbtiImage.src = '/static/images/estj.png';
        break;
      case 'ESFJ':
        resultExplain.textContent = '발표대장 어린이';
        mbtiImage.src = '/static/images/esfj.png';
        break;
      case 'ENFJ':
        resultExplain.textContent = '사차원적 어린이';
        mbtiImage.src = '/static/images/enfj.png';
        break;
      case 'ENTJ':
        resultExplain.textContent = '원칙주의 어린이';
        mbtiImage.src = '/static/images/entj.png';
        break;
    }
  }

  // 테스트 다시하기 버튼 이벤트 리스너
  restartButton.addEventListener('click', function() {
    window.location.href = 'mbti_test';
  });

  // 맞춤 상담사 찾기 버튼 이벤트 리스너
  matchButton.addEventListener('click', function() {
    // 결과값 추출
    const urlParams = new URLSearchParams(window.location.search);
    const result = urlParams.get('result');

    // 서버로 결과값 전송
    fetch('/save_mbti_result', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ result: result }),
    })
    .then(response => {
      if (response.ok) {
        // 성공적으로 업데이트된 경우
        window.location.href = 'mbti_match'
      } else {
        // 실패한 경우에 대한 처리
        response.json().then(data => {
          console.error('Failed to update child MBTI:', data.error);
        });
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
  });

});
