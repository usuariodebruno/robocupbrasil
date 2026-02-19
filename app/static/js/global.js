let isTransferring = false;
let threshold = 100;

// Easter egg
window.addEventListener('load', function() {
    console.log('CMS RoboCup Brasil por\n\n ████  ████                     \n░░███ ░░███                     \n ░███  ░███  █████ ████  ██████ \n ░███  ░███ ░░███ ░███  ███░░███\n ░███  ░███  ░███ ░███ ░███ ░░░ \n ░███  ░███  ░███ ░███ ░███  ███\n █████ █████ ░░████████░░██████ \n░░░░░ ░░░░░   ░░░░░░░░  ░░░░░░  \n                                \n █████████████    ██████  █████ ████\n░░███░░███░░███  ███░░███░░███ ░███ \n ░███ ░███ ░███ ░███ ░███ ░███ ░███ \n ░███ ░███ ░███ ░███ ░███ ░███ ░███ \n █████░███ █████░░██████  ░░████████\n░░░░░ ░░░ ░░░░░  ░░░░░░    ░░░░░░░░ \n\nhttps://lluc.dev | https://github.com/lluckymou\n');
    console.log('%cAgora, o que você faz aqui? Sai fora hacker\n', "color: #ff0000;");
    setupTabs();
    setupCarousel();
    setupAdminShortcut();
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

function setupTabs() {
    document.querySelectorAll('.tabs').forEach(tabsContainer => {
        const buttons = Array.from(tabsContainer.querySelectorAll('[data-tab]'))
                             .filter(btn => btn.closest('.tabs') === tabsContainer);
        
        if (buttons.length === 0) return;

        const contentContainer = tabsContainer.querySelector('.tab-content');
        const panes = contentContainer 
            ? Array.from(contentContainer.querySelectorAll('.tab-pane'))
                   .filter(pane => pane.closest('.tabs') === tabsContainer)
            : [];

        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();

                buttons.forEach(btn => btn.classList.remove('active'));
                panes.forEach(pane => pane.classList.remove('active'));

                button.classList.add('active');
                const tabId = button.dataset.tab;
                const targetPane = panes.find(p => p.id === tabId);
                if (targetPane) {
                    targetPane.classList.add('active');
                }
            });
        });

        // Activate first tab if none are active
        const hasActive = buttons.some(btn => btn.classList.contains('active'));
        if (!hasActive && buttons.length > 0) {
            buttons[0].click();
        }
    });
}

function setupCarousel() {
    document.querySelectorAll('.carousel').forEach(carousel => {
        const track = carousel.querySelector('.carousel-track');
        const slides = Array.from(track.children);
        const dotsContainer = carousel.querySelector('.carousel-dots');
        const dots = Array.from(dotsContainer.children);
        const prevBtn = carousel.querySelector('.carousel-nav.prev');
        const nextBtn = carousel.querySelector('.carousel-nav.next');
        
        let currentIndex = 0;
        let interval;
        let isLocked = false;
        let duration = parseInt(carousel.dataset.duration) || 10000;
        
        const updateCarousel = () => {
            track.style.transform = `translateX(-${currentIndex * 100}%)`;
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentIndex);
                dot.innerHTML = '';
                if (index === currentIndex && isLocked) {
                    dot.innerHTML = '<i class="fa fa-lock"></i>';
                }
            });
        };

        const nextSlide = () => {
            currentIndex = (currentIndex + 1) % slides.length;
            updateCarousel();
        };

        const prevSlide = () => {
            currentIndex = (currentIndex - 1 + slides.length) % slides.length;
            updateCarousel();
        };

        const startAutoScroll = () => {
            if (interval) clearInterval(interval);
            if (!isLocked) {
                interval = setInterval(nextSlide, duration);
            }
        };

        const stopAutoScroll = () => {
            if (interval) clearInterval(interval);
        };

        const lock = () => {
            isLocked = true;
            stopAutoScroll();
            updateCarousel();
            carousel.classList.add('locked');
        };

        const unlock = () => {
            isLocked = false;
            startAutoScroll();
            updateCarousel();
            carousel.classList.remove('locked');
        };

        // Event Listeners
        dots.forEach((dot, index) => {
            dot.addEventListener('click', (e) => {
                e.stopPropagation();
                currentIndex = index;
                lock();
                updateCarousel();
            });
        });

        [prevBtn, nextBtn].forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (btn === prevBtn) prevSlide(); else nextSlide();
                lock();
            });
        });

        // Drag / Swipe Logic
        let startX = 0;
        let isDown = false;

        const handleDragStart = (e) => {
            isDown = true;
            startX = e.type.includes('mouse') ? e.pageX : e.touches[0].clientX;
            stopAutoScroll();
        };

        const handleDragEnd = (e) => {
            if (!isDown) return;
            isDown = false;
            const endX = e.type.includes('mouse') ? e.pageX : e.changedTouches[0].clientX;
            const diff = endX - startX;

            if (Math.abs(diff) > 50) { // Drag threshold
                if (diff > 0) prevSlide(); else nextSlide();
                lock();
            } else {
                // Click logic (if not dragged significantly)
                if (carousel.contains(e.target) && !e.target.closest('.carousel-nav') && !e.target.closest('.carousel-dots')) {
                    lock();
                }
            }
            if (!isLocked) startAutoScroll();
        };

        track.addEventListener('mousedown', handleDragStart);
        track.addEventListener('touchstart', handleDragStart, {passive: true});
        
        track.addEventListener('mouseup', handleDragEnd);
        track.addEventListener('touchend', handleDragEnd);
        
        track.addEventListener('mouseleave', () => {
            if (isDown) {
                isDown = false;
                if (!isLocked) startAutoScroll();
            }
        });

        // Global unlock click
        document.addEventListener('click', (e) => {
            if (!carousel.contains(e.target) && isLocked) {
                unlock();
            }
        });

        startAutoScroll();
    });
}

function setupAdminShortcut() {
    const targets = document.querySelectorAll('header.floating div:first-child');
    
    targets.forEach(target => {
        let timer;
        
        const start = () => {
            target.classList.add('holding');
            timer = setTimeout(() => {
                window.location.href = '/admin/';
            }, 2000);
        };

        const end = () => {
            target.classList.remove('holding');
            clearTimeout(timer);
        };

        target.addEventListener('mousedown', (e) => { if (e.button === 0) start(); });
        target.addEventListener('touchstart', start, { passive: true });

        ['mouseup', 'mouseleave', 'touchend', 'touchcancel'].forEach(evt => target.addEventListener(evt, end));

        target.addEventListener('contextmenu', (e) => e.preventDefault());
    });
}