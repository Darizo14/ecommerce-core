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

// Hero Carousel drag/swipe (mobile only)
(function() {
    const heroSlides = document.getElementById('heroSlides');
    if (!heroSlides || totalSlides <= 0) return;
    
    let dragState = null;
    
    function isMobile() {
        return window.innerWidth <= 768;
    }
    
    function getClientX(e) {
        return e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
    }
    
    function getCurrentPct() {
        const elW = heroSlides.offsetWidth;
        if (!elW) return -(currentSlide * 100);
        const s = window.getComputedStyle(heroSlides).transform;
        return (new DOMMatrixReadOnly(s).m41 / elW) * 100 || 0;
    }
    
    function onDragStart(e) {
        if (!isMobile() || dragState) return;
        if (e.type === 'mousedown' && heroSlides.dataset.touchEnded) return;
        dragState = { startX: getClientX(e), basePct: getCurrentPct() };
        heroSlides.classList.add('hero-carousel__slides--dragging');
        if (e.type === 'mousedown') {
            document.addEventListener('mousemove', onDragMove);
            document.addEventListener('mouseup', onDragEnd);
        }
    }
    
    function onDragMove(e) {
        if (!dragState) return;
        const deltaPct = ((getClientX(e) - dragState.startX) / heroSlides.offsetWidth) * 100;
        heroSlides.style.transform = `translateX(${dragState.basePct + deltaPct}%)`;
    }
    
    function onDragEnd(e) {
        if (!dragState) return;
        const delta = e.type === 'touchend'
            ? e.changedTouches[0].clientX - dragState.startX
            : e.clientX - dragState.startX;
        const containerWidth = heroSlides.parentElement.offsetWidth;
        
        if (Math.abs(delta) > containerWidth * 0.1) {
            if (delta < 0 && currentSlide < totalSlides - 1) currentSlide++;
            else if (delta > 0 && currentSlide > 0) currentSlide--;
        }
        
        heroSlides.classList.remove('hero-carousel__slides--dragging');
        updateSlide();
        
        if (e.type === 'touchend') {
            heroSlides.dataset.touchEnded = '1';
            setTimeout(() => delete heroSlides.dataset.touchEnded, 300);
        } else {
            document.removeEventListener('mousemove', onDragMove);
            document.removeEventListener('mouseup', onDragEnd);
        }
        dragState = null;
    }
    
    function onTouchCancel() {
        if (dragState) {
            heroSlides.classList.remove('hero-carousel__slides--dragging');
            updateSlide();
            dragState = null;
        }
    }
    
    heroSlides.addEventListener('touchstart', onDragStart, { passive: true });
    heroSlides.addEventListener('touchmove', onDragMove, { passive: true });
    heroSlides.addEventListener('touchend', onDragEnd);
    heroSlides.addEventListener('touchcancel', onTouchCancel);
    heroSlides.addEventListener('mousedown', onDragStart);
})();

// Product Carousel — free scroll
document.addEventListener('DOMContentLoaded', function() {
    const carousels = document.querySelectorAll('.product-carousel__track');
    
    carousels.forEach(track => {
        // Mobile: let CSS Scroll Snap handle natively
        if (window.innerWidth <= 480) {
            track.style.transform = 'none';
            return;
        }

        const carouselName = track.dataset.carousel;
        const carousel = track.closest('.product-carousel');
        const prevBtn = document.querySelector(`.section-arrow--prev[data-carousel="${carouselName}"]`);
        const nextBtn = document.querySelector(`.section-arrow--next[data-carousel="${carouselName}"]`);
        
        let offsetX = 0;
        
        function getMaxOffset() {
            const overflow = track.scrollWidth - carousel.offsetWidth;
            return Math.max(0, overflow);
        }
        
        function applyPos() {
            track.style.transform = `translateX(${offsetX}px)`;
        }
        
        function clamp() {
            const max = getMaxOffset();
            if (offsetX > 0) { offsetX = 0; return true; }
            if (offsetX < -max) { offsetX = -max; return true; }
            return false;
        }
        
        function updateButtons() {
            const max = getMaxOffset();
            if (prevBtn) prevBtn.disabled = offsetX >= -1;
            if (nextBtn) nextBtn.disabled = offsetX <= -max + 1;
        }
        
        function snap() {
            const bounced = clamp();
            applyPos();
            updateButtons();
        }
        
        // Initial setup
        track.style.transition = 'none';
        snap();
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                track.style.transition = '';
            });
        });
        
        // Resize
        window.addEventListener('resize', () => {
            snap();
        });
        
        // Arrow buttons
        const scrollAmount = () => Math.min(carousel.offsetWidth * 0.8, 400);
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                offsetX += scrollAmount();
                snap();
            });
        }
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                offsetX -= scrollAmount();
                snap();
            });
        }
        
        // --- Free drag / swipe ---
        let dragState = null;
        
        function getClientX(e) {
            return e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
        }
        
        function getCurrentX() {
            const s = window.getComputedStyle(track).transform;
            return new DOMMatrixReadOnly(s).m41 || 0;
        }
        
        function onDragStart(e) {
            if (dragState || e.type === 'mousedown' && track.dataset.touchEnded) return;
            dragState = { startX: getClientX(e), baseX: getCurrentX() };
            track.classList.add('product-carousel__track--dragging');
            if (e.type === 'mousedown') {
                document.addEventListener('mousemove', onDragMove);
                document.addEventListener('mouseup', onDragEnd);
            }
        }
        
        function onDragMove(e) {
            if (!dragState) return;
            const delta = getClientX(e) - dragState.startX;
            offsetX = dragState.baseX + delta;
            track.style.transform = `translateX(${offsetX}px)`;
        }
        
        function onDragEnd(e) {
            if (!dragState) return;
            track.classList.remove('product-carousel__track--dragging');
            snap();
            if (e.type === 'touchend') {
                track.dataset.touchEnded = '1';
                setTimeout(() => delete track.dataset.touchEnded, 300);
            } else {
                document.removeEventListener('mousemove', onDragMove);
                document.removeEventListener('mouseup', onDragEnd);
            }
            dragState = null;
        }
        
        function onTouchCancel() {
            if (dragState) {
                track.classList.remove('product-carousel__track--dragging');
                snap();
                dragState = null;
            }
        }
        
        track.addEventListener('touchstart', onDragStart, { passive: true });
        track.addEventListener('touchmove', onDragMove, { passive: true });
        track.addEventListener('touchend', onDragEnd);
        track.addEventListener('touchcancel', onTouchCancel);
        track.addEventListener('mousedown', onDragStart);
    });
    
    // --- Mobile: tap overlay toggle ---
    if (window.innerWidth <= 768) {
        document.querySelectorAll('.dawn-card__overlay').forEach(overlay => {
            overlay.addEventListener('click', function(e) {
                if (e.target.closest('.dawn-card__overlay-actions')) return;
                this.classList.toggle('dawn-card__overlay--visible');
            });
        });
    }
});
