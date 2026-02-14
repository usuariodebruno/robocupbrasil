window.addEventListener('scroll', function() {
    const floatingHeader = document.querySelector('header.floating');
    const mainHeader = document.querySelector('header.main');
    const mainContent = document.querySelector('main');

    if (window.scrollY > 100) {
        if (!floatingHeader.contains(mainContent)) {
            floatingHeader.appendChild(mainContent);
            floatingHeader.classList.add('scrolled');
        }
    } else {
        if (!mainHeader.contains(mainContent)) {
            mainHeader.appendChild(mainContent);
            floatingHeader.classList.remove('scrolled');
        }
    }
});

function toggleMenu() {
    const menu = document.getElementById('menu');
    const icon = document.getElementById('icon');
    
    menu.classList.toggle('active');

    

    icon.style.opacity = '0';
    setTimeout(() => {
        icon.classList.toggle('active');
        icon.style.opacity = '1';
    }, 100);

    setTimeout(() => {
        if(menu.classList.contains('active')) {
        const style = window.getComputedStyle(menu);
        const height = menu.offsetHeight + parseFloat(style.marginTop) + parseFloat(style.marginBottom);
        document.querySelector(':root').style.setProperty('--header-js', `${height}px`);
    } else {
        document.querySelector(':root').style.setProperty('--header-js', '0px');
    }
    }, 240);
}