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


  //아동 비밀번호 확인
  function childcheckPasswordMatch() {
      var password = document.getElementById("child-password").value;
      var confirmPassword = document.getElementById("child-confirm-password").value;
      var matchMessage = document.getElementById("password-match-message");
      matchMessage.innerHTML = ""

      if (password !== confirmPassword) {
          matchMessage.innerHTML = "비밀번호가 일치하지 않습니다. 비밀번호를 다시 확인해 주세요.";
      } else {
          matchMessage.innerHTML = "";
      }
  }

  //상담사 비밀번호 확인
  function counselorcheckPasswordMatch() {
    var co_password = document.getElementById("counselor_pw").value;
    var co_confirmPassword = document.getElementById("counselor-confirm-password").value;
    var co_matchMessage = document.getElementById("co_password-match-message");
    co_matchMessage.innerHTML = ""

      if (co_password !== co_confirmPassword) {
          co_matchMessage.innerHTML = "비밀번호가 일치하지 않습니다. 비밀번호를 다시 확인해 주세요.";
      } else {
          co_matchMessage.innerHTML = "";
      }
    
  }

  
// 아동 아이디 중복 검사
function checkID() {
  // 아이디 입력란에서 아이디 가져오기
  var childId = document.getElementById("child_id").value;

  // 중복 확인 결과를 표시할 메시지 엘리먼트
  var duplicateIdMessage = document.getElementById("duplicate-id-message");

  // 새로운 요청을 보내기 전에 메시지 초기화
  duplicateIdMessage.innerHTML = "";

  console.log("Sending request to server with child_id:", childId);

  // 아이디 중복 검사를 서버 쪽에서 수행 (AJAX를 사용하여 비동기적으로 처리)
  $.ajax({
      type: "POST",
      url: "/check_id_duplicate",
      data: { "child_id": childId },
      success: function(response) {
          console.log("Server response:", response);

          // 서버 응답이 JSON 형태인지 확인
          if (response && typeof response === 'object') {
              // duplicate 필드를 직접 확인
              if (response.duplicate !== undefined) {
                  if (response.duplicate) {
                      duplicateIdMessage.innerHTML = "이미 사용 중인 아이디입니다.";
                      // 아이디 중복 시 회원가입 버튼 비활성화 (선택사항)
                      document.getElementById("signupClick").disabled = true;
                  } else {
                      duplicateIdMessage.innerHTML = "사용 가능한 아이디입니다.";
                      
                  }
              } else if (response.result === null) {
                  // 쿼리 결과가 None이면 아이디가 중복되지 않은 것으로 처리
                  duplicateIdMessage.innerHTML = "사용 가능한 아이디입니다.";
                  
              } else {
                  // 응답이 예상치 못한 형태인 경우
                  console.error("Unexpected server response format.");
              }
          } else {
              // 응답이 JSON 형태가 아니라면 예외 처리 또는 적절한 로깅 수행
              console.error("Unexpected server response format.");
          }
      },
      error: function(error) {
          console.error("Error checking ID duplicate:", error);
          duplicateIdMessage.innerHTML = "중복 확인 중 오류가 발생했습니다.";
      }
  });
}

// 상담사 사번 이름 일치 확인
function RegistrationID() {
var counselorName = document.getElementById("counselor_name").value;
var counselorID = document.getElementById("counselor_id").value;
var RegistrationIdMessage = document.getElementById("Registration-id-message");
var signupButton = document.getElementById("signupClick");

// 새로운 요청 전 메시지 초기화
RegistrationIdMessage.innerHTML = "";

console.log("counselor_name 및 counselor_id로 서버에 요청 보내기:", counselorName, counselorID);

$.ajax({
    type: "POST",
    url: "/check_name_and_id_association",
    data: {
        "counselor_name": counselorName,
        "counselor_id": counselorID
    },
    success: function(response) {
        console.log("서버 응답:", response);

        if (response && typeof response === 'object') {
            // 두 조건이 모두 참이면 "이름과 사번이 일치합니다"로 판단
            if (response.name_associated_with_id && response.id_associated_with_name) {
                RegistrationIdMessage.innerHTML = "이름과 사번이 일치합니다.";
                
            } else {
                RegistrationIdMessage.innerHTML = "이름과 사번이 일치하지 않습니다.";
                signupButton.disabled = true; // 회원가입 버튼 비활성화

                // 입력값 초기화 
                document.getElementById("counselor_name").value = "";
                document.getElementById("counselor_id").value = "";
            }
        } else {
            console.error("예상치 못한 서버 응답 형식입니다.");
        }
    },
    error: function(error) {
        console.error("이름과 사번 연관성 확인 중 오류:", error);
        RegistrationIdMessage.innerHTML = "이름과 사번 확인 중 오류가 발생했습니다.";
        signupButton.disabled = true; // 오류 발생 시 회원가입 버튼 비활성화
    }
});
}

function intext() {
  // MBTI 드롭다운에서 선택된 값 가져오기
  var selectedMBTI = document.getElementById("mbti-dropdown").value;
  console.log("Selected MBTI:", selectedMBTI);

  // 체크박스에서 선택된 값들 가져오기
  var checkedAreas = [];
  var checkboxElements = document.querySelectorAll('.input-group-checkbox input[type="checkbox"]:checked');
  checkboxElements.forEach(function(checkbox) {
      checkedAreas.push(checkbox.nextElementSibling.nextElementSibling.innerText);
  });

  console.log("Checked Areas:", checkedAreas);
  
  // 가져온 값들을 서버로 전송할 FormData에 추가
  formData.append('mbti', selectedMBTI);
  formData.append('areas', checkedAreas.join(','));  // 여러 값이면 쉼표로 구분하여 전송

  // AJAX를 사용하여 서버로 전송
  $.ajax({
    type: 'POST',
    url: '/join',
    data: formData,
    contentType: false,
    processData: false,
    success: function(response) {
        console.log('Server response:', response);
        
    },
    error: function(error) {
        console.error('Error submitting form:', error);
        
    }
});
}


function submitForm() {
  // 선택된 사용자 유형에 따라 폼을 유효성 검사
  if (validateForms()) {
    // 유효성 검사가 성공하면 폼을 제출합니다.

    // 선택된 회원가입 폼에 따라 FormData 생성
    var formData = new FormData();

    if (document.getElementById('child-info-group').style.display !== 'none') {
      // 아동 회원가입 폼 필드 추가
      formData.append('user_type', 'child');
      formData.append('ch_name', document.getElementById('child_name').value);
      formData.append('ch_id', document.getElementById('child_id').value);
      formData.append('ch_pw', document.getElementById('child-password').value);
      formData.append('ch_pw2', document.getElementById('child-confirm-password').value);
      formData.append('ch_ph', document.getElementById('child_phone_num').value);
      formData.append('ch_email', document.getElementById('child_email').value);
      formData.append('ch_by', document.getElementById('child-birth-year').value);
      formData.append('ch_bm', document.getElementById('child-birth-month').value);
      formData.append('ch_bd', document.getElementById('child-birth-day').value);
      formData.append('ch_address', document.getElementById('child-address').value);
      formData.append('pa_name',document.getElementById('parent_name').value);

    } else if (document.getElementById('counselor-info-group').style.display !== 'none') {
      // 상담사 회원가입 폼 필드 추가
      formData.append('user_type', 'counselor');
      formData.append('co_name', document.getElementById('counselor_name').value);
      formData.append('co_id', document.getElementById('counselor_id').value);
      formData.append('co_pw', document.getElementById('counselor_pw').value);
      formData.append('co_pw2', document.getElementById('counselor-confirm-password').value);
      formData.append('co_phone', document.getElementById('counselor_phone').value);
      formData.append('co_email', document.getElementById('counselor_email').value);
      formData.append('co_birth_year', document.getElementById('counselor-birth-year').value);
      formData.append('co_birth_month', document.getElementById('counselor-birth-month').value);
      formData.append('co_birth_day', document.getElementById('counselor-birth-day').value);
      // MBTI 드롭다운에서 선택된 값 가져오기
      var selectedMBTI = document.getElementById("mbti-dropdown").value;
      console.log("Selected MBTI:", selectedMBTI);

      // 체크박스에서 선택된 값들 가져오기
      var checkedAreas = [];
      var checkboxElements = document.querySelectorAll('.input-group-checkbox input[type="checkbox"]:checked');
      checkboxElements.forEach(function (checkbox) {
        checkedAreas.push(checkbox.nextElementSibling.nextElementSibling.innerText);
      });

      console.log("Checked Areas:", checkedAreas);

      // 가져온 값들을 서버로 전송할 FormData에 추가
      formData.append('mbti', selectedMBTI);
      formData.append('areas', checkedAreas.join(','));  // 여러 값이면 쉼표로 구분하여 전송
    }

    // AJAX를 사용하여 서버로 전송
    $.ajax({
      type: 'POST',
      url: '/join',
      data: formData,
      contentType: false,
      processData: false,
      success: function (response) {
        console.log('서버 응답:', response);
        if (response && response.user_type === 'child') {
          console.log('아동 회원가입 성공');
          var childID = response.child_id;
          var parentName = response.parent_name;
          // parentName 값을 guardianName 입력란에 설정
          $('#guardianName').val(parentName);

      // 페이지 이동
          window.location.href = '/survey_pre?child_id=' + childID + '&parent_name=' + parentName;
        } else if (response && response.user_type === 'counselor') {
          console.log('상담사 회원가입 성공');
          window.location.href = '/';
        } else {
          console.log('조건에 맞는 경우 없음');
        }

      },
      error: function (error) {
        console.error('폼 제출 중 오류:', error);

        
      }
    });
  }
}


function submitloginForm() {
  // 선택된 로그인 폼에 따라 FormData 생성
  var formData = new FormData();

  if (document.getElementById('child-login-group').style.display !== 'none') {
    // 아동 로그인 폼 필드 추가
    formData.append('user_type', 'child');
    formData.append('ch_id2', document.getElementById('child_ID2').value);
    formData.append('ch_pw_2', document.getElementById('child_pw2').value);
  } else if (document.getElementById('counselor-login-group').style.display !== 'none') {
    // 상담사 로그인 폼 필드 추가
    formData.append('user_type', 'counselor');
    formData.append('co_id2', document.getElementById('counselor_id2').value);
    formData.append('co_pw_2', document.getElementById('counselor_pw2').value);
  }

  // AJAX를 사용하여 서버로 전송
  $.ajax({
    type: 'POST',
    url: '/login',
    data: formData,
    contentType: false,
    processData: false,
    success: function (response) {
        console.log('서버 응답:', response);

        if (response && response.user_type === 'child') {
            console.log('아동 로그인 성공');
            var childID = document.getElementById('child_ID2').value;
            console.log('childID:', childID);
           // window.location.href = '/mbti_match?child_id=' + encodeURIComponent(childID);
            window.location.href = '/user_home'
            
        } else if (response && response.user_type === 'counselor') {
            console.log('상담사 로그인 성공');
            var counselorName = response.counselor_name;
            console.log('상담사 이름:', counselorName);

            // 페이지 이동
            window.location.href = '/counselor_home?counselor_name=' + encodeURIComponent(counselorName);
        } else {
            console.log('조건에 맞는 경우 없음');
        }
    },
    error: function (error) {
        console.error('폼 제출 중 오류:', error);
    }
});

}

