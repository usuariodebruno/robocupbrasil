var dFlipLocation = '/static/js/dflip/';

let isTransferring = false;
let threshold = 100;

// Easter egg
window.addEventListener('load', function() {
    console.log('CMS RoboCup Brasil por\n\n ████  ████                     \n░░███ ░░███                     \n ░███  ░███  █████ ████  ██████ \n ░███  ░███ ░░███ ░███  ███░░███\n ░███  ░███  ░███ ░███ ░███ ░░░ \n ░███  ░███  ░███ ░███ ░███  ███\n █████ █████ ░░████████░░██████ \n░░░░░ ░░░░░   ░░░░░░░░  ░░░░░░  \n                                \n █████████████    ██████  █████ ████\n░░███░░███░░███  ███░░███░░███ ░███ \n ░███ ░███ ░███ ░███ ░███ ░███ ░███ \n ░███ ░███ ░███ ░███ ░███ ░███ ░███ \n █████░███ █████░░██████  ░░████████\n░░░░░ ░░░ ░░░░░  ░░░░░░    ░░░░░░░░ \n\nhttps://lluc.dev | https://github.com/lluckymou\n');
    console.log('%cAgora, o que você faz aqui? Sai fora hacker\n', "color: #ff0000;");
    setupTabs();
    setupCarousel();
    setupAdminShortcut();
    setupCalendar();
    setupDraggableScroll();
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

function setupCalendar() {
    const calendarComponent = document.getElementById('calendar-component');
    if (!calendarComponent) return;

    const eventsScript = document.getElementById('calendar-events');
    const eventsData = (eventsScript && JSON.parse(eventsScript.textContent)) || [];
    const grid = document.getElementById('rcb-calendar-days');
    const weekdaysContainer = document.getElementById('rcb-calendar-weekdays');
    const monthDisplay = document.getElementById('cal-month');
    const prevBtn = document.getElementById('cal-prev');
    const nextBtn = document.getElementById('cal-next');

    let currentDate = new Date();
    const minDate = new Date();

    // toISOString() converte para UTC e adiantaria o dia em fusos a leste de Greenwich.
    function toDateKey(d) {
        const mes = String(d.getMonth() + 1).padStart(2, '0');
        const dia = String(d.getDate()).padStart(2, '0');
        return `${d.getFullYear()}-${mes}-${dia}`;
    }

    // Hover Sync Logic
    function setHover(dateKey, active) {
        if (!dateKey) return;

        document.querySelectorAll(`.calendar-day[data-date="${dateKey}"]`).forEach(el => {
            el.classList.toggle('hover-sync', active);
        });

        // O card da lista guarda o intervalo inteiro: casar pelo dia exato só
        // acenderia o card no primeiro dia de um evento de vários dias.
        document.querySelectorAll('.event-card').forEach(card => {
            const inicio = card.dataset.date;
            if (!inicio) return;
            const fim = card.dataset.dateFim || inicio;
            card.classList.toggle('hover-sync', active && dateKey >= inicio && dateKey <= fim);
        });
    }

    // Add hover to static list items once
    const listItems = document.querySelectorAll('.event-card');
    listItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            const dateStr = item.dataset.date;
            if (dateStr) {
                const [y, m, d] = dateStr.split('-').map(Number);
                if (currentDate.getFullYear() !== y || currentDate.getMonth() !== (m - 1)) {
                    currentDate.setFullYear(y);
                    currentDate.setMonth(m - 1);
                    renderCalendar(currentDate.getFullYear(), currentDate.getMonth());
                }
                setHover(dateStr, true);
            }
        });
        item.addEventListener('mouseleave', () => setHover(item.dataset.date, false));
    });

    function renderCalendar(year, month) {
        const monthName = new Date(year, month).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
        monthDisplay.textContent = monthName.charAt(0).toUpperCase() + monthName.slice(1);
        grid.innerHTML = '';
        if (weekdaysContainer) weekdaysContainer.innerHTML = '';

        // Visibility of Prev Button
        if (year === minDate.getFullYear() && month === minDate.getMonth()) {
            prevBtn.style.visibility = 'hidden';
        } else {
            prevBtn.style.visibility = 'visible';
        }

        // Render Weekdays
        if (weekdaysContainer) {
            const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
            weekdays.forEach(day => {
                const daySpan = document.createElement('span');
                daySpan.textContent = day;
                weekdaysContainer.appendChild(daySpan);
            });
        }

        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);
        
        for (let i = 0; i < firstDayOfMonth.getDay(); i++) {
            const blankCell = document.createElement('div');
            blankCell.className = 'calendar-day blank';
            grid.appendChild(blankCell);
        }

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        for (let d = 1; d <= lastDayOfMonth.getDate(); d++) {
            const dayDate = new Date(year, month, d);
            const dateKey = toDateKey(dayDate);
            // Um evento ocupa todos os dias entre date e date_fim (inclusive).
            const eventsForDay = eventsData.filter(e => dateKey >= e.date && dateKey <= (e.date_fim || e.date));

            const cell = document.createElement('div');
            cell.className = 'calendar-day';
            cell.dataset.date = dateKey;

            cell.addEventListener('mouseenter', () => setHover(dateKey, true));
            cell.addEventListener('mouseleave', () => setHover(dateKey, false));

            if (dayDate < today) {
                cell.classList.add('past-day');
            }
            if (dayDate.getTime() === today.getTime()) {
                cell.classList.add('today');
            }

            const dayNumber = document.createElement('strong');
            dayNumber.className = 'day-number';
            dayNumber.textContent = d;
            cell.appendChild(dayNumber);

            if (eventsForDay.length > 0) {
                const linesContainer = document.createElement('div');
                linesContainer.className = 'event-lines-container flex flex-column';
                
                eventsForDay.forEach(event => {
                    const eventLine = document.createElement('div');
                    eventLine.className = 'event-line';
                    eventLine.style.backgroundColor = event.cor;

                    // Repetir a descrição em cada dia do intervalo polui a barra, então
                    // o texto só aparece onde a barra recomeça visualmente: no primeiro
                    // dia do evento, a cada domingo (quebra de linha da grade) e no dia
                    // 1º, quando o intervalo vem emendado do mês anterior.
                    const startsVisibleRun = dateKey === event.date
                        || dayDate.getDay() === 0
                        || d === 1;

                    const label = document.createElement('span');
                    if (startsVisibleRun) {
                        label.textContent = event.descricao;
                    }
                    eventLine.appendChild(label);

                    if (event.link) {
                        const link = document.createElement('a');
                        link.href = event.link;
                        link.target = '_blank';
                        link.title = event.descricao;
                        link.appendChild(eventLine);
                        linesContainer.appendChild(link);
                    } else {
                        eventLine.title = event.descricao;
                        linesContainer.appendChild(eventLine);
                    }
                });
                cell.appendChild(linesContainer);
            }
            grid.appendChild(cell);
        }

        // Apply corner radius logic dynamically
        const cells = grid.children;
        const totalCells = cells.length;
        const cols = 7;
        const rows = Math.ceil(totalCells / cols);
        const radius = 'calc(var(--default-measure) * 0.5)';

        if (totalCells > 0) {
            // Top Corners
            cells[0].style.borderTopLeftRadius = radius;
            if (cells[6]) cells[6].style.borderTopRightRadius = radius;

            // Bottom Corners
            const bottomLeftIndex = (rows - 1) * cols;
            if (cells[bottomLeftIndex]) cells[bottomLeftIndex].style.borderBottomLeftRadius = radius;

            const bottomRightIndex = (rows * cols) - 1;
            if (cells[bottomRightIndex]) cells[bottomRightIndex].style.borderBottomRightRadius = radius;
        }
    }

    prevBtn.addEventListener('click', () => {
        const prevMonthDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
        const minMonthDate = new Date(minDate.getFullYear(), minDate.getMonth(), 1);
        if (prevMonthDate < minMonthDate) return;

        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate.getFullYear(), currentDate.getMonth());
    });

    nextBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate.getFullYear(), currentDate.getMonth());
    });

    renderCalendar(currentDate.getFullYear(), currentDate.getMonth());
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

function setupDraggableScroll() {
    document.querySelectorAll('.scroll-wrapper').forEach(wrapper => {
        const slider = wrapper.querySelector('.scroll-items');
        if (!slider) return;
        
        const indicator = wrapper.querySelector('.scroll-indicator');
        const isScrollable = slider.scrollWidth > slider.clientWidth;

        if (!isScrollable) {
            if (indicator) indicator.style.display = 'none';
            slider.style.cursor = 'default';
            return;
        } else if(indicator) {
            slider.style.justifyContent = 'start';
            indicator.style.display = 'block';
        }

        if (indicator) {
            slider.addEventListener('scroll', () => {
                indicator.style.opacity = '0';
            }, { once: true });
        }

        let isDown = false;
        let startX;
        let scrollLeft;

        const start = (e) => {
            isDown = true;
            slider.classList.add('grabbing');
            startX = (e.pageX || e.touches[0].pageX) - slider.offsetLeft;
            scrollLeft = slider.scrollLeft;
        };

        const end = () => {
            isDown = false;
            slider.classList.remove('grabbing');
        };

        const move = (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = (e.pageX || e.touches[0].pageX) - slider.offsetLeft;
            const walk = (x - startX);
            slider.scrollLeft = scrollLeft - walk;
        };

        slider.addEventListener('mousedown', start);
        slider.addEventListener('touchstart', start, { passive: false });

        ['mouseup', 'mouseleave', 'touchend', 'touchcancel'].forEach(evt => slider.addEventListener(evt, end));

        slider.addEventListener('mousemove', move);
        slider.addEventListener('touchmove', move);
    });
}

function rcb_change_page(param, delta, anchor) {
    try {
        const url = new URL(window.location.href);
        const cur = parseInt(url.searchParams.get(param) || '0');
        const next = Math.max(0, cur + delta);
        url.searchParams.set(param, next);
        const base = url.toString().split('#')[0];
        window.location.assign(base + '#' + anchor);
    } catch(e) { console.warn(e); }
}

// PDF Viewer Functions
let activeBook = null;

function showPDFViewer(event, pdfUrl) {
    event.preventDefault();
    const component = event.target.closest('#arquivos-component');
    if (!component) return;
    
    const list = component.querySelector('.arquivo-list');
    const viewer = component.querySelector('.arquivo-visualizador');
    const book = component.querySelector('.arquivo-pdf');
    
    // Trigger transitions
    list.classList.add('pdf-viewer-active');
    viewer.classList.add('pdf-viewer-active');
    
    // Initialize dFlip after transition
    setTimeout(() => {
        // Add the class so dFlip recognizes it
        book.classList.add('_df_book');
        
        // Initialize dFlip
        if (window.DFLIP && window.jQuery) {
            // Dispose previous instance if exists (safety check)
            if (activeBook) {
                activeBook.dispose();
                activeBook = null;
            }
            activeBook = jQuery(book).flipBook(pdfUrl);
        }
    }, 300);
}

function closePDFViewer(event) {
    event.preventDefault();
    const component = event.target.closest('#arquivos-component');
    if (!component) return;
    
    const list = component.querySelector('.arquivo-list');
    const viewer = component.querySelector('.arquivo-visualizador');
    const book = component.querySelector('.arquivo-pdf');
    
    // Remove active classes
    list.classList.remove('pdf-viewer-active');
    viewer.classList.remove('pdf-viewer-active');
    
    // Clean up after transition
    setTimeout(() => {
        if (activeBook) {
            activeBook.dispose();
            activeBook = null;
        }

        book.classList.remove('_df_book');
        book.innerHTML = '';
        book.removeAttribute('source');
    }, 300);
}