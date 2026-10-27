import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { DarkHeader } from "@/components/puc/Brand";
import { PhoneFrame } from "@/components/puc/PhoneFrame";
import { TipoEspacoIcon, TipoPontoIcon } from "@/components/puc/icons";
import { estimarRota, getPontosDoAndar, getTipoPonto, resolveEspaco } from "@/lib/puc-data";

export const Route = createFileRoute("/espaco/$id")({
  head: () => ({
    meta: [
      { title: "Detalhes do espaço — LocalizaPUC" },
      {
        name: "description",
        content:
          "Informações do espaço na PUC-Rio: prédio, andar, código, acessibilidade e como chegar.",
      },
      { property: "og:title", content: "Detalhes do espaço — LocalizaPUC" },
      {
        property: "og:description",
        content: "Prédio, andar, código e acessibilidade do espaço escolhido no campus da PUC-Rio.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: EspacoPage,
});

function EspacoPage() {
  const { id } = Route.useParams();
  const navigate = useNavigate();
  const full = resolveEspaco(id);

  if (!full) {
    return (
      <PhoneFrame>
        <DarkHeader onBack={() => navigate({ to: "/busca", search: {} })} />
        <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
          <p className="t-place">Local não encontrado</p>
          <p className="t-body text-muted-foreground">
            O espaço que você procura não está cadastrado. Tente buscar pelo código da sala.
          </p>
          <Link to="/busca" search={{}} className="puc-btn">
            Nova busca
          </Link>
        </div>
      </PhoneFrame>
    );
  }

  const { espaco, andar, predio, tipo } = full;
  const rota = estimarRota(espaco);
  const pontosDoAndar = getPontosDoAndar(andar.id_andar);

  return (
    <PhoneFrame>
      <DarkHeader onBack={() => navigate({ to: "/mapa", search: { destino: espaco.id_espaco } })} />

      <div className="flex-1 overflow-y-auto pb-8">
        <div className="flex items-center gap-3 bg-heading px-5 pb-6">
          <span className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-white/10 text-white">
            <TipoEspacoIcon tipo={espaco.id_tipo} size={28} />
          </span>
          <div className="min-w-0">
            <h1 className="text-2xl font-bold leading-tight text-white">{espaco.nome}</h1>
            <p className="t-body text-white/75">{espaco.codigo}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 px-5 py-4">
          <span className="puc-tag">{predio.nome.replace("Prédio ", "Bloco ")}</span>
          <span className="puc-tag">{andar.nome}</span>
          <span className="puc-tag">{tipo.nome}</span>
          {espaco.acessivel ? (
            <span className="puc-tag" style={{ background: "var(--primary)" }}>
              Acessível
            </span>
          ) : null}
        </div>

        <p className="t-body px-5 text-muted-foreground">{espaco.descricao}</p>

        <section className="mt-6 px-5">
          <h2 className="t-section mb-3">Localização</h2>
          <ul className="divide-y divide-border overflow-hidden rounded-[20px] bg-surface">
            <Row label="Prédio" value={predio.nome} />
            <Row label="Andar" value={andar.nome} />
            <Row label="Código" value={espaco.codigo} />
            <Row label="Endereço" value={predio.endereco} />
            <Row
              label="Até o destino"
              value={`${rota.metros} m · ${rota.minutos} min a pé`}
            />
          </ul>
        </section>

        {espaco.observacoes ? (
          <section className="mt-6 px-5">
            <h2 className="t-section mb-2">Observações</h2>
            <p className="t-body text-muted-foreground">{espaco.observacoes}</p>
          </section>
        ) : null}

        {pontosDoAndar.length ? (
          <section className="mt-6 px-5">
            <h2 className="t-section mb-3">No percurso</h2>
            <ul className="flex flex-col gap-2">
              {pontosDoAndar.map((p) => (
                <li key={p.id_ponto} className="flex items-center gap-3 rounded-xl bg-surface px-4 py-3">
                  <span className="text-route">
                    <TipoPontoIcon tipo={p.id_tipo_ponto} />
                  </span>
                  <span className="min-w-0">
                    <span className="t-place block truncate">{p.nome}</span>
                    <span className="t-caption block">{getTipoPonto(p.id_tipo_ponto).nome}</span>
                  </span>
                </li>
              ))}
            </ul>
          </section>
        ) : null}

        <div className="mt-7 flex gap-2 px-5">
          <Link
            to="/mapa"
            search={{ destino: espaco.id_espaco }}
            className="puc-btn flex-1"
          >
            Ver rota
          </Link>
          <Link
            to="/predio/$id"
            params={{ id: predio.id_predio }}
            className="puc-btn-outline flex-1"
          >
            Ver andares
          </Link>
        </div>
      </div>
    </PhoneFrame>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <li className="flex items-center justify-between gap-4 px-4 py-3">
      <span className="t-body text-muted-foreground">{label}</span>
      <span className="t-body text-right font-semibold text-heading">{value}</span>
    </li>
  );
}
