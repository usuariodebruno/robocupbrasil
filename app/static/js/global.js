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