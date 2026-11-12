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
    const modeloCartao = document.getElementById('mapa-cartao-local');

function criarCartao(predio, locais) {
    const cartao = modeloCartao.content.firstElementChild.cloneNode(true);
    const titulo = cartao.querySelector('[data-nome]');
    const tipo = cartao.querySelector('[data-tipo]');
    const andar = cartao.querySelector('[data-andar]');

    cartao.querySelector('[data-predio]').textContent = predio.nome;

    function mostrarLocal(local) {
        titulo.textContent = local.nome;
        tipo.textContent = local.tipo;
        andar.textContent = local.andar || '—';
    }

    if (locais.length > 1) {
        const seletor = cartao.querySelector('select');

        locais.forEach((local, indice) => {
            const descricao = local.andar
                ? `${local.nome} — ${local.andar}`
                : local.nome;
            seletor.add(new Option(descricao, indice));
        });

        seletor.closest('label').hidden = false;
        seletor.addEventListener('change', () => {
            mostrarLocal(locais[seletor.selectedIndex]);
        });
    }

    mostrarLocal(locais[0]);
    return cartao;
}
   const siglas = {
    predio: 'PR',
    banheiro: 'WC',
    auditorio: 'AU',
    sala: 'SA',
    laboratorio: 'LB',
    biblioteca: 'BI',
    restaurante: 'RE',
    entrada: 'EN',
    elevador: 'EL',
    escada: 'ES',
    outro: '•',
};

for (const predio of predios) {
    const locaisDoPredio = [
        {nome: `${predio.sigla} — ${predio.nome}`, tipo: 'Prédio'},
        ...(predio.locais ?? []),
    ];

    const locaisPorTipo = new Map();

    for (const local of locaisDoPredio) {
        const chave = local.tipo
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim()
            .toLowerCase()
            .split(/\s+/)[0];

        const tipo = Object.hasOwn(siglas, chave) ? chave : 'outro';

        if (!locaisPorTipo.has(tipo)) {
            locaisPorTipo.set(tipo, []);
        }
        locaisPorTipo.get(tipo).push(local);
    }

    const categorias = Array.from(locaisPorTipo.entries());

    categorias.forEach(([tipo, locais], indice) => {
        const coluna = indice % 3;
        const linha = Math.floor(indice / 3);
        const colunasNaLinha = Math.min(3, categorias.length - linha * 3);
        const x = (coluna - (colunasNaLinha - 1) / 2) * 36;
        const y = linha * 38;

        const icone = L.divIcon({
            className: `mapa-marcador mapa-marcador--${tipo}`,
            html: `<span class="mapa-pin" aria-hidden="true"><span>${siglas[tipo]}</span></span>`,
            iconSize: [30, 36],
            iconAnchor: [15 - x, 36 - y],
            popupAnchor: [x, y - 32],
        });

        const nome = locais.length === 1
            ? locais[0].nome
            : `${locais[0].tipo} — ${predio.nome}`;

            const marcador = L.marker([predio.latitude, predio.longitude], {
        icon: icone,
        title: nome,
    })
        .bindPopup(() => criarCartao(predio, locais), {maxWidth: 270})
        .addTo(mapa);

    const pin = marcador.getElement();
    pin.setAttribute('aria-label', nome);
    pin.setAttribute('aria-expanded', 'false');

marcador.on('popupopen popupclose', (evento) => {
    const ativo = evento.type === 'popupopen';
    pin.classList.toggle('mapa-marcador--ativo', ativo);
    pin.setAttribute('aria-expanded', String(ativo));
    marcador.setZIndexOffset(ativo ? 1000 : 0);
    });
});
}

    document.getElementById('mapa-estatico').hidden = true;
})();