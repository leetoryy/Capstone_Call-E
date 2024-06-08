// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
  'use strict';

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  var forms = document.querySelectorAll('.needs-validation');

  // Loop over them and prevent submission
  Array.prototype.slice.call(forms).forEach(function (form) {
      form.addEventListener(
          'submit',
          function (event) {
              if (!form.checkValidity()) {
                  event.preventDefault();
                  event.stopPropagation();
              }

              form.classList.add('was-validated');
          },
          false,
      );
  });

  document.querySelector('form.needs-validation').addEventListener('submit', function (event) {
      // 우선순위 선택 값 가져오기
      const priority1 = document.querySelector('input[name="paymentMethod1"]:checked').value;
      const priority2 = document.querySelector('input[name="paymentMethod2"]:checked').value;
      const priority3 = document.querySelector('input[name="paymentMethod3"]:checked').value;
      const priority4 = document.querySelector('input[name="paymentMethod4"]:checked').value;

      // 중복 여부 확인
      if (checkForDuplicates([priority1, priority2, priority3, priority4])) {
          // 중복이 있을 경우 폼 제출을 중지하고 에러 메시지를 표시
          event.preventDefault();
          alert('중복된 우선순위가 있습니다. 각 항목은 중복되지 않도록 선택해주세요.');
      }
  });

  // 중복 확인 함수
  function checkForDuplicates(values) {
      return new Set(values).size !== values.length;
  }
})();
