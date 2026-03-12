let intervalObject = function(){};
function start_interval(){
    let minutes = 29;
    let seconds = 59;
    const close_modal = document.getElementsByClassName("btn-close-modal");
    close_modal[0].setAttribute("disabled", "");
    const temp = document.getElementById("counter-timer");
    const btn_footer = document.getElementById("btn-footer");
    temp.innerHTML="01h:00m:00s";
    intervalObject= setInterval(function(){
        temp.textContent = `00h:${minutes.toString().padStart(2,'0')}m:${seconds.toString().padStart(2,'0')}s`;
        if(minutes === 0 && seconds === 0){
            clearInterval(interval);
            temp.style.color = "red";
        }
        if(minutes === 5 && seconds === 59){
            blinking(temp);
        }
        if(seconds === 0){
            minutes--;
            seconds = 59;
        } else {
            seconds --;
        }
    }, 1000);
    btn_footer.innerHTML = "<button id='btn-lunch' class='btn btn-success' type='button' disabled>Lunch Out</button>";
}

function blinking(element) {
    const btn_lunch = document.getElementById("btn-lunch");
    btn_lunch.removeAttribute("disabled");
    btn_lunch.addEventListener("click",function(){
        clearInterval(intervalObject);
        AttendanceControl("Lunch-Out");    
    },false);
    element.classList.add("blink");
    element.style.color = "red";
    element.classList.remove("text-muted");
}