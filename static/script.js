function openNav() {
    document.getElementById("mySidenav").style.width = "390px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    
    setTimeout(() => {
        // location.reload();
    }, 200);
}

function toggleMenu() {
    var menu = document.getElementById("dropdownMenu");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function toggleSection(sectionId) {
    var section = document.getElementById(sectionId);
    section.style.display = section.style.display === "block" ? "none" : "block";
}

// Fecha o menu só se clicar fora do .menu-container
window.onclick = function(event) {
    if (!event.target.closest('.menu-container')) {
        var dropdowns = document.getElementsByClassName("menu-dropdown");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.style.display === "block") {
                openDropdown.style.display = "none";
            }
        }
    }
}
