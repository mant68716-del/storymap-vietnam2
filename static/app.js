
const cfg = window.STORYMAP || {};

const map = L.map('map', {
    scrollWheelZoom: true,
    zoomControl: true
}).setView([16.2, 107.8], 5.4);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap'
}).addTo(map);

const visited = new Set(cfg.visited || []);
const storyLinks = cfg.storyLinks || {};
const markers = {};

(cfg.provinces || []).forEach(([code, name]) => {
    const center = cfg.centers[name];
    if (!center) return;

    const done = visited.has(code);
    const stories = storyLinks[code] || [];

    const icon = L.divIcon({
        className: 'province-pin-wrap',
        html: `<div class="province-pin ${done ? 'done' : ''}">
            ${done ? '✓' : '+'}
        </div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
    });

    const marker = L.marker(center, { icon }).addTo(map);
    markers[code] = marker;

    // Nếu tỉnh có Story, hiện các liên kết xem Story đã lưu.
    const viewLinks = stories.map(story =>
        `<a href="/story/${story.id}">📖 ${escapeHtml(story.title)}</a>`
    ).join('');

    const popupContent = `
        <div class="popup">
            <b>${escapeHtml(name)}</b>
            <span>${stories.length
                ? `📚 Có ${stories.length} kỷ niệm đã lưu`
                : 'Chưa có kỷ niệm'}</span>
            ${viewLinks}
            <a href="/story/new/${encodeURIComponent(code)}">
                ＋ Lưu kỷ niệm
            </a>
        </div>
    `;

    marker.bindPopup(popupContent);
});

// Hiện tên tỉnh an toàn trong popup.
function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[char]);
}

// Bấm vào tên tỉnh trong danh sách cũng mở popup trên bản đồ.
document.querySelectorAll('.province-chip').forEach(chip => {
    chip.addEventListener('click', event => {
        const code = chip.dataset.code;
        if (!markers[code]) return;

        event.preventDefault();
        markers[code].openPopup();
        map.panTo(markers[code].getLatLng());
    });
});

const islandData = [
    ['Hoàng Sa', 16.5, 111.75],
    ['Trường Sa', 10.5, 114],
    ['Phú Quốc', 10.23, 103.97],
    ['Côn Đảo', 8.68, 106.6],
    ['Cát Bà', 20.73, 107.05]
];

islandData.forEach(([name, lat, lon]) => {
    L.circleMarker([lat, lon], {
        radius: 6,
        color: '#0b63ce',
        fillColor: '#22a06b',
        fillOpacity: 0.85
    }).addTo(map).bindTooltip(`🏝️ ${name}`);
});

const search = document.getElementById('search');

if (search) {
    search.addEventListener('input', event => {
        const query = event.target.value.toLowerCase();

        document.querySelectorAll('.province-chip').forEach(chip => {
            chip.style.display =
                chip.dataset.name.includes(query) ? 'inline-flex' : 'none';
        });
    });
}
