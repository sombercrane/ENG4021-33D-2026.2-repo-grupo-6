/**
 * Modelagem de dados LocalizaPUC.
 * Entidades: Prédio, Andar, Espaço, Tipo_Espaço, Ponto, Tipo_Ponto.
 */

export type TipoEspacoId = "T_SALA" | "T_LAB" | "T_AUDIT" | "T_PREDIO";
export type TipoPontoId =
  | "TP_ENTRADA"
  | "TP_ELEVADOR"
  | "TP_ESCADA"
  | "TP_BANHEIRO"
  | "TP_BIBLIO"
  | "TP_RESTAUR";

export interface TipoEspaco {
  id_tipo: TipoEspacoId;
  nome: string;
  descricao: string;
  cor: string;
}

export interface TipoPonto {
  id_tipo_ponto: TipoPontoId;
  nome: string;
  descricao: string;
}

export interface Predio {
  id_predio: string;
  nome: string;
  sigla: string;
  descricao: string;
  endereco: string;
  pos_x: number;
  pos_y: number;
}

export interface Andar {
  id_andar: string;
  id_predio: string;
  numero: number;
  nome: string;
  descricao?: string;
}

export interface Espaco {
  id_espaco: string;
  id_andar: string;
  id_tipo: TipoEspacoId;
  nome: string;
  codigo: string;
  descricao: string;
  pos_x: number;
  pos_y: number;
  acessivel: boolean;
  observacoes: string;
}

export interface Ponto {
  id_ponto: string;
  id_andar: string;
  id_tipo_ponto: TipoPontoId;
  nome: string;
  pos_x: number;
  pos_y: number;
  descricao: string;
}

export const tiposEspaco: TipoEspaco[] = [
  { id_tipo: "T_SALA", nome: "Sala", descricao: "Salas de aula e estudos", cor: "var(--primary)" },
  {
    id_tipo: "T_LAB",
    nome: "Laboratório",
    descricao: "Laboratórios e centros de pesquisa",
    cor: "var(--tag)",
  },
  {
    id_tipo: "T_AUDIT",
    nome: "Auditório",
    descricao: "Auditórios e espaços de eventos",
    cor: "var(--route)",
  },
  {
    id_tipo: "T_PREDIO",
    nome: "Prédio",
    descricao: "Todos os prédios do campus",
    cor: "var(--heading)",
  },
];

export const tiposPonto: TipoPonto[] = [
  { id_tipo_ponto: "TP_ENTRADA", nome: "Entrada", descricao: "Entradas do prédio" },
  { id_tipo_ponto: "TP_ELEVADOR", nome: "Elevador", descricao: "Elevadores" },
  { id_tipo_ponto: "TP_ESCADA", nome: "Escada", descricao: "Escadas" },
  { id_tipo_ponto: "TP_BANHEIRO", nome: "Banheiro", descricao: "Banheiros" },
  { id_tipo_ponto: "TP_BIBLIO", nome: "Biblioteca", descricao: "Bibliotecas" },
  { id_tipo_ponto: "TP_RESTAUR", nome: "Restaurante", descricao: "Restaurantes e lanchonetes" },
];

const ENDERECO = "Rua Marquês de São Vicente, 225 — Gávea";

export const predios: Predio[] = [
  {
    id_predio: "P_RDC",
    nome: "Prédio RDC",
    sigla: "RDC",
    descricao: "Prédio do Departamento de Computação e cursos de TI.",
    endereco: ENDERECO,
    pos_x: 90,
    pos_y: 250,
  },
  {
    id_predio: "P_IAG",
    nome: "Prédio IAG",
    sigla: "IAG",
    descricao: "Instituto de Artes e Design.",
    endereco: ENDERECO,
    pos_x: 220,
    pos_y: 200,
  },
  {
    id_predio: "P_KEN",
    nome: "Prédio Kennedy",
    sigla: "K",
    descricao: "Centro de Ciências Sociais e Humanas.",
    endereco: ENDERECO,
    pos_x: 310,
    pos_y: 285,
  },
  {
    id_predio: "P_LEME",
    nome: "Prédio Leme",
    sigla: "L",
    descricao: "Prédio de Ciências Exatas e Laboratórios.",
    endereco: ENDERECO,
    pos_x: 140,
    pos_y: 380,
  },
  {
    id_predio: "P_REIT",
    nome: "Prédio da Reitoria",
    sigla: "R",
    descricao: "Administração central da PUC-Rio.",
    endereco: ENDERECO,
    pos_x: 255,
    pos_y: 120,
  },
];

export const andares: Andar[] = [
  { id_andar: "A_L1", id_predio: "P_LEME", numero: 1, nome: "Térreo" },
  { id_andar: "A_L2", id_predio: "P_LEME", numero: 2, nome: "2º andar" },
  { id_andar: "A_R1", id_predio: "P_RDC", numero: 1, nome: "Térreo" },
  { id_andar: "A_R2", id_predio: "P_RDC", numero: 2, nome: "2º andar" },
  { id_andar: "A_R3", id_predio: "P_RDC", numero: 3, nome: "3º andar" },
  { id_andar: "A_I1", id_predio: "P_IAG", numero: 1, nome: "Térreo" },
  { id_andar: "A_I2", id_predio: "P_IAG", numero: 2, nome: "2º andar" },
  { id_andar: "A_K1", id_predio: "P_KEN", numero: 1, nome: "Térreo" },
  { id_andar: "A_K2", id_predio: "P_KEN", numero: 2, nome: "2º andar" },
  { id_andar: "A_REIT1", id_predio: "P_REIT", numero: 1, nome: "Térreo" },
];

export const espacos: Espaco[] = [
  {
    id_espaco: "E_RDC_AUD",
    id_andar: "A_R2",
    id_tipo: "T_AUDIT",
    nome: "Auditório RDC",
    codigo: "RDC-200",
    descricao: "Auditório principal do Prédio RDC, com capacidade para 120 pessoas.",
    pos_x: 90,
    pos_y: 250,
    acessivel: true,
    observacoes: "Equipado com projetor 4K e sistema de som.",
  },
  {
    id_espaco: "E_IAG_AUD",
    id_andar: "A_I2",
    id_tipo: "T_AUDIT",
    nome: "Auditório IAG",
    codigo: "IAG-201",
    descricao: "Auditório do Instituto de Artes e Design.",
    pos_x: 220,
    pos_y: 200,
    acessivel: true,
    observacoes: "",
  },
  {
    id_espaco: "E_KEN_AUD",
    id_andar: "A_K2",
    id_tipo: "T_AUDIT",
    nome: "Auditório Kennedy",
    codigo: "KEN-201",
    descricao: "Auditório do Centro de Ciências Sociais.",
    pos_x: 310,
    pos_y: 285,
    acessivel: false,
    observacoes: "Acesso apenas por escada.",
  },
  {
    id_espaco: "E_L_FIS",
    id_andar: "A_L2",
    id_tipo: "T_LAB",
    nome: "Laboratório de Física",
    codigo: "L252",
    descricao: "Laboratório didático de Física Experimental.",
    pos_x: 140,
    pos_y: 380,
    acessivel: true,
    observacoes: "Acesso controlado — cartão de aluno.",
  },
  {
    id_espaco: "E_L100",
    id_andar: "A_L1",
    id_tipo: "T_SALA",
    nome: "Sala L100",
    codigo: "L100",
    descricao: "Sala de aula padrão — 40 lugares.",
    pos_x: 140,
    pos_y: 380,
    acessivel: true,
    observacoes: "",
  },
  {
    id_espaco: "E_L340",
    id_andar: "A_L2",
    id_tipo: "T_SALA",
    nome: "Sala L340",
    codigo: "L340",
    descricao: "Sala de aula — 50 lugares.",
    pos_x: 140,
    pos_y: 380,
    acessivel: true,
    observacoes: "",
  },
  {
    id_espaco: "E_RDC402",
    id_andar: "A_R3",
    id_tipo: "T_SALA",
    nome: "Sala 402 — Bloco RDC",
    codigo: "RDC-402",
    descricao: "Sala de aula de pós-graduação.",
    pos_x: 90,
    pos_y: 250,
    acessivel: true,
    observacoes: "",
  },
  {
    id_espaco: "E_KEN_BIB",
    id_andar: "A_K1",
    id_tipo: "T_SALA",
    nome: "Biblioteca Kennedy",
    codigo: "KEN-BIB",
    descricao: "Acervo de ciências sociais e humanas.",
    pos_x: 310,
    pos_y: 285,
    acessivel: true,
    observacoes: "",
  },
  {
    id_espaco: "E_IAG_LAB",
    id_andar: "A_I1",
    id_tipo: "T_LAB",
    nome: "Laboratório de Design",
    codigo: "IAG-105",
    descricao: "Laboratório de prototipagem e modelagem.",
    pos_x: 220,
    pos_y: 200,
    acessivel: true,
    observacoes: "",
  },
  {
    id_espaco: "E_REIT_SALA",
    id_andar: "A_REIT1",
    id_tipo: "T_SALA",
    nome: "Atendimento ao Aluno",
    codigo: "REIT-001",
    descricao: "Secretaria e atendimento administrativo.",
    pos_x: 255,
    pos_y: 120,
    acessivel: true,
    observacoes: "Atendimento de 9h às 17h.",
  },
];

export const pontos: Ponto[] = [
  {
    id_ponto: "PT_L_ENTR",
    id_andar: "A_L1",
    id_tipo_ponto: "TP_ENTRADA",
    nome: "Entrada Prédio Leme",
    pos_x: 140,
    pos_y: 412,
    descricao: "Portaria principal",
  },
  {
    id_ponto: "PT_L_ELEV",
    id_andar: "A_L1",
    id_tipo_ponto: "TP_ELEVADOR",
    nome: "Elevador Leme",
    pos_x: 168,
    pos_y: 392,
    descricao: "Acessível",
  },
  {
    id_ponto: "PT_L_ESC",
    id_andar: "A_L2",
    id_tipo_ponto: "TP_ESCADA",
    nome: "Escada Leme",
    pos_x: 112,
    pos_y: 392,
    descricao: "Acesso aos andares superiores",
  },
  {
    id_ponto: "PT_R_ENTR",
    id_andar: "A_R1",
    id_tipo_ponto: "TP_ENTRADA",
    nome: "Entrada Prédio RDC",
    pos_x: 90,
    pos_y: 282,
    descricao: "Portaria",
  },
  {
    id_ponto: "PT_R_BIB",
    id_andar: "A_R2",
    id_tipo_ponto: "TP_BIBLIO",
    nome: "Biblioteca Central",
    pos_x: 120,
    pos_y: 240,
    descricao: "Acervo geral",
  },
  {
    id_ponto: "PT_R_WC",
    id_andar: "A_R1",
    id_tipo_ponto: "TP_BANHEIRO",
    nome: "Banheiros RDC",
    pos_x: 62,
    pos_y: 262,
    descricao: "Térreo, ao lado da portaria",
  },
  {
    id_ponto: "PT_K_REST",
    id_andar: "A_K1",
    id_tipo_ponto: "TP_RESTAUR",
    nome: "Restaurante Kennedy",
    pos_x: 340,
    pos_y: 300,
    descricao: "Almoço e lanches",
  },
  {
    id_ponto: "PT_I_WC",
    id_andar: "A_I1",
    id_tipo_ponto: "TP_BANHEIRO",
    nome: "Banheiros IAG",
    pos_x: 248,
    pos_y: 214,
    descricao: "Térreo",
  },
];

/** Posição simulada do usuário no mapa do campus. */
export const posicaoUsuario = { x: 200, y: 330 };

export interface EspacoFull {
  espaco: Espaco;
  andar: Andar;
  predio: Predio;
  tipo: TipoEspaco;
}

export function getPredio(id: string) {
  return predios.find((p) => p.id_predio === id) ?? null;
}

export function getAndaresDoPredio(id_predio: string) {
  return andares
    .filter((a) => a.id_predio === id_predio)
    .sort((a, b) => a.numero - b.numero);
}

export function getEspacosDoAndar(id_andar: string) {
  return espacos.filter((e) => e.id_andar === id_andar);
}

export function getPontosDoAndar(id_andar: string) {
  return pontos.filter((p) => p.id_andar === id_andar);
}

export function getTipoPonto(id: TipoPontoId) {
  return tiposPonto.find((t) => t.id_tipo_ponto === id)!;
}

export function getEspacoFull(id_espaco: string): EspacoFull | null {
  const espaco = espacos.find((e) => e.id_espaco === id_espaco);
  if (!espaco) return null;
  const andar = andares.find((a) => a.id_andar === espaco.id_andar)!;
  const predio = predios.find((p) => p.id_predio === andar.id_predio)!;
  const tipo = tiposEspaco.find((t) => t.id_tipo === espaco.id_tipo)!;
  return { espaco, andar, predio, tipo };
}

/** Busca por nome, código, prédio ou andar, com filtro opcional de categoria. */
export function searchByQuery(query: string, categoria?: TipoEspacoId | null): EspacoFull[] {
  const q = (query || "").toLowerCase().trim();
  const results: EspacoFull[] = [];

  espacos.forEach((espaco) => {
    if (categoria && categoria !== "T_PREDIO" && espaco.id_tipo !== categoria) return;
    if (categoria === "T_PREDIO") return;
    const andar = andares.find((a) => a.id_andar === espaco.id_andar)!;
    const predio = predios.find((p) => p.id_predio === andar.id_predio)!;
    const campos = [espaco.nome, espaco.codigo, predio.nome, predio.sigla, andar.nome].map((s) =>
      s.toLowerCase(),
    );
    if (!q || campos.some((c) => c.includes(q))) {
      results.push({
        espaco,
        andar,
        predio,
        tipo: tiposEspaco.find((t) => t.id_tipo === espaco.id_tipo)!,
      });
    }
  });

  if (!categoria || categoria === "T_PREDIO") {
    predios.forEach((predio) => {
      const match = !q || [predio.nome, predio.sigla].some((s) => s.toLowerCase().includes(q));
      if (!match) return;
      const andar = getAndaresDoPredio(predio.id_predio)[0];
      if (!andar) return;
      results.push({
        espaco: {
          id_espaco: `V_${predio.id_predio}`,
          id_andar: andar.id_andar,
          id_tipo: "T_PREDIO",
          nome: predio.nome,
          codigo: predio.sigla,
          descricao: predio.descricao,
          pos_x: predio.pos_x,
          pos_y: predio.pos_y,
          acessivel: true,
          observacoes: predio.endereco,
        },
        andar,
        predio,
        tipo: tiposEspaco.find((t) => t.id_tipo === "T_PREDIO")!,
      });
    });
  }

  return results;
}

/** Resolve um espaço real ou virtual (prédio) pelo id. */
export function resolveEspaco(id: string): EspacoFull | null {
  if (id.startsWith("V_")) {
    const predio = getPredio(id.slice(2));
    if (!predio) return null;
    const andar = getAndaresDoPredio(predio.id_predio)[0];
    if (!andar) return null;
    return {
      espaco: {
        id_espaco: id,
        id_andar: andar.id_andar,
        id_tipo: "T_PREDIO",
        nome: predio.nome,
        codigo: predio.sigla,
        descricao: predio.descricao,
        pos_x: predio.pos_x,
        pos_y: predio.pos_y,
        acessivel: true,
        observacoes: predio.endereco,
      },
      andar,
      predio,
      tipo: tiposEspaco.find((t) => t.id_tipo === "T_PREDIO")!,
    };
  }
  return getEspacoFull(id);
}

/** Distância/tempo estimados até o destino (simulação do protótipo). */
export function estimarRota(destino: { pos_x: number; pos_y: number }) {
  const dx = destino.pos_x - posicaoUsuario.x;
  const dy = destino.pos_y - posicaoUsuario.y;
  const metros = Math.round(Math.hypot(dx, dy) * 1.4);
  const minutos = Math.max(1, Math.round(metros / 75));
  return { metros, minutos };
}
