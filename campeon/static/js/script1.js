/**
 * Campeón Sports - Core JS
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Campeón Sports ready.');

    // Search bar interaction
    const searchInput = document.querySelector('input[placeholder="Search products..."]');
    if (searchInput) {
        searchInput.addEventListener('focus', () => {
            searchInput.classList.add('w-64');
            searchInput.classList.remove('w-48');
        });
        searchInput.addEventListener('blur', () => {
            searchInput.classList.remove('w-64');
            searchInput.classList.add('w-48');
        });
    }

    // Load More functionality (mock)
    const loadMoreBtn = document.querySelector('button:contains("Load More")');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', () => {
            loadMoreBtn.textContent = 'Loading...';
            setTimeout(() => {
                loadMoreBtn.textContent = 'No more products';
                loadMoreBtn.disabled = true;
            }, 1500);
        });
    }

    // Sticky Header effect on scroll
    const header = document.querySelector('header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            header.classList.add('shadow-sm');
        } else {
            header.classList.remove('shadow-sm');
        }
    });
});

// Helper for selecting elements by text (like jQuery :contains)
// (Since querySelector doesn't support :contains)
document.querySelectorAll('button').forEach(btn => {
    if (btn.textContent.includes('Load More')) {
        btn.addEventListener('click', () => {
            btn.textContent = 'Loading...';
            setTimeout(() => {
                btn.textContent = 'No more products';
                btn.classList.add('opacity-50', 'cursor-not-allowed');
            }, 1500);
        });
    }
});
