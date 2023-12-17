document.addEventListener('DOMContentLoaded', function() {
  const choice1Button = document.querySelector('.js-choice1');
  const choice2Button = document.querySelector('.js-choice2');
  const progressBar = document.querySelector('.js-progressBar');
  const backButton = document.querySelector('.js-backButton');
  const questionTitle = document.querySelector('.js-question');

  // 질문지
  const questions = [
      {question: '나는 새로운 친구를 사귈 때...', choices: ['친구가 먼저 다가오면 이야기를 하는 경우가 많아요.', '내가 먼저 다가가서 이야기를 하는 경우가 더 많아요.']},
      {question: '새로운 모둠 반에 처음 들어가게 되었어요. 이때 나는...', choices: ['새로운 친구들을 만나게 되어 신이나요.', '새로운 친구들과 어떻게 지낼까 걱정이 돼요.']},
      {question: '내 성격은...', choices: ['활발하다는 말을 많이 들어요.', '부끄러움을 많이 타요.']},
      {question: '나는 놀 때...', choices: ['혼자 노는 걸 좋아해요.', '친구들과 다같이 노는 걸 좋아해요.']},
      {question: '나는 학교에서 발표를..', choices: ['다른 친구보다 많이 해요.', '나서서 하지 않아요.']},
      {question: '나는 만들기 시간에 선생님이 만드신 것과..', choices: ['비슷하게 만드는 것이 더 즐거워요.', '다르게 내 생각대로 만드는 것이 더 즐거워요.']},
      {question: '나는 책을 읽을 때..', choices: ['실제 이야기가 좋아요.', '상상 속의 이야기가 좋아요.']},
      {question: '주변 사람의 모습을..', choices: ['잘 기억해요.', '잘 기억 못해요.']},
      {question: '그림 그리기 시간에 나는..', choices: ['그리고 싶은 그림을 그리는 것이 좋아요.', '그려져 있는 그림을 예쁘게 색칠하는 것이 좋아요.']},
      {question: '나는 혼자 있을 때..', choices: ['상상을 많이 해요.', '아무 생각도 하지 않아요.']},
      {question: '친구가 울고 있을 때 나는..', choices: ['“친구야, 왜 울어?”하고 왜 우는지 물어봐요.', '“친구야, 울지 마”하고 달래줘요.']},
      {question: '부모님께 혼났을 때 나는..', choices: ['슬퍼서 울다가 말을 제대로 하지 못해요.', '“그래서 이럴 수 밖에 없었어요.” 하고 이유를 설명해요.']},
      {question: '나는 커서..', choices: ['공평한 사람이 되고 싶어요.', '친절한 사람이 되고 싶어요.']},
      {question: '나는 친구들과 놀 때 뭐 하면서 놀지..', choices: ['빨리 정해요.', '쉽게 정하지 못해요.']},
      {question: '친구가 아프다고 하면..', choices: ['걱정부터 돼요.', '왜 아픈지 물어봐요.']},
      {question: '오늘 수업 시간에 게임이나 만들기를 한대요..', choices: ['전에 배웠던 방법으로 하고 싶어요.', '새로운 방법으로 해보고 싶어요.']},
      {question: '나는 숙제를..', choices: ['미리 끝내놓는 게 좋아요.', '마지막까지 미루다가 해요.']},
      {question: '나는 물건을 사용하고 나서..', choices: ['정해진 자리에 둬요.', ' 바로 사용하기 쉽게 적당한 곳에 둬요.']},
      {question: '나는 하루를 보낼 때..', choices: ['특별한 계획 없이 즐겁게 보내는 것이 좋아요.', '미리 정해놓은 계획에 따라 보내는 것이 좋아요.']},
      {question: '계획에 없던 일이 생기면..', choices: ['짜증이 나고 힘이 들어요.', '별로 신경 안 써요.']},
  ];

  // 문항별 답변 성향
  const mbtiScore = [
    {1: 'I', 2: 'E'},
    {1: 'E', 2: 'I'},
    {1: 'E', 2: 'I'},
    {1: 'I', 2: 'E'},
    {1: 'E', 2: 'I'},
    {1: 'S', 2: 'N'},
    {1: 'S', 2: 'N'},
    {1: 'S', 2: 'N'},
    {1: 'N', 2: 'S'},
    {1: 'N', 2: 'S'},
    {1: 'T', 2: 'F'},
    {1: 'F', 2: 'T'},
    {1: 'T', 2: 'F'},
    {1: 'T', 2: 'F'},
    {1: 'F', 2: 'T'},
    {1: 'J', 2: 'P'},
    {1: 'J', 2: 'P'},
    {1: 'J', 2: 'P'},
    {1: 'P', 2: 'J'},
    {1: 'J', 2: 'P'}
  ]

  // MBTI 유형별 점수 초기화
  let typeCounts = {
    'E': 0,
    'I': 0,
    'S': 0,
    'N': 0,
    'T': 0,
    'F': 0,
    'J': 0,
    'P': 0
  };

  let progress = 0;

  // 질문 및 선택지
  function updateQuestion() {
    const currentQuestion = questions[progress];
    questionTitle.textContent = currentQuestion.question;
    choice1Button.textContent = currentQuestion.choices[0];
    choice2Button.textContent = currentQuestion.choices[1];
  }

  // 선택한 값 기준 점수 업데이트
  function updateCounts(selectedValue) {
    // 사용자가 선택한 값이 첫 번째 선택지와 일치하는지 확인
    if (selectedValue === questions[progress].choices[0]) {
      // 일치하면 MBTI 유형 스코어링
      typeCounts[mbtiScore[progress][1]]++;
    // 사용자가 선택한 값이 두 번째 선택지일 때
    } else {
      // 두 번째 유형 스코어링 
      typeCounts[mbtiScore[progress][2]]++;
    }
    // ex) 4번 문항('나는 놀 때...')에서 1번 선택지('혼자 노는 걸 좋아해요.')를 선택하면 I에 점수 부여
  }

  // MBTI 결과 계산
  function calculateMBTIResult() {
    let mbtiType = '';
    
    // I의 부여된 점수가 E보다 크면 mbtiType에 I 추가
    if (typeCounts['I'] > typeCounts['E']) mbtiType += 'I';
    else mbtiType += 'E';

    if (typeCounts['S'] > typeCounts['N']) mbtiType += 'S';
    else mbtiType += 'N';

    if (typeCounts['T'] > typeCounts['F']) mbtiType += 'T';
    else mbtiType += 'F';

    if (typeCounts['J'] > typeCounts['P']) mbtiType += 'J';
    else mbtiType += 'P';

    return mbtiType;
  }

  // 다음 질문으로 이동
  function nextQuestion(selectedValue) {
    updateCounts(selectedValue);
    progress++;

    if (progress < questions.length) {
      updateQuestion();
    } else {
      const mbtiResult = calculateMBTIResult();
      // alert("계산된 MBTI 결과: " + mbtiResult);
      window.location.href = `mbti_result?result=${mbtiResult}`;  
    } 
      // 진행바
      const percentage = (progress / questions.length) * 100;
      progressBar.value = percentage;

      // 이전 버튼
      backButton.style.visibility = 'visible';
  }

  choice1Button.addEventListener('click', function() {
    nextQuestion(choice1Button.textContent.trim());
  });
  choice2Button.addEventListener('click', function() {
    nextQuestion(choice2Button.textContent.trim());
  });

  // 이전 버튼 클릭 이벤트
  backButton.addEventListener('click', function() {
    progress = Math.max(0, progress - 1);
    updateQuestion();

    const percentage = (progress / questions.length) * 100;
    progressBar.value = percentage;

    if (progress === 0) {
      backButton.style.visibility = 'hidden';
    }
  });

  updateQuestion();
});