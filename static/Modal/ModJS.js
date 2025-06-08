document.addEventListener('DOMContentLoaded', function () {
    const modalOverlay = document.getElementById('modalOverlay');
    const closeModal = document.getElementById('closeModal');
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    const modalContainer = document.querySelector('.modal-container');
    const modalFrame = document.getElementById('modalFrame');
    const copyBtn = document.getElementById('copyBtn');

    // Add openModal function to window object
    window.openModal = function(path) {
        modalFrame.src = path;
        modalOverlay.style.display = 'block';
    };

    // Copy button handler
    if (copyBtn) {
        copyBtn.addEventListener('click', async () => {
            try {
                const iframeDoc = modalFrame.contentDocument || modalFrame.contentWindow.document;
                const code = iframeDoc.body.innerHTML;
                await navigator.clipboard.writeText(code);
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                }, 2000);
            } catch (err) {
                console.error('Copy failed:', err);
                copyBtn.textContent = 'Error';
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                }, 2000);
            }
        });
    }

    // Fullscreen button handler
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', function () {
            if (!document.fullscreenElement) {
                if (modalContainer.requestFullscreen) {
                    modalContainer.requestFullscreen();
                } else if (modalContainer.mozRequestFullScreen) {
                    modalContainer.mozRequestFullScreen();
                } else if (modalContainer.webkitRequestFullscreen) {
                    modalContainer.webkitRequestFullscreen();
                } else if (modalContainer.msRequestFullscreen) {
                    modalContainer.msRequestFullscreen();
                }
                fullscreenBtn.textContent = '🗖';
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.mozCancelFullScreen) {
                    document.mozCancelFullScreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
                fullscreenBtn.textContent = '⛶';
            }
        });
    }

    // Close button handler
    if (closeModal) {
        closeModal.addEventListener('click', function () {
            modalOverlay.style.display = 'none';
            modalFrame.src = '';
            modalContainer.style.width = '50%';
            modalContainer.style.height = '50%';
            if (document.fullscreenElement) {
                document.exitFullscreen();
            }
        });
    }

    // Close on overlay click
    window.addEventListener('mousedown', function (event) {
        if (event.target === modalOverlay) {
            modalOverlay.style.display = 'none';
            modalFrame.src = '';
            modalContainer.style.width = '50%';
            modalContainer.style.height = '50%';
        }
    });

    // Handle iframe viewport
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
            console.error('Error updating viewport:', error);
        }
    });

    // Handle resize
    let isResizing = false;
    let currentHandle = null;
    let startWidth = 0;
    let startHeight = 0;
    let centerX = 0;
    let centerY = 0;

    document.querySelectorAll('.resize-handle').forEach(handle => {
        handle.addEventListener('mousedown', initResize);
    });

    function initResize(e) {
        e.preventDefault();
        isResizing = true;
        currentHandle = e.target;

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

        const mouseX = e.clientX;
        const mouseY = e.clientY;
        const dx = mouseX - centerX;
        const dy = mouseY - centerY;

        let newWidth = startWidth;
        let newHeight = startHeight;

        const handleClasses = currentHandle.classList;

        if (handleClasses.contains('right') || handleClasses.contains('left') || handleClasses.contains('corner')) {
            const halfWidth = Math.abs(dx);
            newWidth = halfWidth * 2;
        }

        if (handleClasses.contains('top') || handleClasses.contains('bottom') || handleClasses.contains('corner')) {
            const halfHeight = Math.abs(dy);
            newHeight = halfHeight * 2;
        }

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

document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".modal-header");
    if (header) {
        headerObserver.observe(header);
        updateButtons(); // Initial setup
    }
});

// Update on window resize
window.addEventListener("resize", updateButtons);
const resizeObserver = new ResizeObserver(entries => {
    const iframe = document.getElementById('modalFrame');
    iframe.contentWindow.postMessage({
        type: 'resize',
        width: iframe.offsetWidth,
        height: iframe.offsetHeight
    }, '*');
});

// Start on modal open
document.querySelectorAll('.js-modal-trigger').forEach(button => {
    button.addEventListener('click', () => {
        setTimeout(() => {
            resizeObserver.observe(document.querySelector('.modal-container'));
        }, 300);
    });
});