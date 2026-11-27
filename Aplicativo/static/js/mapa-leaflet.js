
(() => {
    const elemento = document.getElementById('mapa-interativo');
    if (!elemento || !window.L) return;

    elemento.hidden = false;

    const mapa = L.map(elemento).setView(
        [-22.9793, -43.23245],
        17
    );

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        referrerPolicy: 'strict-origin-when-cross-origin',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapa);

    const predios = JSON.parse(
        document.getElementById('mapa-dados').textContent
    );

    const modeloCartao = document.getElementById(
        'mapa-cartao-local'
    );

    function criarCartao(predio) {
        const cartao = modeloCartao.content
            .firstElementChild.cloneNode(true);

        const titulo = cartao.querySelector('[data-nome]');
        const tipo = cartao.querySelector('[data-tipo]');
        const andar = cartao.querySelector('[data-andar]');
        const seletor = cartao.querySelector('select');

        cartao.querySelector('[data-predio]').textContent =
            predio.nome;

        cartao.querySelector('[data-ver-predio]').href =
            predio.url;

        const locais = predio.locais ?? [];

        function mostrarLocal(local) {
            titulo.textContent = local.nome;
            tipo.textContent = local.tipo || '—';
            andar.textContent = local.andar || '—';
        }

        if (locais.length > 0) {
            locais.forEach((local, indice) => {
                const descricao = local.andar
                    ? `${local.nome} — ${local.andar}`
                    : local.nome;

                seletor.add(new Option(descricao, indice));
            });

            if (locais.length > 1) {
                seletor.closest('label').hidden = false;

                seletor.addEventListener('change', () => {
                    mostrarLocal(locais[seletor.selectedIndex]);
                });
            } else {
                seletor.closest('label').hidden = true;
            }

            mostrarLocal(locais[0]);
        } else {
            titulo.textContent = 'Nenhum espaço cadastrado';
            tipo.textContent = '—';
            andar.textContent = '—';
            seletor.closest('label').hidden = true;
        }

        return cartao;
    }

    for (const predio of predios) {
        const icone = L.divIcon({
            className: 'mapa-marcador mapa-marcador--predio',
            html: `
                <span class="mapa-pin" aria-hidden="true">
                    <span>PR</span>
                </span>
            `,
            iconSize: [30, 36],
            iconAnchor: [15, 36],
        });

        const marcador = L.marker(
            [predio.latitude, predio.longitude],
            {
                icon: icone,
                title: predio.nome,
            }
        )
            .bindPopup(
                () => criarCartao(predio),
                {maxWidth: 270}
            )
            .addTo(mapa);

        marcador.on('popupopen popupclose', (evento) => {
            const ativo = evento.type === 'popupopen';
            const pin = marcador.getElement();

            if (!pin) return;

            pin.classList.toggle(
                'mapa-marcador--ativo',
                ativo
            );

            marcador.setZIndexOffset(ativo ? 1000 : 0);
        });
    }

    document.getElementById('mapa-estatico').hidden = true;
})();
