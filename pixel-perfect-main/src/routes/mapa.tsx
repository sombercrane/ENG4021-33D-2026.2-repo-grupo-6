import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { DarkHeader } from "@/components/puc/Brand";
import { BottomNav } from "@/components/puc/BottomNav";
import { PhoneFrame } from "@/components/puc/PhoneFrame";
import { CampusMap } from "@/components/puc/CampusMap";
import { TipoPontoIcon } from "@/components/puc/icons";
import { estimarRota, resolveEspaco, tiposPonto, type TipoPontoId } from "@/lib/puc-data";

type MapaSearch = { destino?: string };

export const Route = createFileRoute("/mapa")({
  validateSearch: (search: Record<string, unknown>): MapaSearch => {
    const out: MapaSearch = {};
    const destino = search["destino"] as string | undefined;
    if (destino) out.destino = destino;
    return out;
  },
  head: () => ({
    meta: [
      { title: "Mapa da PUC-Rio — LocalizaPUC" },
      {
        name: "description",
        content:
          "Veja o mapa do campus da PUC-Rio com a sua localização, o destino destacado e os pontos de interesse.",
      },
      { property: "og:title", content: "Mapa da PUC-Rio — LocalizaPUC" },
      {
        property: "og:description",
        content: "Mapa do campus com destino destacado, rota estimada e pontos de interesse.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Mapa,
});

function Mapa() {
  const { destino: destinoId } = Route.useSearch();
  const navigate = useNavigate();
  const [filtros, setFiltros] = useState<TipoPontoId[]>([]);

  const destino = destinoId ? resolveEspaco(destinoId) : null;
  const rota = destino ? estimarRota(destino.espaco) : null;

  const toggleFiltro = (id: TipoPontoId) =>
    setFiltros((f) => (f.includes(id) ? f.filter((x) => x !== id) : [...f, id]));

  return (
    <PhoneFrame>
      <DarkHeader onBack={() => navigate({ to: "/" })} />

      <div className="flex items-center justify-between bg-heading px-5 pb-3">
        <h1 className="text-[15px] font-bold text-white">Mapa da PUC-Rio</h1>
        {destino ? (
          <button
            onClick={() => navigate({ to: "/mapa", search: {} })}
            className="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold text-white"
          >
            Ver campus inteiro
          </button>
        ) : null}
      </div>

      <div className="flex gap-2 overflow-x-auto bg-background px-5 py-3">
        {tiposPonto.map((t) => {
          const ativo = filtros.includes(t.id_tipo_ponto);
          return (
            <button
              key={t.id_tipo_ponto}
              onClick={() => toggleFiltro(t.id_tipo_ponto)}
              aria-pressed={ativo}
              className={`flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold ${
                ativo ? "bg-tag text-tag-foreground" : "bg-surface text-heading"
              }`}
            >
              <TipoPontoIcon tipo={t.id_tipo_ponto} size={14} />
              {t.nome}
            </button>
          );
        })}
      </div>

      <CampusMap
        destino={destino}
        filtros={filtros}
        onSelectPredio={(id) => navigate({ to: "/predio/$id", params: { id } })}
      />

      <div className="shrink-0 rounded-t-[24px] bg-background px-5 pb-4 pt-2 shadow-sheet">
        <span className="mx-auto mb-3 block h-1 w-10 rounded bg-surface-2" />
        {destino ? (
          <>
            <p className="t-caption">Destino selecionado</p>
            <div className="mb-3 mt-1 flex items-center gap-2">
              <span className="text-route">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
                  <path d="M12 2a7 7 0 00-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 00-7-7zm0 9.5A2.5 2.5 0 1112 6.5a2.5 2.5 0 010 5z" />
                </svg>
              </span>
              <h2 className="text-[22px] font-bold leading-tight text-heading">
                {destino.espaco.nome}
              </h2>
            </div>
            <div className="mb-4 grid grid-cols-3 gap-2">
              <InfoBlock label="Prédio" value={destino.predio.nome.replace("Prédio ", "")} />
              <InfoBlock label="Andar" value={destino.andar.nome} />
              <InfoBlock label="Espaço" value={destino.espaco.codigo} />
            </div>
            <p className="t-caption mb-3">
              Distância e tempo estimado até o destino: {rota?.metros} m · {rota?.minutos} min a pé
            </p>
            <div className="flex gap-2">
              <Link
                to="/espaco/$id"
                params={{ id: destino.espaco.id_espaco }}
                className="puc-btn flex-1"
              >
                Ver detalhes
              </Link>
              <Link
                to="/predio/$id"
                params={{ id: destino.predio.id_predio }}
                className="puc-btn-outline flex-1"
              >
                Ver andares
              </Link>
            </div>
          </>
        ) : (
          <>
            <p className="t-place mb-1">Visualização geral do campus</p>
            <p className="t-body mb-3 text-muted-foreground">
              Toque em um prédio para ver seus andares ou busque uma sala pelo nome ou código.
            </p>
            <Link to="/busca" search={{}} className="puc-btn w-full">
              Buscar sala
            </Link>
          </>
        )}
      </div>

      <BottomNav active="map" />
    </PhoneFrame>
  );
}

function InfoBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex min-h-[70px] flex-col gap-1 rounded-xl bg-surface p-3">
      <span className="t-caption">{label}</span>
      <span className="text-sm font-semibold leading-tight text-heading">{value}</span>
    </div>
  );
}
