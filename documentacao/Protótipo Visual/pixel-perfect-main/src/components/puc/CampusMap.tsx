import { useEffect, useRef, useState } from "react";
import {
  pontos as todosOsPontos,
  posicaoUsuario,
  predios,
  type EspacoFull,
  type TipoPontoId,
} from "@/lib/puc-data";

const VIEW_W = 400;
const VIEW_H = 500;
const MIN_ZOOM = 0.8;
const MAX_ZOOM = 3.2;
const STEP = 0.35;

const CORES_PREDIO: Record<string, string> = {
  P_RDC: "var(--primary)",
  P_IAG: "var(--route)",
  P_KEN: "var(--heading)",
  P_LEME: "var(--tag)",
  P_REIT: "var(--foreground)",
};

interface Props {
  destino: EspacoFull | null;
  filtros: TipoPontoId[];
  onSelectPredio?: (id_predio: string) => void;
}

export function CampusMap({ destino, filtros, onSelectPredio }: Props) {
  const [zoom, setZoom] = useState(1.4);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const drag = useRef<{ x: number; y: number; px: number; py: number } | null>(null);
  const [dragging, setDragging] = useState(false);

  const centerOn = (x: number, y: number, z: number) => {
    setZoom(z);
    setPan({ x: VIEW_W / 2 - x * z, y: VIEW_H / 2 - y * z });
  };

  const destinoId = destino?.espaco.id_espaco ?? null;
  useEffect(() => {
    if (destino) centerOn(destino.espaco.pos_x, destino.espaco.pos_y, 1.8);
    else centerOn(200, 260, 1.1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [destinoId]);

  const pontosVisiveis = filtros.length
    ? todosOsPontos.filter((p) => filtros.includes(p.id_tipo_ponto))
    : [];

  const onPointerDown = (e: React.PointerEvent<SVGSVGElement>) => {
    drag.current = { x: e.clientX, y: e.clientY, px: pan.x, py: pan.y };
    setDragging(true);
  };
  const onPointerMove = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!drag.current) return;
    const scale = VIEW_W / (e.currentTarget.clientWidth || VIEW_W);
    setPan({
      x: drag.current.px + (e.clientX - drag.current.x) * scale,
      y: drag.current.py + (e.clientY - drag.current.y) * scale,
    });
  };
  const endDrag = () => {
    drag.current = null;
    setDragging(false);
  };

  const zoomBy = (delta: number) => {
    const next = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, zoom + delta));
    setPan({
      x: VIEW_W / 2 - ((VIEW_W / 2 - pan.x) / zoom) * next,
      y: VIEW_H / 2 - ((VIEW_H / 2 - pan.y) / zoom) * next,
    });
    setZoom(next);
  };

  return (
    <div className="relative flex-1 overflow-hidden bg-surface">
      <svg
        viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
        className={`h-full w-full touch-none ${dragging ? "cursor-grabbing" : "cursor-grab"}`}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerLeave={endDrag}
        role="img"
        aria-label="Mapa do campus da PUC-Rio"
      >
        <rect width={VIEW_W} height={VIEW_H} fill="var(--surface)" />
        <g transform={`translate(${pan.x} ${pan.y}) scale(${zoom})`}>
          <rect x="20" y="60" width="360" height="400" rx="24" fill="var(--cat-1)" />
          <path
            d="M40 430 C120 400 160 340 200 300 C250 250 280 180 330 140"
            stroke="var(--surface-2)"
            strokeWidth="18"
            fill="none"
            strokeLinecap="round"
          />
          <path
            d="M60 200 C140 210 240 250 360 250"
            stroke="var(--surface-2)"
            strokeWidth="14"
            fill="none"
            strokeLinecap="round"
          />

          {destino ? (
            <path
              d={`M${posicaoUsuario.x} ${posicaoUsuario.y} Q ${
                (posicaoUsuario.x + destino.espaco.pos_x) / 2 + 30
              } ${(posicaoUsuario.y + destino.espaco.pos_y) / 2} ${destino.espaco.pos_x} ${
                destino.espaco.pos_y
              }`}
              stroke="var(--route)"
              strokeWidth="4"
              strokeDasharray="8 7"
              fill="none"
              strokeLinecap="round"
            />
          ) : null}

          {predios.map((p) => {
            const selecionado = destino?.predio.id_predio === p.id_predio;
            const w = 62;
            const h = 56;
            return (
              <g
                key={p.id_predio}
                className="cursor-pointer"
                onClick={() => onSelectPredio?.(p.id_predio)}
              >
                {selecionado ? (
                  <rect
                    x={p.pos_x - w / 2 - 6}
                    y={p.pos_y - h / 2 + 2}
                    width={w + 12}
                    height={h + 12}
                    rx="12"
                    fill="var(--route)"
                    opacity="0.18"
                  />
                ) : null}
                <rect
                  x={p.pos_x - w / 2}
                  y={p.pos_y - h / 2 + 8}
                  width={w}
                  height={h}
                  rx="6"
                  fill={CORES_PREDIO[p.id_predio] ?? "var(--primary)"}
                  opacity={selecionado ? 1 : 0.9}
                  stroke={selecionado ? "var(--route)" : "transparent"}
                  strokeWidth="2.5"
                />
                <g fill="var(--surface)" opacity="0.75">
                  {[0, 1].map((row) =>
                    [-14, -4, 6].map((dx) => (
                      <rect
                        key={`${row}-${dx}`}
                        x={p.pos_x + dx}
                        y={p.pos_y - 8 + row * 9}
                        width="3.5"
                        height="3.5"
                      />
                    )),
                  )}
                </g>
                <text
                  x={p.pos_x}
                  y={p.pos_y + 38}
                  textAnchor="middle"
                  fontSize="11"
                  fontWeight="700"
                  fill="var(--heading)"
                >
                  {p.sigla}
                </text>
              </g>
            );
          })}

          {pontosVisiveis.map((pt) => (
            <g key={pt.id_ponto}>
              <circle cx={pt.pos_x} cy={pt.pos_y} r="7" fill="var(--background)" />
              <circle
                cx={pt.pos_x}
                cy={pt.pos_y}
                r="5"
                fill="var(--tag)"
                stroke="var(--heading)"
                strokeWidth="1"
              />
              <title>{pt.nome}</title>
            </g>
          ))}

          <g>
            <circle
              cx={posicaoUsuario.x}
              cy={posicaoUsuario.y}
              r="14"
              fill="var(--primary)"
              opacity="0.18"
            />
            <circle
              cx={posicaoUsuario.x}
              cy={posicaoUsuario.y}
              r="6"
              fill="var(--primary)"
              stroke="#fff"
              strokeWidth="2.5"
            />
            <title>Você está aqui</title>
          </g>

          {destino ? (
            <g transform={`translate(${destino.espaco.pos_x} ${destino.espaco.pos_y - 34})`}>
              <path
                d="M0 22C0 22 11 11.5 11 5.5A11 11 0 10-11 5.5C-11 11.5 0 22 0 22z"
                fill="var(--route)"
                stroke="#fff"
                strokeWidth="2"
              />
              <circle cy="5" r="4" fill="#fff" />
            </g>
          ) : null}
        </g>
      </svg>

      {destino ? (
        <span className="pointer-events-none absolute left-4 top-4 rounded-[10px] bg-heading px-3.5 py-2 text-[13px] font-bold text-white">
          {destino.espaco.nome}
        </span>
      ) : null}

      <div className="absolute right-4 top-4 flex flex-col gap-1 rounded-xl bg-background p-1 shadow-card">
        <button
          onClick={() => zoomBy(STEP)}
          aria-label="Ampliar o mapa"
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-[22px] font-semibold text-heading hover:bg-surface"
        >
          +
        </button>
        <button
          onClick={() => zoomBy(-STEP)}
          aria-label="Reduzir o mapa"
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-[22px] font-semibold text-heading hover:bg-surface"
        >
          −
        </button>
      </div>

      <button
        onClick={() => centerOn(posicaoUsuario.x, posicaoUsuario.y, 1.8)}
        aria-label="Centralizar na minha localização"
        className="absolute bottom-5 right-4 inline-flex h-12 w-12 items-center justify-center rounded-full bg-background text-primary shadow-card"
      >
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true">
          <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="2" />
          <path
            d="M12 2v3M12 19v3M2 12h3M19 12h3"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </button>
    </div>
  );
}
