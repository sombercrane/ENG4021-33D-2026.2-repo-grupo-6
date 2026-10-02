import { createFileRoute } from "@tanstack/react-router";
import {
  Accessibility,
  ArrowLeft,
  Bath,
  Building2,
  ChevronRight,
  CircleHelp,
  DoorOpen,
  FlaskConical,
  Layers3,
  LocateFixed,
  MapPin,
  Minus,
  MoreHorizontal,
  Plus,
  Presentation,
  Search,
  Footprints,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Button } from "../components/ui/button";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "LocalizaPUC — Encontre seu caminho no campus" },
      { name: "description", content: "Busque salas, laboratórios, auditórios e prédios e veja sua rota no campus da PUC-Rio." },
      { property: "og:title", content: "LocalizaPUC — Encontre seu caminho no campus" },
      { property: "og:description", content: "Busque espaços e navegue pelo campus da PUC-Rio com facilidade." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: LocalizaPuc,
});

type Screen = "home" | "search" | "route";
type Room = { code: string; building: string; floor: string };

const rooms: Room[] = [
  { code: "L252", building: "Prédio Leme", floor: "2º andar" },
  { code: "L253", building: "Prédio Leme", floor: "2º andar" },
  { code: "L254", building: "Prédio Leme", floor: "2º andar" },
  { code: "L260", building: "Prédio Leme", floor: "2º andar" },
];

const categories = [
  { label: "Sala", icon: DoorOpen },
  { label: "Laboratório", icon: FlaskConical },
  { label: "Auditório", icon: Presentation },
  { label: "Prédio", icon: Building2 },
];

function Brand() {
  return (
    <div className="flex items-center gap-3" aria-label="LocalizaPUC">
      <div className="grid size-10 place-items-center rounded-full bg-primary text-primary-foreground">
        <MapPin size={21} strokeWidth={2.4} />
      </div>
      <div>
        <p className="font-display text-xl leading-none text-foreground">LocalizaPUC</p>
        <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.18em] text-muted-foreground">PUC-Rio</p>
      </div>
    </div>
  );
}

function CampusMap({ indoor = false, zoom = 1 }: { indoor?: boolean; zoom?: number }) {
  if (indoor) {
    return (
      <svg viewBox="0 0 720 620" className="h-full w-full transition-transform duration-300" style={{ transform: `scale(${zoom})` }} role="img" aria-label="Mapa interno do segundo andar do Prédio Leme com rota até a sala L252">
        <rect width="720" height="620" fill="var(--map)" />
        <g fill="var(--card)" stroke="var(--map-line)" strokeWidth="3">
          <path d="M70 90h210v130H170v105H70z" />
          <path d="M450 90h200v235H540V220h-90z" />
          <path d="M70 410h200v130H70z" />
          <path d="M450 410h200v130H450z" />
        </g>
        <g fill="var(--muted-foreground)" fontFamily="Manrope" fontSize="17" fontWeight="600">
          <text x="120" y="160">L248</text><text x="500" y="160">L252</text>
          <text x="125" y="480">L246</text><text x="505" y="480">L254</text>
        </g>
        <path d="M150 485 C260 480, 260 350, 345 350 S430 270, 535 180" fill="none" stroke="var(--route)" strokeWidth="10" strokeLinecap="round" strokeDasharray="2 24" />
        <circle cx="150" cy="485" r="17" fill="var(--primary)" stroke="var(--card)" strokeWidth="6" />
        <path d="M535 145c-25 0-44 19-44 43 0 34 44 72 44 72s44-38 44-72c0-24-19-43-44-43z" fill="var(--route)" />
        <circle cx="535" cy="187" r="12" fill="var(--card)" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 720 430" className="h-full w-full" role="img" aria-label="Mapa geral ilustrado do campus da PUC-Rio">
      <rect width="720" height="430" fill="var(--map)" />
      <path d="M0 315C125 255 160 356 288 295S520 236 720 305" fill="none" stroke="var(--card)" strokeWidth="42" />
      <path d="M338 0c-30 100 2 144-25 245s-10 125-1 185" fill="none" stroke="var(--card)" strokeWidth="24" />
      <g fill="var(--accent)" opacity=".72">
        <circle cx="77" cy="66" r="38"/><circle cx="151" cy="79" r="49"/><circle cx="622" cy="55" r="64"/><circle cx="92" cy="390" r="70"/><circle cx="654" cy="390" r="59"/>
      </g>
      <g fill="var(--secondary)" stroke="var(--map-line)" strokeWidth="2">
        <rect x="98" y="145" width="150" height="92" rx="6"/><rect x="422" y="116" width="178" height="115" rx="6"/><rect x="400" y="318" width="126" height="75" rx="6"/>
      </g>
      <g fill="var(--foreground)" fontFamily="Manrope" fontSize="14" fontWeight="700">
        <text x="143" y="195">Pilotis</text><text x="473" y="178">Leme</text><text x="424" y="361">Kennedy</text>
      </g>
      <path d="M345 300c-20 0-36 16-36 36 0 28 36 59 36 59s36-31 36-59c0-20-16-36-36-36z" fill="var(--route)" />
      <circle cx="345" cy="335" r="10" fill="var(--card)" />
    </svg>
  );
}

function LocalizaPuc() {
  const [screen, setScreen] = useState<Screen>("home");
  const [query, setQuery] = useState("L25");
  const [selected, setSelected] = useState<Room>({ code: "L252", building: "Prédio Leme", floor: "2º andar" });
  const [floor, setFloor] = useState("2");
  const [zoom, setZoom] = useState(1);
  const [poi, setPoi] = useState("Entrada");
  const filteredRooms = useMemo(() => rooms.filter((room) => room.code.toLowerCase().includes(query.toLowerCase())), [query]);

  return (
    <main className="min-h-screen bg-secondary px-0 py-0 sm:px-6 sm:py-8 lg:px-10">
      <div className="mx-auto min-h-screen max-w-6xl overflow-hidden bg-background shadow-map sm:min-h-[calc(100vh-4rem)] sm:rounded-lg">
        {screen === "home" && <HomeScreen onSearch={() => setScreen("search")} />}
        {screen === "search" && (
          <SearchScreen query={query} setQuery={setQuery} rooms={filteredRooms} selected={selected} setSelected={setSelected} onBack={() => setScreen("home")} onConfirm={() => setScreen("route")} />
        )}
        {screen === "route" && (
          <RouteScreen room={selected} floor={floor} setFloor={setFloor} zoom={zoom} setZoom={setZoom} poi={poi} setPoi={setPoi} onBack={() => setScreen("search")} />
        )}
      </div>
    </main>
  );
}

function HomeScreen({ onSearch }: { onSearch: () => void }) {
  return (
    <div className="grid min-h-screen lg:min-h-[calc(100vh-4rem)] lg:grid-cols-[0.82fr_1.18fr]">
      <section className="flex flex-col px-6 pb-8 pt-6 sm:px-10 sm:pt-8 lg:px-14 lg:py-12">
        <Brand />
        <div className="mt-14 max-w-xl lg:mt-auto">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-route">Navegue pelo campus</p>
          <h1 className="mt-3 font-display text-5xl leading-[0.95] text-foreground sm:text-6xl">Onde você quer chegar?</h1>
          <p className="mt-5 max-w-md text-base leading-7 text-muted-foreground">Encontre salas, laboratórios e outros espaços da PUC-Rio com rapidez.</p>
          <button onClick={onSearch} className="mt-8 flex min-h-14 w-full items-center gap-3 rounded-md bg-input px-5 text-left text-sm text-muted-foreground outline-none transition-shadow hover:shadow-map focus-visible:ring-2 focus-visible:ring-ring">
            <Search size={20} /><span className="truncate">buscar sala, laboratório, auditório...</span>
          </button>
        </div>
        <div className="mt-10 lg:mt-auto">
          <p className="mb-4 text-sm font-bold text-foreground">Buscar por categoria</p>
          <div className="grid grid-cols-2 gap-3">
            {categories.map(({ label, icon: Icon }) => (
              <Button key={label} variant="soft" onClick={onSearch} className="h-20 justify-start px-4 text-left">
                <span className="grid size-9 shrink-0 place-items-center rounded-full bg-background text-primary"><Icon size={18} /></span>{label}
              </Button>
            ))}
          </div>
        </div>
      </section>
      <section className="relative min-h-[380px] overflow-hidden bg-map lg:min-h-full">
        <CampusMap />
        <div className="absolute bottom-5 left-5 rounded-md bg-card px-4 py-3 shadow-map">
          <p className="text-xs text-muted-foreground">Você está perto de</p>
          <p className="mt-0.5 text-sm font-bold text-foreground">Entrada principal</p>
        </div>
        <Button variant="icon" aria-label="Minha localização" title="Minha localização" className="absolute bottom-5 right-5 size-11 p-0"><LocateFixed size={20} /></Button>
      </section>
    </div>
  );
}

function SearchScreen({ query, setQuery, rooms: results, selected, setSelected, onBack, onConfirm }: { query: string; setQuery: (value: string) => void; rooms: Room[]; selected: Room; setSelected: (room: Room) => void; onBack: () => void; onConfirm: () => void }) {
  return (
    <div className="mx-auto flex min-h-screen max-w-3xl flex-col px-5 py-6 sm:min-h-[calc(100vh-4rem)] sm:px-10 sm:py-9">
      <header className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBack} className="-ml-3 px-3"><ArrowLeft size={20} /> Sala</Button>
        <Brand />
      </header>
      <section className="mx-auto mt-12 w-full max-w-xl">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-route">Escolha seu destino</p>
        <h1 className="mt-2 font-display text-4xl text-foreground sm:text-5xl">Qual sala você procura?</h1>
        <label className="mt-8 flex min-h-16 items-center gap-3 rounded-md bg-input px-5 ring-2 ring-primary">
          <Search size={21} className="text-primary" />
          <span className="sr-only">Código da sala</span>
          <input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Digite o código da sala" className="min-w-0 flex-1 bg-transparent text-lg font-semibold uppercase text-foreground outline-none placeholder:normal-case placeholder:text-muted-foreground" />
          {query && <span className="text-xs font-semibold text-muted-foreground">{results.length} resultados</span>}
        </label>
        <div className="mt-5 space-y-2" role="listbox" aria-label="Salas encontradas">
          {results.map((room) => {
            const active = selected.code === room.code;
            return (
              <button key={room.code} role="option" aria-selected={active} onClick={() => setSelected(room)} className="flex min-h-20 w-full items-center gap-4 rounded-md border border-border bg-card px-5 text-left transition-colors hover:bg-secondary aria-selected:border-primary aria-selected:bg-secondary">
                <span className="grid size-10 place-items-center rounded-full bg-primary text-sm font-bold text-primary-foreground">L</span>
                <span className="min-w-0 flex-1"><strong className="block text-lg text-foreground">{room.code}</strong><span className="text-sm text-muted-foreground">{room.building} · {room.floor}</span></span>
                <ChevronRight size={20} className={active ? "text-primary" : "text-muted-foreground"} />
              </button>
            );
          })}
          {results.length === 0 && <div className="rounded-md bg-secondary p-5 text-sm text-muted-foreground">Nenhuma sala encontrada. Verifique o código e tente novamente.</div>}
        </div>
        <div className="mt-5 flex items-start gap-3 text-sm leading-6 text-muted-foreground"><CircleHelp size={18} className="mt-0.5 shrink-0" /><p>Não sabe o código completo? Digite a letra do prédio e os primeiros números da sala.</p></div>
      </section>
      <div className="mx-auto mt-auto w-full max-w-xl pt-8"><Button onClick={onConfirm} disabled={!selected || results.length === 0} className="w-full">Confirmar sala <ChevronRight size={18} /></Button></div>
    </div>
  );
}

function RouteScreen({ room, floor, setFloor, zoom, setZoom, poi, setPoi, onBack }: { room: Room; floor: string; setFloor: (floor: string) => void; zoom: number; setZoom: (zoom: number) => void; poi: string; setPoi: (poi: string) => void; onBack: () => void }) {
  const filters = [{ label: "Banheiros", icon: Bath }, { label: "Entrada", icon: DoorOpen }, { label: "Mais", icon: MoreHorizontal }];
  return (
    <div className="flex min-h-screen flex-col sm:min-h-[calc(100vh-4rem)]">
      <header className="flex items-center justify-between border-b border-border px-4 py-4 sm:px-7">
        <Button variant="ghost" onClick={onBack} className="px-2"><ArrowLeft size={20} /><span className="hidden sm:inline">Voltar</span></Button>
        <div className="text-center"><p className="text-xs text-muted-foreground">Indo para</p><h1 className="font-display text-xl text-foreground">Sala {room.code}</h1></div>
        <div className="w-11 sm:w-20" />
      </header>
      <div className="relative min-h-[520px] flex-1 overflow-hidden bg-map">
        <CampusMap indoor zoom={zoom} />
        <div className="absolute left-4 top-5 flex flex-col gap-2 sm:left-6 sm:top-7">
          {["3", "2", "1", "T"].map((item) => <Button key={item} variant="floor" aria-label={`Andar ${item}`} aria-pressed={floor === item} onClick={() => setFloor(item)} className="size-11 p-0">{item}</Button>)}
        </div>
        <div className="absolute right-4 top-5 flex flex-col gap-2 sm:right-6 sm:top-7">
          <Button variant="icon" aria-label="Aumentar zoom" title="Aumentar zoom" onClick={() => setZoom(Math.min(1.2, zoom + 0.1))} className="size-11 p-0"><Plus size={19} /></Button>
          <Button variant="icon" aria-label="Diminuir zoom" title="Diminuir zoom" onClick={() => setZoom(Math.max(0.8, zoom - 0.1))} className="size-11 p-0"><Minus size={19} /></Button>
          <Button variant="icon" aria-label="Minha localização" title="Minha localização" className="size-11 p-0"><LocateFixed size={19} /></Button>
        </div>
        <div className="absolute bottom-4 left-1/2 w-[calc(100%-2rem)] max-w-xl -translate-x-1/2 rounded-md bg-card p-5 shadow-map sm:bottom-6">
          <div className="flex items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-route">Destino</p><h2 className="mt-1 font-display text-3xl text-foreground">Sala {room.code}</h2><p className="mt-1 text-sm text-muted-foreground">{room.building} · {room.floor}</p></div><div className="text-right"><strong className="font-display text-3xl text-primary">3 min</strong><p className="text-xs text-muted-foreground">a pé</p></div></div>
          <div className="mt-4 flex gap-2 border-t border-border pt-4 text-xs font-semibold text-foreground"><span className="flex items-center gap-2 rounded-md bg-secondary px-3 py-2"><Footprints size={16} /> 1 lance</span><span className="flex items-center gap-2 rounded-md bg-secondary px-3 py-2"><Accessibility size={16} /> Elevador</span></div>
        </div>
      </div>
      <nav className="flex items-center justify-center gap-2 border-t border-border bg-background px-3 py-3" aria-label="Pontos de interesse">
        <span className="mr-1 hidden text-xs font-bold text-muted-foreground sm:inline">Mostrar</span>
        {filters.map(({ label, icon: Icon }) => <Button key={label} variant={poi === label ? "primary" : "soft"} onClick={() => setPoi(label)} className="min-w-0 flex-1 px-3 sm:max-w-36"><Icon size={17} /><span className="truncate">{label}</span></Button>)}
        <Button variant="ghost" aria-label="Camadas do mapa" title="Camadas do mapa" className="size-11 px-0"><Layers3 size={19} /></Button>
      </nav>
    </div>
  );
}