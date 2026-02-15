let isTransferring = false;
let threshold = 100;

// Easter egg
window.addEventListener('load', function() {
    console.log('Site "RoboCup Brasil" por\n\n ████  ████                     \n░░███ ░░███                     \n ░███  ░███  █████ ████  ██████ \n ░███  ░███ ░░███ ░███  ███░░███\n ░███  ░███  ░███ ░███ ░███ ░░░ \n ░███  ░███  ░███ ░███ ░███  ███\n █████ █████ ░░████████░░██████ \n░░░░░ ░░░░░   ░░░░░░░░  ░░░░░░  \n                                \n █████████████    ██████  █████ ████\n░░███░░███░░███  ███░░███░░███ ░███ \n ░███ ░███ ░███ ░███ ░███ ░███ ░███ \n ░███ ░███ ░███ ░███ ░███ ░███ ░███ \n █████░███ █████░░██████  ░░████████\n░░░░░ ░░░ ░░░░░  ░░░░░░    ░░░░░░░░ \n\nhttps://lluc.dev | https://github.com/lluckymou\n');
    console.log('%cAgora, o que você faz aqui? Sai fora hacker', "color: #ff0000;");
});

window.addEventListener('scroll', function() {
    if (isTransferring) return;

    const floatingHeader = document.querySelector('header.floating');
    const mainHeader = document.querySelector('header.main');
    const mainContent = document.querySelector('header main');

    if (!mainContent) return;

    const scrollY = window.scrollY;
    const targetParent = scrollY > threshold ? floatingHeader : mainHeader;

    if (!targetParent.contains(mainContent)) {
        isTransferring = true;
        mainContent.classList.add('transferring');

        setTimeout(() => {
            targetParent.appendChild(mainContent);
            
            if (targetParent === floatingHeader) {
                floatingHeader.classList.add('scrolled');
            } else {
                floatingHeader.classList.remove('scrolled');
            }

            requestAnimationFrame(() => {
                mainContent.classList.remove('transferring');
                setTimeout(() => {
                    isTransferring = false;
                }, 70);
            });
        }, 70);
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