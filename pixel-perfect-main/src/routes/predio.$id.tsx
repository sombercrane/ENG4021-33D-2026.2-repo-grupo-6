import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { DarkHeader } from "@/components/puc/Brand";
import { PhoneFrame } from "@/components/puc/PhoneFrame";
import { TipoEspacoIcon, TipoPontoIcon } from "@/components/puc/icons";
import {
  getAndaresDoPredio,
  getEspacosDoAndar,
  getPontosDoAndar,
  getPredio,
  getTipoPonto,
} from "@/lib/puc-data";

export const Route = createFileRoute("/predio/$id")({
  head: () => ({
    meta: [
      { title: "Andares e espaços do prédio — LocalizaPUC" },
      {
        name: "description",
        content:
          "Veja os andares de cada prédio da PUC-Rio, com salas, laboratórios, auditórios e pontos de interesse.",
      },
      { property: "og:title", content: "Andares e espaços do prédio — LocalizaPUC" },
      {
        property: "og:description",
        content: "Navegue pelos andares de um prédio da PUC-Rio e veja os espaços de cada um.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: PredioPage,
});

function PredioPage() {
  const { id } = Route.useParams();
  const navigate = useNavigate();
  const predio = getPredio(id);
  const andares = predio ? getAndaresDoPredio(predio.id_predio) : [];
  const [andarAtivo, setAndarAtivo] = useState(andares[0]?.id_andar ?? "");

  if (!predio) {
    return (
      <PhoneFrame>
        <DarkHeader onBack={() => navigate({ to: "/mapa", search: {} })} />
        <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
          <p className="t-place">Prédio não encontrado</p>
          <Link to="/mapa" search={{}} className="puc-btn">
            Voltar ao mapa
          </Link>
        </div>
      </PhoneFrame>
    );
  }

  const espacos = getEspacosDoAndar(andarAtivo);
  const pontos = getPontosDoAndar(andarAtivo);

  return (
    <PhoneFrame>
      <DarkHeader onBack={() => navigate({ to: "/mapa", search: {} })} />

      <div className="flex-1 overflow-y-auto pb-8">
        <div className="bg-heading px-5 pb-5">
          <h1 className="text-2xl font-bold text-white">{predio.nome}</h1>
          <p className="t-body mt-1 text-white/80">{predio.descricao}</p>
          <p className="t-caption mt-2 text-white/60">{predio.endereco}</p>
        </div>

        <div className="flex gap-2 overflow-x-auto px-5 py-4">
          {andares.map((a) => (
            <button
              key={a.id_andar}
              onClick={() => setAndarAtivo(a.id_andar)}
              className={`shrink-0 rounded-full px-4 py-1.5 text-xs font-semibold ${
                a.id_andar === andarAtivo
                  ? "bg-primary text-primary-foreground"
                  : "bg-surface text-heading"
              }`}
            >
              {a.nome}
            </button>
          ))}
        </div>

        <h2 className="t-section mb-3 px-5">Espaços do andar</h2>
        {espacos.length === 0 ? (
          <p className="t-body px-5 text-muted-foreground">Nenhum espaço cadastrado neste andar.</p>
        ) : (
          <ul className="flex flex-col gap-2 px-5">
            {espacos.map((e) => (
              <li key={e.id_espaco}>
                <Link
                  to="/espaco/$id"
                  params={{ id: e.id_espaco }}
                  className="puc-card flex items-center gap-3 px-4 py-3.5"
                >
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-white/70 text-heading">
                    <TipoEspacoIcon tipo={e.id_tipo} />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="t-place block truncate">{e.nome}</span>
                    <span className="t-caption block">{e.codigo}</span>
                  </span>
                  {e.acessivel ? <span className="puc-tag">Acessível</span> : null}
                </Link>
              </li>
            ))}
          </ul>
        )}

        <h2 className="t-section mb-3 mt-6 px-5">Pontos de interesse</h2>
        {pontos.length === 0 ? (
          <p className="t-body px-5 text-muted-foreground">Nenhum ponto cadastrado neste andar.</p>
        ) : (
          <ul className="flex flex-col gap-2 px-5">
            {pontos.map((p) => (
              <li key={p.id_ponto} className="flex items-center gap-3 rounded-xl bg-surface px-4 py-3">
                <span className="text-primary">
                  <TipoPontoIcon tipo={p.id_tipo_ponto} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="t-place block truncate">{p.nome}</span>
                  <span className="t-caption block">
                    {getTipoPonto(p.id_tipo_ponto).nome} · {p.descricao}
                  </span>
                </span>
              </li>
            ))}
          </ul>
        )}

        <div className="mt-7 px-5">
          <Link
            to="/mapa"
            search={{ destino: `V_${predio.id_predio}` }}
            className="puc-btn w-full"
          >
            Ver no mapa do campus
          </Link>
        </div>
      </div>
    </PhoneFrame>
  );
}
