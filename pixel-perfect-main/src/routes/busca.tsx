import { useMemo, useState } from "react";
import { createFileRoute, useNavigate, useRouter } from "@tanstack/react-router";
import { DarkHeader } from "@/components/puc/Brand";
import { PhoneFrame } from "@/components/puc/PhoneFrame";
import { TipoEspacoIcon } from "@/components/puc/icons";
import { searchByQuery, tiposEspaco, type TipoEspacoId } from "@/lib/puc-data";

type BuscaSearch = { cat?: TipoEspacoId; q?: string };

export const Route = createFileRoute("/busca")({
  validateSearch: (search: Record<string, unknown>): BuscaSearch => {
    const out: BuscaSearch = {};
    const cat = search["cat"] as TipoEspacoId | undefined;
    const q = search["q"] as string | undefined;
    if (cat) out.cat = cat;
    if (q) out.q = q;
    return out;
  },
  head: () => ({
    meta: [
      { title: "Buscar sala, prédio ou código — LocalizaPUC" },
      {
        name: "description",
        content:
          "Pesquise salas, laboratórios, auditórios e prédios da PUC-Rio pelo nome ou código e veja em qual prédio e andar ficam.",
      },
      { property: "og:title", content: "Buscar sala, prédio ou código — LocalizaPUC" },
      {
        property: "og:description",
        content: "Sugestões em tempo real de salas, laboratórios, auditórios e prédios da PUC-Rio.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Busca,
});

function Busca() {
  const { cat, q } = Route.useSearch();
  const navigate = useNavigate();
  const router = useRouter();
  const [termo, setTermo] = useState(q ?? "");
  const [categoria, setCategoria] = useState<TipoEspacoId | null>(cat ?? null);

  const resultados = useMemo(() => searchByQuery(termo, categoria), [termo, categoria]);

  return (
    <PhoneFrame>
      <DarkHeader onBack={() => router.history.back()} />

      <div className="flex flex-1 flex-col overflow-hidden bg-background">
        <div className="mx-5 mt-4 flex items-center gap-2 rounded-full border border-border bg-background px-4 py-3 shadow-soft">
          <span className="text-heading">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true">
              <circle cx="11" cy="11" r="6" stroke="currentColor" strokeWidth="2" />
              <path d="M20 20l-3.5-3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </span>
          <input
            autoFocus
            value={termo}
            onChange={(e) => setTermo(e.target.value)}
            placeholder="Buscar sala, prédio ou código"
            aria-label="Buscar sala, prédio ou código"
            className="flex-1 bg-transparent px-2 text-base text-heading outline-none placeholder:text-muted-foreground"
          />
          {termo ? (
            <button
              onClick={() => setTermo("")}
              aria-label="Limpar busca"
              className="rounded-full p-1 text-muted-foreground hover:bg-surface"
            >
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </button>
          ) : null}
        </div>

        <div className="mt-4 flex gap-2 overflow-x-auto px-5 pb-1">
          <button
            onClick={() => setCategoria(null)}
            className={`shrink-0 rounded-full px-3.5 py-1.5 text-xs font-semibold ${
              categoria === null ? "bg-primary text-primary-foreground" : "bg-surface text-heading"
            }`}
          >
            Todos
          </button>
          {tiposEspaco.map((t) => (
            <button
              key={t.id_tipo}
              onClick={() => setCategoria(t.id_tipo)}
              className={`shrink-0 rounded-full px-3.5 py-1.5 text-xs font-semibold ${
                categoria === t.id_tipo
                  ? "bg-primary text-primary-foreground"
                  : "bg-surface text-heading"
              }`}
            >
              {t.id_tipo === "T_PREDIO" ? "Prédios" : `${t.nome}s`}
            </button>
          ))}
        </div>

        <h2 className="t-section mb-3 mt-5 px-5">
          {termo ? "Resultados" : "Sugestões"}
        </h2>

        {resultados.length === 0 ? (
          <div className="mx-5 rounded-[20px] bg-surface p-6 text-center">
            <p className="t-place">Local não encontrado</p>
            <p className="t-body mt-1 text-muted-foreground">
              Não encontramos “{termo}”. Verifique o nome ou o código da sala, como L252.
            </p>
          </div>
        ) : (
          <ul className="flex flex-1 flex-col gap-2 overflow-y-auto px-5 pb-6">
            {resultados.map((r) => (
              <li key={r.espaco.id_espaco}>
                <button
                  onClick={() =>
                    navigate({ to: "/mapa", search: { destino: r.espaco.id_espaco } })
                  }
                  className="puc-card flex w-full items-center gap-3 px-4 py-3.5 text-left"
                >
                  <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white/70 text-heading">
                    <TipoEspacoIcon tipo={r.espaco.id_tipo} />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="t-place block truncate">{r.espaco.nome}</span>
                    <span className="t-caption block truncate">
                      {r.predio.nome} · {r.andar.nome} · {r.tipo.nome}
                    </span>
                  </span>
                  <span className="text-muted-foreground">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" aria-hidden="true">
                      <path
                        d="M9 6l6 6-6 6"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </PhoneFrame>
  );
}
