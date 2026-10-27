import type { TipoEspacoId, TipoPontoId } from "@/lib/puc-data";

export function TipoEspacoIcon({ tipo, size = 20 }: { tipo: TipoEspacoId; size?: number }) {
  const common = {
    viewBox: "0 0 24 24",
    width: size,
    height: size,
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.6,
    "aria-hidden": true as const,
  };
  if (tipo === "T_LAB")
    return (
      <svg {...common}>
        <path d="M9 3v6l-4 9a2 2 0 002 2h10a2 2 0 002-2l-4-9V3" strokeLinejoin="round" />
        <path d="M8 3h8" />
        <circle cx="11.5" cy="16" r="1" fill="currentColor" stroke="none" />
      </svg>
    );
  if (tipo === "T_AUDIT")
    return (
      <svg {...common}>
        <path d="M4 12c0-3 2-5 4-5h8c2 0 4 2 4 5v4H4v-4z" strokeLinejoin="round" />
        <path d="M6 12v3M9 12v3M15 12v3M18 12v3" />
        <rect x="9" y="18" width="6" height="2" fill="currentColor" stroke="none" />
      </svg>
    );
  if (tipo === "T_PREDIO")
    return (
      <svg {...common}>
        <path d="M5 21V7l7-4 7 4v14" strokeLinejoin="round" />
        <rect x="8" y="10" width="2" height="3" fill="currentColor" stroke="none" />
        <rect x="14" y="10" width="2" height="3" fill="currentColor" stroke="none" />
        <rect x="11" y="14" width="2" height="5" fill="currentColor" stroke="none" />
      </svg>
    );
  return (
    <svg {...common}>
      <path d="M7 3h10v18l-5-3-5 3V3z" strokeLinejoin="round" />
      <circle cx="12" cy="9" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function TipoPontoIcon({ tipo, size = 18 }: { tipo: TipoPontoId; size?: number }) {
  const common = {
    viewBox: "0 0 24 24",
    width: size,
    height: size,
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.6,
    "aria-hidden": true as const,
  };
  switch (tipo) {
    case "TP_ELEVADOR":
      return (
        <svg {...common}>
          <rect x="5" y="3" width="14" height="18" rx="2" />
          <path d="M12 3v18M9 9l-1.5 2h3L9 9zM15 15l1.5-2h-3L15 15z" />
        </svg>
      );
    case "TP_ESCADA":
      return (
        <svg {...common}>
          <path d="M4 20h4v-4h4v-4h4V8h4" strokeLinejoin="round" />
        </svg>
      );
    case "TP_BANHEIRO":
      return (
        <svg {...common}>
          <circle cx="8" cy="5" r="2" />
          <path d="M8 8c-1.7 0-2.5 1-2.5 2.5V14H7v6h2v-6h1.5v-3.5C10.5 9 9.7 8 8 8z" />
          <circle cx="16" cy="5" r="2" />
          <path d="M16 8l-2.5 6h1.7v6h1.6v-6h1.7L16 8z" />
        </svg>
      );
    case "TP_BIBLIO":
      return (
        <svg {...common}>
          <path d="M4 5h7v14H4zM13 5h7v14h-7z" strokeLinejoin="round" />
        </svg>
      );
    case "TP_RESTAUR":
      return (
        <svg {...common}>
          <path d="M6 3v8a2 2 0 004 0V3M8 11v10M16 3c-1.5 1-2 3-2 5s.5 3 2 3v10" />
        </svg>
      );
    default:
      return (
        <svg {...common}>
          <path d="M14 3H6v18h8M10 12h9m0 0l-3-3m3 3l-3 3" strokeLinejoin="round" />
        </svg>
      );
  }
}
