import type { ReactNode } from "react";
import { Link } from "@tanstack/react-router";

type Tab = "home" | "map";

const tabs: { id: Tab; label: string; to: string; icon: (active: boolean) => ReactNode }[] = [
  {
    id: "home",
    label: "Início",
    to: "/",
    icon: (active) => (
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
        <path
          d="M3 11l9-7 9 7v9a2 2 0 01-2 2h-3v-6h-8v6H5a2 2 0 01-2-2v-9z"
          fill={active ? "var(--primary)" : "none"}
          stroke={active ? "none" : "currentColor"}
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    id: "map",
    label: "Mapa",
    to: "/mapa",
    icon: (active) => (
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
        <path
          d="M9 4l-6 2v14l6-2 6 2 6-2V4l-6 2-6-2zm0 2.2l6 2v11.6l-6-2V6.2z"
          fill={active ? "var(--primary)" : "none"}
          stroke={active ? "none" : "currentColor"}
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
];

export function BottomNav({ active }: { active: Tab }) {
  return (
    <nav
      aria-label="Navegação principal"
      className="flex shrink-0 items-center justify-around border-t border-border bg-background px-3 py-2"
    >
      {tabs.map((tab) => {
        const isActive = tab.id === active;
        return (
          <Link
            key={tab.id}
            to={tab.to}
            className={`relative flex flex-1 flex-col items-center gap-1 rounded-xl px-2 py-2 ${
              isActive ? "text-heading" : "text-muted-foreground"
            }`}
          >
            {tab.icon(isActive)}
            <span className="text-xs">{tab.label}</span>
            {isActive ? (
              <span className="absolute bottom-0.5 h-[3px] w-9 rounded-full bg-heading" />
            ) : null}
          </Link>
        );
      })}
    </nav>
  );
}
