const cfg=window.STORYMAP||{};
const map=L.map('map',{scrollWheelZoom:true,zoomControl:true}).setView([16.2,107.8],5.4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'© OpenStreetMap'}).addTo(map);
const visited=new Set(cfg.visited||[]);
(cfg.provinces||[]).forEach(([code,name])=>{
 const c=cfg.centers[name]; if(!c)return;
 const done=visited.has(code);
 const icon=L.divIcon({className:'province-pin-wrap',html:`<div class="province-pin ${done?'done':''}">${done?'✓':'+'}</div>`,iconSize:[28,28],iconAnchor:[14,14]});
 const marker=L.marker(c,{icon}).addTo(map);
 marker.bindPopup(`<div class="popup"><b>${name}</b><span>${done?'✓ Đã đi':'Chưa đi'}</span><a href="/story/new/${code}">＋ Lưu Story tại đây</a></div>`);
});
const islandData=[['Hoàng Sa',16.5,111.75],['Trường Sa',10.5,114],['Phú Quốc',10.23,103.97],['Côn Đảo',8.68,106.6],['Cát Bà',20.73,107.05]];
islandData.forEach(([n,lat,lon])=>L.circleMarker([lat,lon],{radius:6,color:'#0b63ce',fillColor:'#22a06b',fillOpacity:.85}).addTo(map).bindTooltip(`🏝️ ${n}`));
const search=document.getElementById('search');
if(search)search.addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('.province-chip').forEach(x=>x.style.display=x.dataset.name.includes(q)?'inline-flex':'none')});
