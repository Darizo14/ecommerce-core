let currentSlide = 0;
const slides = document.querySelectorAll('.hero-carousel__slide');
const dots = document.querySelectorAll('.hero-carousel__dot');
const totalSlides = slides.length;

function updateSlide() {
    document.getElementById('heroSlides').style.transform = `translateX(-${currentSlide * 100}%)`;
    dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === currentSlide);
    });
}

function moveSlide(direction) {
    currentSlide = (currentSlide + direction + totalSlides) % totalSlides;
    updateSlide();
}

function goToSlide(index) {
    currentSlide = index;
    updateSlide();
}

setInterval(() => moveSlide(1), 5000);

// Product Carousel
document.addEventListener('DOMContentLoaded', function() {
    const carousels = document.querySelectorAll('.product-carousel__track');
    
    carousels.forEach(track => {
        const carouselName = track.dataset.carousel;
        const cards = track.querySelectorAll('.dawn-card');
        const totalCards = cards.length;
        
        let currentIndex = 0;
        let visibleCards = getVisibleCards();
        
        const prevBtn = document.querySelector(`.section-arrow--prev[data-carousel="${carouselName}"]`);
        const nextBtn = document.querySelector(`.section-arrow--next[data-carousel="${carouselName}"]`);
        
        function getVisibleCards() {
            const width = window.innerWidth;
            if (width >= 1200) return 4;
            if (width >= 768) return 3;
            return 2;
        }
        
        function updateCarousel() {
            const cardWidth = cards[0].offsetWidth;
            const gap = parseFloat(getComputedStyle(track).gap) || 24;
            const translateX = currentIndex * -(cardWidth + gap);
            track.style.transform = `translateX(${translateX}px)`;
            
            // Update buttons (always visible, just disabled)
            if (prevBtn) {
                prevBtn.disabled = currentIndex === 0;
            }
            if (nextBtn) {
                nextBtn.disabled = currentIndex >= totalCards - visibleCards;
            }
        }
        
        // Initial setup
        visibleCards = getVisibleCards();
        
        if (currentIndex >= totalCards - visibleCards) {
            currentIndex = Math.max(0, totalCards - visibleCards);
        }
        updateCarousel();
        
        // Window resize
        window.addEventListener('resize', () => {
            visibleCards = getVisibleCards();
            
            if (currentIndex >= totalCards - visibleCards) {
                currentIndex = Math.max(0, totalCards - visibleCards);
            }
            updateCarousel();
        });
        
        // Button handlers
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentIndex > 0) {
                    currentIndex--;
                    updateCarousel();
                }
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (currentIndex < totalCards - visibleCards) {
                    currentIndex++;
                    updateCarousel();
                }
            });
        }
    });
});