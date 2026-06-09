function copyBibTeX() {
  var bibTexElement = document.querySelector(".bibtex-section pre code");
  var bibTexText = bibTexElement.innerText.trim();
  navigator.clipboard.writeText(bibTexText).then(function () {
    var btn = document.querySelector(".bibtex-copy-button");
    var original = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(function () {
      btn.textContent = original;
    }, 1500);
  });
}

function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  document.querySelector(".nav").classList.toggle("dark-mode");
}

window.onscroll = function () {
  const scrollUpBtn = document.getElementById("scrollUpBtn");
  if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
    scrollUpBtn.style.display = "block";
  } else {
    scrollUpBtn.style.display = "none";
  }
};

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

class Carousel {
  constructor(element, interval = 4000) {
    this.container = element;
    this.track = element.querySelector(".carousel-track");
    this.slides = Array.from(element.querySelectorAll(".carousel-slide"));
    this.indicators = element.querySelector(".carousel-indicators");

    this.currentIndex = 0;
    this.slidesPerView = window.innerWidth <= 768 ? 1 : 3;
    this.totalSlides = Math.ceil(this.slides.length / this.slidesPerView);
    this.interval = interval;
    this.autoPlayTimer = null;

    this.createIndicators();
    this.setupEventListeners();
    if (this.totalSlides > 1) this.startAutoPlay();
    this.updateCarousel();
  }

  createIndicators() {
    this.indicators.innerHTML = "";
    for (let i = 0; i < this.totalSlides; i++) {
      const button = document.createElement("button");
      button.classList.add("indicator");
      if (i === 0) button.classList.add("active");
      button.addEventListener("click", () => this.goToSlide(i));
      this.indicators.appendChild(button);
    }
  }

  setupEventListeners() {
    this.container.querySelector(".prev").addEventListener("click", (e) => {
      e.preventDefault();
      this.prevSlide();
    });
    this.container.querySelector(".next").addEventListener("click", (e) => {
      e.preventDefault();
      this.nextSlide();
    });
    this.container.addEventListener("mouseenter", () => this.stopAutoPlay());
    this.container.addEventListener("mouseleave", () => {
      if (this.totalSlides > 1) this.startAutoPlay();
    });
  }

  updateCarousel() {
    const offset = -this.currentIndex * (100 / this.slidesPerView) * this.slidesPerView;
    this.track.style.transform = `translateX(${offset}%)`;
    Array.from(this.indicators.children).forEach((indicator, index) => {
      indicator.classList.toggle("active", index === this.currentIndex);
    });
  }

  nextSlide() {
    this.currentIndex = (this.currentIndex + 1) % this.totalSlides;
    this.updateCarousel();
    this.resetAutoPlay();
  }

  prevSlide() {
    this.currentIndex = (this.currentIndex - 1 + this.totalSlides) % this.totalSlides;
    this.updateCarousel();
    this.resetAutoPlay();
  }

  goToSlide(index) {
    if (index !== this.currentIndex) {
      this.currentIndex = index;
      this.updateCarousel();
      this.resetAutoPlay();
    }
  }

  startAutoPlay() {
    if (this.autoPlayTimer) clearInterval(this.autoPlayTimer);
    this.autoPlayTimer = setInterval(() => this.nextSlide(), this.interval);
  }

  stopAutoPlay() {
    if (this.autoPlayTimer) {
      clearInterval(this.autoPlayTimer);
      this.autoPlayTimer = null;
    }
  }

  resetAutoPlay() {
    this.stopAutoPlay();
    if (this.totalSlides > 1) this.startAutoPlay();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".carousel-container").forEach((el) => {
    let carousel = new Carousel(el, 4000);
    let touchStartX = 0;
    el.addEventListener(
      "touchstart",
      (e) => (touchStartX = e.changedTouches[0].screenX),
      { passive: true }
    );
    el.addEventListener(
      "touchend",
      (e) => {
        const diff = touchStartX - e.changedTouches[0].screenX;
        if (Math.abs(diff) > 50) diff > 0 ? carousel.nextSlide() : carousel.prevSlide();
      },
      { passive: true }
    );
  });
});
