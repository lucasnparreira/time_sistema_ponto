function openNav() {
    document.getElementById("mySidenav").style.width = "390px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    
    setTimeout(() => {
        // location.reload();
    }, 200);
}