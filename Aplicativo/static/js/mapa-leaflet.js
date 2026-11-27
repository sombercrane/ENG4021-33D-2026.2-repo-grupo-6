(() => {
    const filtro = document.getElementById('mapa-filtros');
    const campoBusca = document.getElementById('mapa-busca');
    const sugestoes = document.getElementById('mapa-sugestoes');
    const elemento = document.getElementById('mapa-interativo');
    const aviso = document.getElementById('localizacao-aviso');
    const entradas = document.getElementById('entrada-select');
    const botaoGps = document.getElementById('localizacao-botao');
    const formBanheiro = document.getElementById('banheiro-proximo');
    const resultadoBanheiro = document.getElementById('banheiro-resultado');
    const marcadores = new Map();
    let origem = null;
    let mapa = null;
    let marcadorOrigem = null;

    function atualizarFormulario(formulario) {
        formulario.hidden = !origem;
        formulario.elements.origem_latitude.value = origem?.latitude ?? '';
        formulario.elements.origem_longitude.value = origem?.longitude ?? '';
    }

    function definirOrigem(referencia, mensagem) {
        origem = referencia;
        aviso.textContent = mensagem;
        resultadoBanheiro.replaceChildren();
        formBanheiro.querySelector('button').disabled = !origem;
        elemento.querySelectorAll('[data-rota-externa]').forEach(atualizarFormulario);

        if (!mapa) return;
        if (marcadorOrigem) mapa.removeLayer(marcadorOrigem);
        marcadorOrigem = null;
        if (origem) {
            marcadorOrigem = L.circleMarker([origem.latitude, origem.longitude], {
                radius: 8,
                color: '#fff',
                fillColor: '#1675d0',
                fillOpacity: 1,
            }).addTo(mapa);
            if (mapa.getBounds().contains(marcadorOrigem.getLatLng())) {
                marcadorOrigem.bringToFront();
            }
        }
    }

    entradas.addEventListener('change', () => {
        if (!entradas.value) {
            definirOrigem(null, '');
            return;
        }
        const [latitude, longitude] = entradas.value.split(',').map(Number);
        definirOrigem({latitude, longitude}, 'Origem: ' + entradas.selectedOptions[0].text);
    });

    if (navigator.geolocation) {
        botaoGps.hidden = false;
        botaoGps.addEventListener('click', () => {
            botaoGps.disabled = true;
            aviso.textContent = 'Buscando sua localização…';
            navigator.geolocation.getCurrentPosition(
                ({coords}) => {
                    botaoGps.disabled = false;
                    entradas.value = '';
                    definirOrigem(
                        {latitude: coords.latitude, longitude: coords.longitude},
                        'Localização obtida. Precisão de cerca de ' + Math.round(coords.accuracy) + ' m.',
                    );
                },
                () => {
                    botaoGps.disabled = false;
                    aviso.textContent = 'Localização indisponível. Você pode escolher uma entrada.';
                },
                {enableHighAccuracy: true, timeout: 10000, maximumAge: 60000},
            );
        });
    }

    formBanheiro.hidden = false;
    formBanheiro.addEventListener('submit', async (evento) => {
        evento.preventDefault();
        if (!origem) return;
        const referencia = origem;
        const botao = formBanheiro.querySelector('button');
        const dados = new FormData(formBanheiro);
        dados.set('origem_latitude', referencia.latitude);
        dados.set('origem_longitude', referencia.longitude);
        botao.disabled = true;
        resultadoBanheiro.textContent = 'Buscando banheiros…';
        try {
            const resposta = await fetch(formBanheiro.action, {method: 'POST', body: dados});
            if (!resposta.ok) throw new Error('Falha na busca de banheiros');
            const resultado = await resposta.json();
            if (origem !== referencia) return;
            if (resultado.estado !== 'ok') {
                resultadoBanheiro.textContent = 'Nenhum banheiro cadastrado com localização no mapa.';
                return;
            }
            const resumo = document.createElement('p');
            resumo.textContent = resultado.predio + ' · ' + resultado.distancia_metros + ' m em linha reta até o prédio';
            const lista = document.createElement('ul');
            for (const local of resultado.locais) {
                const item = document.createElement('li');
                const link = document.createElement('a');
                link.href = local.url;
                link.textContent = local.nome + ' · ' + local.andar;
                item.append(link);
                lista.append(item);
            }
            resultadoBanheiro.replaceChildren(resumo, lista);
        } catch {
            if (origem === referencia) resultadoBanheiro.textContent = 'Não foi possível buscar banheiros agora.';
        } finally {
            botao.disabled = !origem;
        }
    });

    function focarLocal(id) {
        const grupo = marcadores.get(id);
        if (!grupo) return false;
        grupo.selecionado = id;
        grupo.marcador.setPopupContent(criarCartao(grupo)).openPopup();
        return true;
    }

    let buscaPendente;
    let consultaAtiva;
    let locaisSugeridos = [];
    campoBusca.setAttribute('list', 'mapa-sugestoes');
    campoBusca.addEventListener('input', () => {
        clearTimeout(buscaPendente);
        consultaAtiva?.abort();
        const termo = campoBusca.value.trim();
        const escolhidos = locaisSugeridos.filter((local) => local.nome === termo);
        if (escolhidos.length === 1) focarLocal(escolhidos[0].id);
        if (termo.length < 2) {
            locaisSugeridos = [];
            sugestoes.replaceChildren();
            return;
        }
        buscaPendente = setTimeout(async () => {
            const consulta = new AbortController();
            consultaAtiva = consulta;
            const url = new URL(filtro.dataset.sugestoesUrl, window.location.href);
            url.search = new URLSearchParams(new FormData(filtro));
            url.searchParams.set('q', termo);
            try {
                const resposta = await fetch(url, {signal: consulta.signal});
                if (!resposta.ok) return;
                const dados = await resposta.json();
                if (consulta.signal.aborted) return;
                locaisSugeridos = dados.sugestoes;
                const opcoes = locaisSugeridos.map((local) => {
                    const opcao = document.createElement('option');
                    opcao.value = local.nome;
                    opcao.label = local.detalhe || local.tipo;
                    return opcao;
                });
                sugestoes.replaceChildren(...opcoes);
            } catch {
                if (!consulta.signal.aborted) sugestoes.replaceChildren();
            }
        }, 180);
    });

    const modeloCartao = document.getElementById('mapa-cartao-local');
    function criarCartao(grupo) {
        const {predio, locais} = grupo;
        const cartao = modeloCartao.content.firstElementChild.cloneNode(true);
        const titulo = cartao.querySelector('[data-nome]');
        const tipo = cartao.querySelector('[data-tipo]');
        const andar = cartao.querySelector('[data-andar]');
        const linkPredio = cartao.querySelector('[data-ver-predio]');
        const linkLocal = cartao.querySelector('[data-ver-local]');
        const linkRota = cartao.querySelector('[data-ver-rota]');
        const formRotaExterna = cartao.querySelector('[data-rota-externa]');
        const seletor = cartao.querySelector('select');

        linkPredio.href = predio.url;
        formRotaExterna.action = predio.url_rota_externa;
        atualizarFormulario(formRotaExterna);

        function mostrarLocal(local) {
            grupo.selecionado = local.id;
            titulo.textContent = local.nome;
            tipo.textContent = local.tipo;
            andar.textContent = local.andar || '—';
            linkLocal.hidden = !local.destino;
            linkLocal.href = local.url;

            const url = new URL(predio.url_rota, window.location.href);
            if (local.destino) url.searchParams.set('destino', local.destino);
            linkRota.href = url;
            formRotaExterna.elements.destino.value = local.destino ?? '';
        }

        const atual = locais.find((local) => local.id === grupo.selecionado) ?? locais[0];
        if (locais.length > 1) {
            for (const local of locais) {
                const descricao = local.andar ? local.nome + ' · ' + local.andar : local.nome;
                seletor.add(new Option(descricao, local.id));
            }
            seletor.closest('label').hidden = false;
            seletor.value = atual.id;
            seletor.addEventListener('change', () => mostrarLocal(locais[seletor.selectedIndex]));
        }
        mostrarLocal(atual);
        return cartao;
    }

    if (!elemento || !window.L) return;

    const siglas = {
        predio: 'PR', banheiro: 'WC', auditorio: 'AU', sala: 'SA',
        laboratorio: 'LB', biblioteca: 'BI', restaurante: 'RE',
        entrada: 'EN', elevador: 'EL', escada: 'ES', outro: '•',
    };
    const predios = JSON.parse(document.getElementById('mapa-dados').textContent);
    elemento.hidden = false;
    mapa = L.map(elemento).setView([-22.9793, -43.23245], 17);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        referrerPolicy: 'strict-origin-when-cross-origin',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapa);
    for (const predio of predios) {
        const porTipo = new Map();
        for (const local of predio.locais) {
            if (!porTipo.has(local.pin)) porTipo.set(local.pin, []);
            porTipo.get(local.pin).push(local);
        }

        Array.from(porTipo.entries()).forEach(([tipo, locais], indice) => {
            const coluna = indice % 3;
            const linha = Math.floor(indice / 3);
            const colunasNaLinha = Math.min(3, porTipo.size - linha * 3);
            const x = (coluna - (colunasNaLinha - 1) / 2) * 36;
            const y = linha * 38;
            const icone = L.divIcon({
                className: 'mapa-marcador mapa-marcador--' + tipo,
                html: '<span class="mapa-pin" aria-hidden="true"><span>' + siglas[tipo] + '</span></span>',
                iconSize: [30, 36],
                iconAnchor: [15 - x, 36 - y],
                popupAnchor: [x, y - 32],
            });
            const nome = locais.length === 1 ? locais[0].nome : locais[0].tipo + ' · ' + predio.nome;
            const grupo = {predio, locais};
            grupo.marcador = L.marker([predio.latitude, predio.longitude], {icon: icone, title: nome})
                .bindPopup(() => criarCartao(grupo), {maxWidth: 270})
                .addTo(mapa);
            const pin = grupo.marcador.getElement();
            pin.setAttribute('aria-label', nome);
            pin.setAttribute('aria-expanded', 'false');
            grupo.marcador.on('popupopen popupclose', (evento) => {
                const ativo = evento.type === 'popupopen';
                pin.classList.toggle('mapa-marcador--ativo', ativo);
                pin.setAttribute('aria-expanded', String(ativo));
                grupo.marcador.setZIndexOffset(ativo ? 1000 : 0);
                if (ativo) {
                    const formulario = evento.popup.getElement()?.querySelector('[data-rota-externa]');
                    if (formulario) atualizarFormulario(formulario);
                }
            });
            for (const local of locais) marcadores.set(local.id, grupo);
        });
    }

    if (predios.length === 1) mapa.setView([predios[0].latitude, predios[0].longitude], 18);
    for (const botao of document.querySelectorAll('[data-focar-local]')) {
        if (marcadores.has(botao.dataset.focarLocal)) {
            botao.hidden = false;
            botao.addEventListener('click', () => {
                if (focarLocal(botao.dataset.focarLocal)) elemento.scrollIntoView({block: 'nearest'});
            });
        }
    }
    document.getElementById('mapa-estatico').hidden = true;
})();
