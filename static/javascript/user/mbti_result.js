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
        mbtiImage.src = '/static/images/ISTJ.png';
        break;
      case 'ISFJ':
        resultExplain.textContent = '예의 바른 어린이';
        mbtiImage.src = '/static/images/ISFJ.png';
        break;
      case 'INFJ':
        resultExplain.textContent = '우정 가득 어린이';
        mbtiImage.src = '/static/images/INFJ.png';
        break;
      case 'INTJ':
        resultExplain.textContent = '성숙한 어린이';
        mbtiImage.src = '/static/images/INTJ.png';
        break;
      case 'ISTP':
        resultExplain.textContent = '사교적인 어린이';
        mbtiImage.src = '/static/images/ISTP.png';
        break;
      case 'ISFP':
        resultExplain.textContent = '여유로운 어린이';
        mbtiImage.src = '/static/images/ISFP.png';
        break;
      case 'INFP':
        resultExplain.textContent = '인정 많은 어린이';
        mbtiImage.src = '/static/images/INFP.png';
        break;
      case 'INTP':
        resultExplain.textContent = '척척박사 어린이';
        mbtiImage.src = '/static/images/INTP.png';
        break;
      case 'ESTP':
        resultExplain.textContent = '참견쟁이 어린이';
        mbtiImage.src = '/static/images/ESTP.png';
        break;
      case 'ESFP':
        resultExplain.textContent = '적극적인 어린이';
        mbtiImage.src = '/static/images/ESFP.png';
        break;
      case 'ENFP':
        resultExplain.textContent = '변덕쟁이 어린이';
        mbtiImage.src = '/static/images/ENFP.png';
        break;
      case 'ENTP':
        resultExplain.textContent = '개인주의 어린이';
        mbtiImage.src = '/static/images/ENTP.png';
        break;
      case 'ESTJ':
        resultExplain.textContent = '모범적인 어린이';
        mbtiImage.src = '/static/images/ESTJ.png';
        break;
      case 'ESFJ':
        resultExplain.textContent = '발표대장 어린이';
        mbtiImage.src = '/static/images/ESFJ.png';
        break;
      case 'ENFJ':
        resultExplain.textContent = '사차원적 어린이';
        mbtiImage.src = '/static/images/ENFJ.png';
        break;
      case 'ENTJ':
        resultExplain.textContent = '원칙주의 어린이';
        mbtiImage.src = '/static/images/ENTJ.png';
        break;
    }
  }

  // 테스트 다시하기 버튼 이벤트 리스너
  restartButton.addEventListener('click', function() {
    window.location.href = 'mbti_test';
  });

  // 맞춤 상담사 찾기 버튼 이벤트 리스너
  matchButton.addEventListener('click', function() {
    window.location.href = 'mbti_match';
  });
});