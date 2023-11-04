// 로그인 & 회원가입 전환
let container = document.getElementById('container')

toggle = () => {
  container.classList.toggle('sign-in')
  container.classList.toggle('sign-up')
}

setTimeout(() => {
  container.classList.add('sign-in')
}, 200)
// ---------------------------------------------------------------------

// 계정 유형 선택
document.addEventListener('DOMContentLoaded', function () {
  const userTypeButtons = document.querySelectorAll('.user-type-options button');
  const childInfoGroup = document.getElementById('child-info-group');
  const counselorInfoGroup = document.getElementById('counselor-info-group');

  userTypeButtons.forEach((button) => {
    button.addEventListener('click', function () {
      userTypeButtons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');
      document.getElementById('user-type').value = button.value;

      if (button.value === 'child') {
        childInfoGroup.style.display = 'block';
        counselorInfoGroup.style.display = 'none';
      } else {
        childInfoGroup.style.display = 'none';
        counselorInfoGroup.style.display = 'block';
      }
    });
  });

  // 초기 설정: 기본 값으로 아동 버튼이 선택되어 있음
  userTypeButtons[0].click();
});
// ---------------------------------------------------------------------

// 계정 유형 선택 버튼을 누르면 이전에 쓴 내용 초기화
function updateUserType(button) {
  const buttons = document.querySelectorAll('.user-type-options button');
  const selectedUserType = button.value;

  // 초기화할 입력 필드 목록
  const inputFields = document.querySelectorAll('#child-info-group input, #counselor-info-group input');

  buttons.forEach((btn) => {
      if (btn.value === selectedUserType) {
          btn.classList.add('active');
      } else {
          btn.classList.remove('active');
      }
  });

  // 입력 필드 초기화
  inputFields.forEach((input) => {
      input.value = '';
  });

  document.getElementById("user-type").value = selectedUserType;
}
// ---------------------------------------------------------------------