import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Brand } from "@/components/puc/Brand";
import { BottomNav } from "@/components/puc/BottomNav";
import { PhoneFrame } from "@/components/puc/PhoneFrame";
import { TipoEspacoIcon } from "@/components/puc/icons";
import { tiposEspaco } from "@/lib/puc-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "LocalizaPUC — Encontre sua sala na PUC-Rio" },
      {
        name: "description",
        content:
          "Busque salas, laboratórios, auditórios e prédios do campus da PUC-Rio e veja a localização no mapa.",
      },
      { property: "og:title", content: "LocalizaPUC — Encontre sua sala na PUC-Rio" },
      {
        property: "og:description",
        content: "Mapa e localização de salas, laboratórios e auditórios do campus da PUC-Rio.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Home,
});

const CAT_BG = ["bg-cat-1", "bg-cat-2", "bg-cat-3", "bg-cat-4"];

function Home() {
  const navigate = useNavigate();

  return (
    <PhoneFrame>
      <header className="flex shrink-0 items-center justify-between bg-background px-5 pb-4 pt-5">
        <Brand />
      </header>

      <main className="flex-1 overflow-y-auto pb-6">
        <div className="relative mx-5 mb-6 h-[200px] overflow-hidden rounded-[20px] bg-[linear-gradient(135deg,oklch(0.62_0.06_147)_0%,oklch(0.379_0.051_151)_60%,oklch(0.28_0.036_151.9)_100%)] shadow-card">
          <div className="absolute inset-0 bg-[linear-gradient(180deg,transparent_0%,oklch(0.28_0.036_151.9/0.55)_100%)]" />
          <div className="relative p-6">
            <h1 className="t-display text-white">Bem-vindo à PUC-Rio!</h1>
            <p className="t-body mt-2 max-w-[75%] text-white/90">
              Encontre salas, laboratórios, auditórios e prédios no campus.
            </p>
          </div>
        </div>

        <button
          onClick={() => navigate({ to: "/busca" })}
          className="mx-5 mb-7 flex w-[calc(100%-2.5rem)] items-center gap-3 rounded-full bg-surface px-5 py-4 text-left transition-colors hover:bg-surface-2 active:scale-[0.98]"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true">
            <circle cx="11" cy="11" r="6" stroke="var(--heading)" strokeWidth="2" />
            <path d="M20 20l-3.5-3.5" stroke="var(--heading)" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <span className="flex-1 text-[15px] text-muted-foreground">Para onde quer ir?</span>
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true">
            <path
              d="M9 6l6 6-6 6"
              stroke="var(--heading)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <h2 className="t-section mb-3 px-5">Categorias</h2>
        <div className="grid grid-cols-2 gap-3.5 px-5">
          {tiposEspaco.map((tipo, i) => (
            <button
              key={tipo.id_tipo}
              onClick={() => navigate({ to: "/busca", search: { cat: tipo.id_tipo } })}
              className={`${CAT_BG[i]} flex min-h-[112px] flex-col gap-2 rounded-[20px] border border-transparent p-4 text-left transition hover:border-border active:scale-[0.98]`}
            >
              <span className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-white/70 text-primary">
                <TipoEspacoIcon tipo={tipo.id_tipo} size={22} />
              </span>
              <span>
                <span className="block font-bold text-heading">
                  {tipo.id_tipo === "T_PREDIO" ? "Prédios" : `${tipo.nome}s`}
                </span>
                <span className="t-caption mt-0.5 block">{tipo.descricao}</span>
              </span>
            </button>
          ))}
        </div>

        <div className="mt-7 px-5">
          <Link to="/mapa" className="puc-btn w-full">
            Ver mapa do campus
          </Link>
        </div>
      </main>

      <BottomNav active="home" />
    </PhoneFrame>
  );
}
