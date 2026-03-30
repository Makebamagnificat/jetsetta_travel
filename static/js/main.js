// static/js/main.js

let mapInstance = null;

// Initialize Map
function initMap(lat = 36.3932, lng = 25.4617) {
    if (mapInstance) mapInstance.remove();
    
    mapInstance = L.map('map').setView([lat, lng], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap • Jetsetta'
    }).addTo(mapInstance);
}

// Fly to location from itinerary
function flyTo(lat, lng) {
    if (mapInstance) {
        mapInstance.flyTo([lat, lng], 15, { duration: 2 });
        L.marker([lat, lng]).addTo(mapInstance)
            .bindPopup("Activity Location").openPopup();
    }
}

// OpenWeatherMap API Call
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
        // Fallback
        tempEl.textContent = "27°";
        iconEl.textContent = "⛅";
    }
}

// Pay Now Function (used in bookings.html)
async function payNow(bookingId) {
    try {
        const res = await fetch('/create-checkout-session', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({booking_id: bookingId})
        });
        
        const data = await res.json();
        if (data.url) {
            window.location.href = data.url;
        } else {
            alert(data.error || "Payment failed");
        }
    } catch (err) {
        alert("Error processing payment");
    }
}

// Auto initialize on every page load
document.addEventListener('DOMContentLoaded', () => {
    getWeather("Accra");   // Change city if needed
    
    // Initialize map if element exists
    const mapElement = document.getElementById('map');
    if (mapElement) {
        initMap();
    }
});