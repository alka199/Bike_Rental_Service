
let menu = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navbar');


menu.onclick = () => {
    menu.classList.toggle('bi-x');
    navbar.classList.toggle('active');
}

window.onscroll = () => {
    menu.classList.remove('bi-x');
    navbar.classList.remove('active');
}