document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const effectCards = document.querySelectorAll('.effect-card');
    let noResultsMessage = null;

    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        let hasResults = false;

        effectCards.forEach(card => {
            const description = card.querySelector('.card-text').textContent.toLowerCase();
            if (description.includes(searchTerm)) {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.5s ease-in-out';
                hasResults = true;
            } else {
                card.style.display = 'none';
            }
        });

        // Handle no results message
        if (!hasResults) {
            if (!noResultsMessage) {
                noResultsMessage = document.createElement('div');
                noResultsMessage.className = 'no-results-message';
                noResultsMessage.textContent = 'No effects found matching your search.';
                document.querySelector('.row').appendChild(noResultsMessage);
            }
            noResultsMessage.style.display = 'block';
        } else if (noResultsMessage) {
            noResultsMessage.style.display = 'none';
        }
    }

    if (searchButton) {
        searchButton.addEventListener('click', performSearch);
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });

        searchInput.addEventListener('input', function() {
            if (this.value === '') {
                effectCards.forEach(card => {
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.5s ease-in-out';
                });
                if (noResultsMessage) {
                    noResultsMessage.style.display = 'none';
                }
            }
        });
    }
}); 