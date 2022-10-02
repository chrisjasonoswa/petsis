const body = document.querySelector("body"),
    sidebar = body.querySelector(".sidebar"),
    toggle = body.querySelector(".toggle"),
    searchBtn = body.querySelector(".search"),
    modeText = body.querySelector(".mode-text");


toggle.addEventListener("click", () => {
    const s = sidebar
    s.classList.toggle("close");
    if (s.classList.toggle === "close"){
        $(".nav-text").hide();
    }
    else{
        $(".nav-text").show();
    }
        

    
});

modeSwitch.addEventListener("click", () => {
    body.classList.toggle("dark");

    if (body.classList.contains("dark")) {
        modeText.innerText = "Light Mode"
    } else {
        {
            modeText.innerText = "Dark Mode"
        } }
});
