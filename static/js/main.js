document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });

    // Handle page loader
    const pageLoader = document.querySelector('.page-loader');
    if (pageLoader) {
        window.addEventListener('load', () => {
            pageLoader.style.opacity = '0';
            setTimeout(() => {
                pageLoader.style.display = 'none';
            }, 500);
        });
    }

    // Handle navigation active state
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Handle search functionality
    const searchInput = document.querySelector('.search-input');
    const searchButton = document.querySelector('.search-button');
    const effectCards = document.querySelectorAll('.effect-card');

    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        let hasResults = false;

        effectCards.forEach(card => {
            const title = card.querySelector('.card-title').textContent.toLowerCase();
            const description = card.querySelector('.card-text').textContent.toLowerCase();
            
            if (title.includes(searchTerm) || description.includes(searchTerm)) {
                card.style.display = '';
                card.style.opacity = '1';
                hasResults = true;
            } else {
                card.style.display = 'none';
                card.style.opacity = '0';
            }
        });

        // Show/hide no results message
        let noResultsMsg = document.querySelector('.no-results-message');
        if (!hasResults && searchTerm !== '') {
            if (!noResultsMsg) {
                noResultsMsg = document.createElement('div');
                // noResultsMsg.className = 'no-results-message alert alert-info mt-3';
                noResultsMsg.textContent = 'No effects found matching your search.';
                searchInput.parentNode.appendChild(noResultsMsg);
            }
        } else if (noResultsMsg) {
            noResultsMsg.remove();
        }
    }

    if (searchInput && searchButton) {
        searchButton.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        searchInput.addEventListener('input', () => {
            if (searchInput.value.trim() === '') {
                effectCards.forEach(card => {
                    card.style.display = '';
                    card.style.opacity = '1';
                });
                const noResultsMsg = document.querySelector('.no-results-message');
                if (noResultsMsg) {
                    noResultsMsg.remove();
                }
            }
        });
    }

    // Handle theme toggle animation
    const themeToggle = document.querySelector('.theme-toggle button');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const icon = this.querySelector('i');
            icon.style.transform = 'rotate(360deg)';
            setTimeout(() => {
                icon.style.transform = '';
            }, 500);
        });
    }

    // Handle card hover effects
    effectCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (this.style.display !== 'none') {
                this.style.transform = 'translateY(-5px)';
            }
        });

        card.addEventListener('mouseleave', function() {
            if (this.style.display !== 'none') {
                this.style.transform = '';
            }
        });
    });

    // Initialize all cards as visible
    effectCards.forEach(card => {
        card.style.display = '';
        card.style.opacity = '1';
    });
}); 