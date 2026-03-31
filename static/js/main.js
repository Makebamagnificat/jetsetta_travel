// static/js/main.js

let mapInstance = null;

// Initialize Map
function initMap(lat = 36.3932, lng = 25.4617) {
    if (mapInstance) {
        mapInstance.remove();
    }

    mapInstance = L.map('map').setView([lat, lng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap • Jetsetta'
    }).addTo(mapInstance);
}

// Fly to location
function flyTo(lat, lng) {
    if (mapInstance) {
        mapInstance.flyTo([lat, lng], 15, { duration: 2 });

        L.marker([lat, lng])
            .addTo(mapInstance)
            .bindPopup("Activity Location")
            .openPopup();
    }
}

// Weather
async function getWeather(city = "Accra") {
    const tempEl = document.getElementById('weather-temp');
    const iconEl = document.getElementById('weather-icon');
    const cityEl = document.getElementById('weather-city');

    if (!tempEl) return;

    try {
        const response = await fetch(`/api/weather?city=${city}`);
        const data = await response.json();

        tempEl.textContent = data.temp + "°";
        iconEl.textContent = data.icon;
        if (cityEl) cityEl.textContent = data.city;

    } catch (e) {
        tempEl.textContent = "27°";
        iconEl.textContent = "⛅";
    }
}

// Payment
async function payNow(bookingId) {
    try {
        const res = await fetch('/create-checkout-session', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ booking_id: bookingId })
        });

        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        const stripe = Stripe("YOUR_PUBLIC_KEY"); // replace this

        stripe.redirectToCheckout({
            sessionId: data.id
        });

    } catch (err) {
        alert("Error processing payment");
    }
}

// Auto initialize
document.addEventListener('DOMContentLoaded', () => {
    getWeather("Accra");

    const mapElement = document.getElementById('map');
    if (mapElement) {
        initMap();
    }
});