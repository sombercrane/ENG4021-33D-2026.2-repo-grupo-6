(() => {
    const elemento = document.getElementById('mapa-interativo');
    if (!elemento || !window.L) return;

    elemento.hidden = false;
    const mapa = L.map(elemento).setView([-22.9793, -43.23245], 17);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        referrerPolicy: 'strict-origin-when-cross-origin',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapa);

    const predios = JSON.parse(document.getElementById('mapa-dados').textContent);

    for (const predio of predios) {
        const nome = `${predio.sigla} — ${predio.nome}`;
        const conteudo = document.createElement('span');
        conteudo.textContent = nome;

        L.marker([predio.latitude, predio.longitude], {title: nome, alt: nome})
            .bindPopup(conteudo)
            .addTo(mapa);
    }

    document.getElementById('mapa-estatico').hidden = true;
})();