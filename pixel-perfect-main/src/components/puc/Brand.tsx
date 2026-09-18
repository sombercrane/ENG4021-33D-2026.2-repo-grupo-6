import { Link } from "@tanstack/react-router";

export function BrandPin({ size = 28, tone = "dark" }: { size?: number; tone?: "dark" | "light" }) {
  const shell = tone === "dark" ? "var(--heading)" : "#FFFFFF";
  const inner = tone === "dark" ? "var(--surface)" : "var(--heading)";
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} aria-hidden="true">
      <path d="M12 2L4 6v6c0 5 3.5 8.7 8 10 4.5-1.3 8-5 8-10V6l-8-4z" fill={shell} />
      <g fill={inner}>
        <path d="M12 7l-3 2v6l3 1 3-1V9l-3-2zm0 1.4l1.7 1.1-1.7.7-1.7-.7L12 8.4zm-2 3.1l1.7.7v3.3l-1.7-.6v-3.4zm4 0v3.4l-1.7.6v-3.3l1.7-.7z" />
        <rect x="11.3" y="12.4" width="1.4" height="4" />
      </g>
    </svg>
  );
}

export function Brand({ tone = "dark" }: { tone?: "dark" | "light" }) {
  return (
    <Link to="/" className="flex items-center gap-3">
      <BrandPin tone={tone} size={tone === "dark" ? 28 : 22} />
      <span className="flex flex-col leading-none">
        <span
          className={`text-[22px] font-bold tracking-tight ${tone === "dark" ? "text-heading" : "text-white"}`}
        >
          Localiza
        </span>
        <span
          className={`text-[22px] font-bold tracking-wide ${tone === "dark" ? "text-primary" : "text-surface"}`}
        >
          PUC
        </span>
      </span>
    </Link>
  );
}

/** Cabeçalho escuro com botão voltar, usado em Busca, Mapa, Prédio e Espaço. */
export function DarkHeader({ onBack }: { onBack: () => void }) {
  return (
    <header className="flex shrink-0 items-center justify-between gap-3 bg-heading px-5 py-4">
      <button
        onClick={onBack}
        aria-label="Voltar"
        className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-white transition-colors hover:bg-white/10"
      >
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" aria-hidden="true">
          <path
            d="M15 6l-6 6 6 6"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      <div className="mx-auto">
        <Brand tone="light" />
      </div>
      <span className="w-10" />
    </header>
  );
}
