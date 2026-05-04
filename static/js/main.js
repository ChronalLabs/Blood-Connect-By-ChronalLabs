/**
 * BloodConnect — Main JavaScript
 * Navbar, animations, helpers
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Navbar scroll behavior ──
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                navbar.style.background = 'rgba(15,17,23,0.98)';
            } else {
                navbar.style.background = 'rgba(15,17,23,0.9)';
            }
        });
    }

    // ── Mobile hamburger menu ──
    const hamburger = document.getElementById('navHamburger');
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            const links = document.querySelector('.nav-links');
            const actions = document.querySelector('.nav-actions');
            if (links) links.classList.toggle('open');
            if (actions) actions.classList.toggle('open');
        });
    }

    // ── Auto-dismiss flash messages ──
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100%)';
            msg.style.transition = 'all 0.4s ease';
            setTimeout(() => msg.remove(), 400);
        }, 4000);
    });

    // ── Animate on scroll ──
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.step-card, .hospital-card, .stat-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // ── Confirm dialogs ──
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // ── Location detection for donor/seeker forms ──
    const latInput = document.querySelector('input[name="latitude"]');
    const lngInput = document.querySelector('input[name="longitude"]');

    if (latInput && lngInput && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            pos => {
                latInput.value = pos.coords.latitude.toFixed(6);
                lngInput.value = pos.coords.longitude.toFixed(6);
            },
            err => console.log('Location not available:', err.message)
        );
    }

    // ── Blood group display helper ──
    window.getBloodGroupClass = function (bg) {
        const negatives = ['A-', 'B-', 'O-', 'AB-'];
        return negatives.includes(bg) ? 'negative' : 'positive';
    };

    // ── Form validation hints ──
    const phoneInputs = document.querySelectorAll('input[name="phone_number"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 10);
            if (this.value.length === 10) {
                this.style.borderColor = 'var(--success)';
            } else {
                this.style.borderColor = '';
            }
        });
    });

    const aadharInputs = document.querySelectorAll('input[name="aadhar_card_number"]');
    aadharInputs.forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 12);
        });
    });

    console.log('BloodConnect initialized ✓');
});


/**
 * Leaflet map helper — init a standard map
 */
window.initMap = function (elementId, lat = 20.5937, lng = 78.9629, zoom = 5) {
    const map = L.map(elementId).setView([lat, lng], zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
    }).addTo(map);

    // Try to center on user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            map.setView([pos.coords.latitude, pos.coords.longitude], 12);

            L.circleMarker([pos.coords.latitude, pos.coords.longitude], {
                radius: 8,
                color: '#d62828',
                fillColor: '#d62828',
                fillOpacity: 0.7,
                weight: 2
            }).addTo(map).bindPopup('<strong>Your Location</strong>');
        });
    }

    return map;
};


/**
 * Create hospital marker icon
 */
window.createHospitalIcon = function () {
    return L.divIcon({
        html: '<div class="map-pin hospital-pin"><i class="fas fa-hospital"></i></div>',
        className: '',
        iconSize: [36, 36],
        iconAnchor: [18, 36],
        popupAnchor: [0, -36],
    });
};


/**
 * Create donor marker icon
 */
window.createDonorIcon = function () {
    return L.divIcon({
        html: '<div class="map-pin donor-pin"><i class="fas fa-tint"></i></div>',
        className: '',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32],
    });
};
