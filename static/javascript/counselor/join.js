// 로그인 & 회원가입 전환
let container = document.getElementById('container')

toggle = () => {
  container.classList.toggle('sign-in')
  container.classList.toggle('sign-up')

  // 계정 유형 선택 초기화
  const userTypeButtons = document.querySelectorAll('.user-type-options button')
  userTypeButtons.forEach((btn) => {
    btn.classList.remove('active')
  })

  // 아동 버튼이 기본 값으로 선택되도록 설정
  userTypeButtons[0].classList.add('active')

  // 회원가입 페이지에서 로그인 페이지로 전환될 때 계정 유형 선택 버튼이 아동 버튼이 선택되도록 설정
  if (container.classList.contains('sign-in')) {
    const signInUserTypeButtons = document.querySelectorAll('.sign-in #user-type-options-login button')
    signInUserTypeButtons.forEach((btn) => {
      btn.classList.remove('active')
    })
    signInUserTypeButtons[0].classList.add('active')

    // 로그인 페이지에서 아동 정보 그룹을 보이도록 설정
    const signInChildInfoGroup = document.getElementById('child-login-group')
    const signInCounselorInfoGroup = document.getElementById('counselor-login-group')
    signInChildInfoGroup.style.display = 'block'
    signInCounselorInfoGroup.style.display = 'none'
  }

  // 회원가입 페이지에서 로그인 페이지로 전환될 때 계정 유형 선택 버튼이 아동 버튼이 선택되도록 설정
  if (container.classList.contains('sign-up')) {
    const signUpUserTypeButtons = document.querySelectorAll('.sign-up #user-type-options-join button')
    signUpUserTypeButtons.forEach((btn) => {
      btn.classList.remove('active')
    })
    signUpUserTypeButtons[0].classList.add('active')

    // 회원가입 페이지에서 아동 정보 그룹을 보이도록 설정
    const signUpChildInfoGroup = document.getElementById('child-info-group')
    const signUpCounselorInfoGroup = document.getElementById('counselor-info-group')
    signUpChildInfoGroup.style.display = 'block'
    signUpCounselorInfoGroup.style.display = 'none'
  }
}

setTimeout(() => {
  container.classList.add('sign-in')
}, 200)

// 초기에 로그인 페이지에서 아동 버튼이 선택되도록 설정
document.addEventListener('DOMContentLoaded', function () {
  const signInUserTypeButtons = document.querySelectorAll('.sign-in #user-type-options-login button')
  signInUserTypeButtons[0].classList.add('active')

  const signInChildInfoGroup = document.getElementById('child-login-group')
  const signInCounselorInfoGroup = document.getElementById('counselor-login-group')
  signInChildInfoGroup.style.display = 'block'
  signInCounselorInfoGroup.style.display = 'none'
})

// ---------------------------------------------------------------------

// 회원가입 계정 유형 선택
document.addEventListener('DOMContentLoaded', function () {
  const signUpUserTypeButtons = document.querySelectorAll('.sign-up #user-type-options-join button')
  const signUpChildInfoGroup = document.getElementById('child-info-group')
  const signUpCounselorInfoGroup = document.getElementById('counselor-info-group')

  signUpUserTypeButtons.forEach((button) => {
    button.addEventListener('click', function () {
      signUpUserTypeButtons.forEach((btn) => btn.classList.remove('active'))
      button.classList.add('active')
      document.getElementById('user-type').value = button.value

      if (button.value === 'child') {
        signUpChildInfoGroup.style.display = 'block'
        signUpCounselorInfoGroup.style.display = 'none'
      } else {
        signUpChildInfoGroup.style.display = 'none'
        signUpCounselorInfoGroup.style.display = 'block'
      }
    })
  })
})

// 로그인 계정 유형 선택
document.addEventListener('DOMContentLoaded', function () {
  const signInUserTypeButtons = document.querySelectorAll('.sign-in #user-type-options-login button')
  const signInChildInfoGroup = document.getElementById('child-login-group')
  const signInCounselorInfoGroup = document.getElementById('counselor-login-group')

  signInUserTypeButtons.forEach((button) => {
    button.addEventListener('click', function () {
      signInUserTypeButtons.forEach((btn) => btn.classList.remove('active'))
      button.classList.add('active')
      document.getElementById('user-type').value = button.value

      if (button.value === 'child') {
        signInChildInfoGroup.style.display = 'block'
        signInCounselorInfoGroup.style.display = 'none'
      } else {
        signInChildInfoGroup.style.display = 'none'
        signInCounselorInfoGroup.style.display = 'block'
      }
    })
  })
})

// ---------------------------------------------------------------------

// 계정 유형 선택 버튼을 누르면 이전에 쓴 내용 초기화
function updateUserType(button) {
  const buttons = document.querySelectorAll('.user-type-options button')
  const selectedUserType = button.value

  // 초기화할 입력 필드 목록 (회원가입, 로그인 페이지의 입력 필드)
  const inputFields = document.querySelectorAll('#child-info-group input, #counselor-info-group input, #child-login-group input, #counselor-login-group input')

  buttons.forEach((btn) => {
    if (btn.value === selectedUserType) {
      btn.classList.add('active')
    } else {
      btn.classList.remove('active')
    }
  })

  // 입력 필드 초기화
  inputFields.forEach((input) => {
    input.value = ''
  })

  // 체크박스 초기화
  const checkboxes = document.querySelectorAll('#child-info-group input[type="checkbox"], #counselor-info-group input[type="checkbox"]')
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false
  })

  // MBTI 드롭다운 초기화
  const mbtiDropdown = document.getElementById('mbti-dropdown')
  if (mbtiDropdown) {
    mbtiDropdown.value = ''
  }

  document.getElementById('user-type').value = selectedUserType
}

// ---------------------------------------------------------------------
