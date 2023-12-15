const startButton = document.querySelector(".js-start");

function handleStartClick(event){
    event.preventDefault();

    const link = '/mbti_test';
    location.href = link;
}

function init(){
    startButton.addEventListener("click", handleStartClick);
}

init();