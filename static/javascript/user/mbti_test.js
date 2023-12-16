const body = document.querySelector('.js-body'),
  question = document.querySelector('.js-question'),
  pgbar = document.querySelector('.js-progressBar'),
  choice1 = document.querySelector('.js-choice1'),
  choice2 = document.querySelector('.js-choice2'),
  backButton = document.querySelector('.js-backButton')

const question_LIST = [
    '나는 새로운 친구를 사귈 때...',
    '새로운 모둠 반에 처음 들어가게 되었어요. 이때 나는...',
    '내 성격은...',
    '나는 놀 때...',
    '만들기 시간에 나는 선생님이 만드신 것과...',
    '나는 책을 읽을 때...',
    '주변 사람의 모습을...',
    '그림 그리기 시간에 나는...',
    '친구가 울고 있을 때 나는...',
    '부모님께 혼났을 때 나는...',
    '나는 커서...',
    '나는 친구들과 놀 때 무엇을 하면서 놀지...',
    '오늘 수업 시간에 게임이나 만들기를 한대요.',
    '나는 선생님께서 내주신 숙제를...',
    '나는 물건을 사용하고 나서...',
    '나는 하루를 보낼 때',
  ],
  //ENFP
  choice1_LIST = [
    '내가 먼저 다가가서 이야기를 하는 경우가 더 많아요',
    '새로운 친구들을 만나게 되어 신이 나요',
    '활발하다는 말을 많이 들어요',
    '친구들과 다같이 노는 걸 좋아해요',
    '다르게 내 생각대로 만드는 것이 더 즐거워요',
    '상상 속의 이야기가 좋아요',
    '잘 기억 못해요',
    '그리고 싶은 그림을 그리는 것이 좋아요',
    '"친구야, 울지 마."하고 달래줘요',
    '슬퍼서 울다가 말을 제대로 하지 못해요',
    '친절한 사람이 되고 싶어요',
    '쉽게 정하지 못해요',
    '새로운 방법으로 해보고 싶어요',
    '마지막까지 미루는게 좋아요',
    '바로 사용하기 쉽게 적당한 곳에 둬요',
    '특별한 계획 없이 즐겁게 보내는 것이 좋아요',
  ],
  //ISTJ
  choice2_LIST = [
    '친구가 먼저 다가오면 이야기를 하는 경우가 많아요',
    '새로운 친구들과 어떻게 지낼까 걱정이 돼요',
    '부끄러움을 많이 타요',
    '혼자 노는 걸 좋아해요',
    '비슷하게 만드는 것이 더 즐거워요',
    '실제 이야기가 좋아요',
    '잘 기억해요',
    '그려져 있는 그림을 예쁘게 색칠하는 것이 좋아요',
    '"친구야, 왜 울어?"하고 왜 우는지 물어봐요',
    '"그래서 이럴 수 밖에 없었어요."하고 이유를 설명해요',
    '공평한 사람이 되고 싶어요',
    '빨리 정해요',
    '전에 배웠던 방법으로 해보고 싶어요',
    '미리 끝내놓는 게 좋아요',
    '정해진 자리에 둬요',
    '미리 정해놓은 계획에 따라 보내는 것이 좋아요',
  ]

const USER_MBTI = 'currentMBTI'
const userChoice = []
let i = 0
let I = 0,
  E = 0,
  N = 0,
  S = 0,
  F = 0,
  T = 0,
  P = 0,
  J = 0
let IorE, NorS, ForT, PorJ

function resultLoader() {
  IorE = I > E ? 'I' : 'E'
  NorS = N > S ? 'N' : 'S'
  ForT = F > T ? 'F' : 'T'
  PorJ = P > J ? 'P' : 'J'

  const resultArr = [IorE, NorS, ForT, PorJ]
  const resultStr = resultArr.join('')
  localStorage.setItem(USER_MBTI, resultStr)

  const link = '/mbti_result'
  location.href = link
}

//확률로 추정해야 함
function resultJudgement() {
  for (i = 0; question_LIST[i]; i++) {
    switch (i) {
      case 0:
      case 10:
      case 8:
        if (userChoice[i] == 1) E += 30
        else I += 30
        break
      case 3:
      case 6:
      case 9:
        if (userChoice[i] == 1) N += 30
        else S += 30
        break
      case 1:
      case 5:
      case 7:
        if (userChoice[i] == 1) F += 30
        else T += 30
        break
      case 2:
      case 4:
      case 8:
        if (userChoice[i] == 1) P += 30
        else J += 30
        break
      default:
        break
    }
  }
  resultLoader()
}

function pgbarAnimation() {
  const preval = pgbar.value
  let id = setInterval(frame, 6)

  function frame() {
    if (pgbar.value >= preval + 6) {
      clearInterval(id)
    } else {
      pgbar.value += 0.5
    }
  }
}

function resetButtonStyle() {
  backgroundColor1 = choice1.style.background - color
  backgroundColor2 = choice2.style.background - color

  choice1.style.color = 'black'
  choice2.style.color = 'black'
  backgroundColor1 = 'white'
  backgroundColor2 = 'white'
}

function handleChoice1() {
  // fadeIn();
  userChoice[i++] = 1
  pgbarAnimation()

  if (question_LIST[i]) {
    question.innerText = question_LIST[i]
    choice1.innerText = choice1_LIST[i]
    choice2.innerText = choice2_LIST[i]
  } else resultJudgement()

  //resetButtonStyle();
  choice1.addEventListener('click', handleChoice1)
  choice2.addEventListener('click', handleChoice2)
  if (i >= 1) {
    backButton.style.visibility = 'visible'
  }
  backButton.addEventListener('click', handleBackButton)
}

function handleChoice2() {
  // fadeIn();
  userChoice[i++] = 2
  pgbarAnimation()

  if (question_LIST[i]) {
    question.innerText = question_LIST[i]
    choice1.innerText = choice1_LIST[i]
    choice2.innerText = choice2_LIST[i]
  } else resultJudgement()

  //resetButtonStyle();
  choice1.addEventListener('click', handleChoice1)
  choice2.addEventListener('click', handleChoice2)
  if (i >= 1) {
    backButton.style.visibility = 'visible'
  }
  backButton.addEventListener('click', handleBackButton)
}

function handleBackButton() {
  i--
  pgbar.value -= 6

  if (i >= 1) {
    question.innerText = question_LIST[i]
    choice1.innerText = choice1_LIST[i]
    choice2.innerText = choice2_LIST[i]
  } else if (i == 0) {
    question.innerText = question_LIST[i]
    choice1.innerText = choice1_LIST[i]
    choice2.innerText = choice2_LIST[i]
    backButton.style.visibility = 'hidden'
  }
}

function init() {
  // fadeIn();
  question.innerText = question_LIST[0]
  choice1.innerText = choice1_LIST[0]
  choice2.innerText = choice2_LIST[0]
  choice1.addEventListener('click', handleChoice1)
  choice2.addEventListener('click', handleChoice2)
}

init()
