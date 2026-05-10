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