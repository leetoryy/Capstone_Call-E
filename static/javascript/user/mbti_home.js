const startButton = document.querySelector(".js-start"),
    shareButton = document.querySelector(".js-share");

function handleStartClick(event){
    event.preventDefault();

    const link = '/user/mbti_test.html';
    location.href = link;
}

function init(){
    startButton.addEventListener("click", handleStartClick);
    shareButton.addEventListener("click", handleShareClick);
}

init();