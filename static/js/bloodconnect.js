/**
 * BloodConnect - Main JavaScript
 * Handles map initialization, form interactions, and animations
 */

'use strict';

// ---- Auto-dismiss alerts ----
document.addEventListener('DOMContentLoaded', function () {
    // Auto close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.stat-card, .how-card, .request-card, .donor-card, .hospital-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // When animated class is added, show element
    const style = document.createElement('style');
    style.textContent = '.animated { opacity: 1 !important; transform: translateY(0) !important; }';
    document.head.appendChild(style);

    // Form enhancements
    enhanceForms();

    // Role card selection in registration
    handleRoleSelection();

    // Geolocation for forms
    setupGeolocation();
});

// ---- Form enhancements ----
function enhanceForms() {
    // Add floating label effect
    const inputs = document.querySelectorAll('.form-control, .form-select');
    inputs.forEach(input => {
        if (input.value) input.classList.add('has-value');
        input.addEventListener('change', function () {
            this.classList.toggle('has-value', this.value !== '');
        });
    });
}

// ---- Role Selection ----
function handleRoleSelection() {
    const roleInputs = document.querySelectorAll('input[name="role"]');
    if (!roleInputs.length) return;

    // Check initially if a role is pre-selected
    roleInputs.forEach(input => {
        if (input.checked) {
            input.closest('.role-card')?.classList.add('selected');
        }
        input.addEventListener('change', function () {
            roleInputs.forEach(r => r.closest('.role-card')?.classList.remove('selected'));
            if (this.checked) this.closest('.role-card')?.classList.add('selected');
        });
    });
}

// ---- Geolocation for location fields ----
function setupGeolocation() {
    const geoBtn = document.getElementById('get-location-btn');
    if (!geoBtn) return;

    geoBtn.addEventListener('click', function () {
        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser.');
            return;
        }
        this.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Getting location...';
        this.disabled = true;

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude.toFixed(6);
                const lng = pos.coords.longitude.toFixed(6);

                const latField = document.querySelector('input[name="latitude"]');
                const lngField = document.querySelector('input[name="longitude"]');

                if (latField) latField.value = lat;
                if (lngField) lngField.value = lng;

                this.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Location Set';
                this.classList.replace('btn-outline-blood', 'btn-success');
            },
            () => {
                this.innerHTML = '<i class="bi bi-geo-alt me-1"></i>Get My Location';
                this.disabled = false;
                alert('Unable to get your location. Please enter it manually.');
            }
        );
    });
}

// ---- Blood Request Map Helper ----
function initRequestsMap(containerId, requests) {
    if (!document.getElementById(containerId)) return;

    const map = L.map(containerId).setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    const requestIcon = L.divIcon({
        html: '<div class="map-marker" style="background:var(--blood-red)"><i class="bi bi-droplet-fill"></i></div>',
        className: '',
        iconSize: [36, 36],
        iconAnchor: [18, 36],
        popupAnchor: [0, -36]
    });

    requests.forEach(req => {
        if (req.latitude && req.longitude) {
            L.marker([req.latitude, req.longitude], { icon: requestIcon })
                .addTo(map)
                .bindPopup(`
                    <div class="map-popup">
                        <strong>${req.blood_group}${req.rh_factor} needed</strong><br>
                        <small>${req.hospital_name}</small><br>
                        <small>${req.city || ''}</small>
                    </div>
                `);
        }
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            map.setView([pos.coords.latitude, pos.coords.longitude], 11);
        });
    }

    return map;
}

// ---- Confirm dialogs ----
document.addEventListener('click', function (e) {
    const confirmBtn = e.target.closest('[data-confirm]');
    if (confirmBtn) {
        const msg = confirmBtn.getAttribute('data-confirm');
        if (!confirm(msg)) e.preventDefault();
    }
});

// ---- Number animation ----
function animateNumber(el, target, duration = 1500) {
    const start = 0;
    const step = (timestamp) => {
        const progress = Math.min((timestamp - startTime) / duration, 1);
        el.textContent = Math.floor(progress * target);
        if (progress < 1) requestAnimationFrame(step);
    };
    let startTime;
    requestAnimationFrame((timestamp) => {
        startTime = timestamp;
        requestAnimationFrame(step);
    });
}

// Animate stat numbers when visible
const statNums = document.querySelectorAll('.stat-number');
const statObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target;
            const text = el.textContent;
            const num = parseInt(text.replace(/\D/g, ''));
            if (num > 0) {
                const suffix = text.replace(/[0-9]/g, '').trim();
                animateNumber(el, num);
                if (suffix) {
                    setTimeout(() => { el.textContent += suffix; }, 1600);
                }
            }
            statObserver.unobserve(el);
        }
    });
}, { threshold: 0.5 });

statNums.forEach(el => statObserver.observe(el));
