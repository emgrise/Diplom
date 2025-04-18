document.addEventListener('DOMContentLoaded', function () {
    const modalOverlay = document.getElementById('modalOverlay');
    const closeModal = document.getElementById('closeModal');
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    const modalContainer = document.querySelector('.modal-container');
    const modalFrame = document.getElementById('modalFrame');
    
    modalFrame.addEventListener('load', () => {
        try {
            const iframeDoc = modalFrame.contentDocument || modalFrame.contentWindow.document;
            const viewportMeta = iframeDoc.querySelector('meta[name="viewport"]');
            
            if (viewportMeta) {
                viewportMeta.content = "width=device-width, initial-scale=1.0";
            } else {
                const newViewport = iframeDoc.createElement('meta');
                newViewport.name = "viewport";
                newViewport.content = "width=device-width, initial-scale=1.0";
                iframeDoc.head.appendChild(newViewport);
            }
        } catch (error) {
            console.error('Ошибка обновления viewport:', error);
        }
    });


    // Обработчики для кнопок открытия модалки
    document.querySelectorAll('.js-modal-trigger').forEach(button => {
        button.addEventListener('click', () => {
            const index = button.dataset.index;
            const iframe = document.getElementById('modalFrame');
            iframe.src = `/modal?index=${index}`;
            modalOverlay.style.display = 'block';
        });
    });

    closeModal.addEventListener('click', function () {
        modalOverlay.style.display = 'none';
        document.getElementById('modalFrame').src = '';
        modalContainer.style.width = '50%';
        modalContainer.style.height = '50%';
    });

    window.addEventListener('mousedown', function (event) {
        if (event.target === modalOverlay) {
            modalOverlay.style.display = 'none';
            modalContainer.style.width = '50%';
            modalContainer.style.height = '50%';
        }
    });

    fullscreenBtn.addEventListener('click', function () {
        const modalContainer = document.querySelector('.modal-container');
        if (!document.fullscreenElement) {
            if (modalContainer.requestFullscreen) {
                modalContainer.requestFullscreen();
            } else if (modalContainer.mozRequestFullScreen) { // Firefox
                modalContainer.mozRequestFullScreen();
            } else if (modalContainer.webkitRequestFullscreen) { // Chrome, Safari and Opera
                modalContainer.webkitRequestFullscreen();
            } else if (modalContainer.msRequestFullscreen) { // IE/Edge
                modalContainer.msRequestFullscreen();
            }
            
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.mozCancelFullScreen) { // Firefox
                document.mozCancelFullScreen();
            } else if (document.webkitExitFullscreen) { // Chrome, Safari and Opera
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { // IE/Edge
                document.msExitFullscreen();
            }
            
        }
    });
});
document.addEventListener('DOMContentLoaded', function () {
    const modalOverlay = document.getElementById('modalOverlay');
    const modalContainer = document.querySelector('.modal-container');
    const closeModal = document.getElementById('closeModal');
    const fullscreenBtn = document.getElementById('fullscreenBtn');

    // Track resizing state
    let isResizing = false;
    let currentHandle = null;

    // Store initial pointer points, center, and original width/height
    let startWidth = 0;
    let startHeight = 0;
    let centerX = 0;
    let centerY = 0;

    // Attach event listeners to each resize handle
    document.querySelectorAll('.resize-handle').forEach(handle => {
        handle.addEventListener('mousedown', initResize);
    });

    function initResize(e) {
        e.preventDefault();
        isResizing = true;
        currentHandle = e.target;

        // Get bounding rectangle and find center
        const rect = modalContainer.getBoundingClientRect();
        startWidth = rect.width;
        startHeight = rect.height;
        centerX = rect.left + rect.width / 2;
        centerY = rect.top + rect.height / 2;

        document.addEventListener('mousemove', doResize);
        document.addEventListener('mouseup', stopResize);
    }

    function doResize(e) {
        if (!isResizing) return;

        // Current mouse position
        const mouseX = e.clientX;
        const mouseY = e.clientY;

        // Distance from center
        const dx = mouseX - centerX;
        const dy = mouseY - centerY;

        // We start with the original width/height and adjust if needed
        let newWidth = startWidth;
        let newHeight = startHeight;

        // Identify the handle and adjust newWidth / newHeight
        const handleClasses = currentHandle.classList;

        // Horizontal dimension
        if (
            handleClasses.contains('right') ||
            handleClasses.contains('left') ||
            handleClasses.contains('corner')
        ) {
            // The new half-width is the absolute distance in x from center
            const halfWidth = Math.abs(dx);
            newWidth = halfWidth * 2; // total width is double the half-width
        }

        // Vertical dimension
        if (
            handleClasses.contains('top') ||
            handleClasses.contains('bottom') ||
            handleClasses.contains('corner')
        ) {
            // The new half-height is the absolute distance in y from center
            const halfHeight = Math.abs(dy);
            newHeight = halfHeight * 2;
        }

        // Constrain within min/max
        // newWidth = Math.max(minWidth, Math.min(newWidth, maxWidth));
        // newHeight = Math.max(minHeight, Math.min(newHeight, maxHeight));

        // Apply new dimensions (center is maintained by fixed top/left and transform)
        modalContainer.style.width = newWidth + 'px';
        modalContainer.style.height = newHeight + 'px';
    }

    function stopResize() {
        isResizing = false;
        currentHandle = null;
        document.removeEventListener('mousemove', doResize);
        document.removeEventListener('mouseup', stopResize);
    }
});

function adjustButtonText(button) {
    const containerWidth = document.querySelector('.modal-header').offsetWidth;
    
    if (containerWidth < 300) {
        button.innerHTML = button === closeModal ? "×" : "⛶";
    }else if (document.fullscreenElement) {
        fullscreenBtn.textContent = 'Windowed mode';
    }
    else if (!document.fullscreenElement) {
        button.innerHTML = button === closeModal ? "× Close" : "Fullscreen";
    }
}



// Отслеживаем изменения `.modal-header`
const headerObserver = new ResizeObserver(updateButtons);

document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".modal-header");
    if (header) {
        headerObserver.observe(header);
        updateButtons(); // Первоначальная настройка
    }
});

// Обновляем при изменении окна
window.addEventListener("resize", updateButtons);
const resizeObserver = new ResizeObserver(entries => {
    const iframe = document.getElementById('modalFrame');
    iframe.contentWindow.postMessage({
        type: 'resize',
        width: iframe.offsetWidth,
        height: iframe.offsetHeight
    }, '*');
});

// Запуск при открытии модалки
document.querySelectorAll('.js-modal-trigger').forEach(button => {
    button.addEventListener('click', () => {
        setTimeout(() => {
            resizeObserver.observe(document.querySelector('.modal-container'));
        }, 300);
    });
});