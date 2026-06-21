// オフィス（アイソメトリック／斜め見下ろしのドット絵風・サーバーコンポーネントでOK）
// 2:1 アイソメ投影。床/壁/窓/デスク+モニタ/着席キャラ/サーバーラック(LED点滅)/休憩室/本棚/観葉植物。
// データ連携: 役割色・稼働状態(完了/巡回中で画面点灯)を維持。

interface Staff {
  id: string
  name: string
  role: string
  status: string
}

// ── 役割カラー（本体 / 画面 / 髪） ──
const SEAT: Record<string, { body: string; screen: string; hair: string }> = {
  sora: { body: '#2f9bbd', screen: '#7fd0e6', hair: '#23303a' },
  erika: { body: '#3f72c9', screen: '#9ec3ff', hair: '#2a2233' },
  nana: { body: '#37a87c', screen: '#86e8c0', hair: '#26352b' },
  yui: { body: '#c79433', screen: '#ffe08a', hair: '#3a2c18' },
  aoi: { body: '#9b59c9', screen: '#d3a0ff', hair: '#2c2238' },
  sakura: { body: '#d2649e', screen: '#ffc4e0', hair: '#3a2230' },
}

// ── アイソメ投影 ──
const HW = 32 // タイル半幅
const HH = 16 // タイル半高
const OX = 430
const OY = 132
const P = (gx: number, gy: number, lift = 0): [number, number] => [
  OX + (gx - gy) * HW,
  OY + (gx + gy) * HH - lift,
]
const poly = (pts: [number, number][]) => pts.map((p) => `${p[0]},${p[1]}`).join(' ')
const lerp = (a: [number, number], b: [number, number], t: number): [number, number] => [
  a[0] + (b[0] - a[0]) * t,
  a[1] + (b[1] - a[1]) * t,
]

// ── 立方体（top=天面, right=右面(gx+w), front=手前面(gy+d)） ──
function Box({
  gx, gy, w, d, h, base = 0, top, right, front,
}: {
  gx: number; gy: number; w: number; d: number; h: number; base?: number
  top: string; right: string; front: string
}) {
  const tA = P(gx, gy, base + h)
  const tB = P(gx + w, gy, base + h)
  const tC = P(gx + w, gy + d, base + h)
  const tD = P(gx, gy + d, base + h)
  const gB = P(gx + w, gy, base)
  const gC = P(gx + w, gy + d, base)
  const gD = P(gx, gy + d, base)
  return (
    <g>
      <polygon points={poly([tB, tC, gC, gB])} fill={right} />
      <polygon points={poly([tD, tC, gC, gD])} fill={front} />
      <polygon points={poly([tA, tB, tC, tD])} fill={top} />
    </g>
  )
}

// ── 人物（着席 or 立ち） ──
function Person({
  gx, gy, body, hair, standing = false,
}: {
  gx: number; gy: number; body: string; hair: string; standing?: boolean
}) {
  const [x, y] = P(gx, gy)
  const bh = standing ? 34 : 26
  const bw = 22
  const headR = 11
  return (
    <g>
      <ellipse cx={x} cy={y} rx={15} ry={6} fill="#00000055" />
      <rect x={x - bw / 2} y={y - bh} width={bw} height={bh} rx={9} fill={body} />
      <rect x={x - bw / 2} y={y - bh} width={bw} height={Math.min(8, bh)} rx={9} fill="#ffffff22" />
      <circle cx={x} cy={y - bh - headR + 2} r={headR} fill="#e3b489" />
      <path
        d={`M${x - headR} ${y - bh - headR + 1} a${headR} ${headR} 0 0 1 ${headR * 2} 0 l0 -3 a${headR} ${headR} 0 0 0 ${-headR * 2} 0 z`}
        fill={hair}
      />
    </g>
  )
}

// ── デスク＋モニタ＋着席キャラ（名札は最前面レイヤーで別途描画） ──
function Workstation({ gx, gy, staff }: { gx: number; gy: number; staff: Staff }) {
  const c = SEAT[staff.id] ?? SEAT.sora
  const active = staff.status === '完了' || staff.status === '巡回中'
  return (
    <g>
      {/* 着席キャラ（デスクの奥＝先に描画して下半身を隠す） */}
      <Person gx={gx + 0.85} gy={gy + 0.05} body={c.body} hair={c.hair} />
      {/* デスク天板 */}
      <Box gx={gx} gy={gy} w={1.7} d={1.0} h={13} top="#b98a52" right="#8a6038" front="#75502f" />
      {/* モニタ（手前面=画面） */}
      <Box
        gx={gx + 0.35} gy={gy + 0.28} w={0.95} d={0.18} h={20} base={13}
        top="#11161d" right="#1a222c" front={active ? c.screen : '#33414f'}
      />
    </g>
  )
}

// ── 名札（名前だけ・キャラ頭上・最前面でまとめて描画） ──
function NameTag({ x, y, name, color }: { x: number; y: number; name: string; color: string }) {
  const w = name.length * 14 + 14
  return (
    <g>
      <rect x={x - w / 2} y={y - 16} width={w} height={16} rx={8} fill="#0d1016ee" stroke="#2b3340" />
      <text x={x} y={y - 4} textAnchor="middle" fontSize="11" fontWeight="bold" fill={color}>
        {name}
      </text>
    </g>
  )
}

// ── 観葉植物 ──
function Plant({ gx, gy }: { gx: number; gy: number }) {
  const [x, y] = P(gx, gy)
  return (
    <g>
      <ellipse cx={x} cy={y} rx={13} ry={5} fill="#00000055" />
      <path d={`M${x - 8} ${y} L${x - 6} ${y - 16} L${x + 6} ${y - 16} L${x + 8} ${y} Z`} fill="#8a5a3a" />
      <circle cx={x} cy={y - 24} r={13} fill="#3f7d4a" />
      <circle cx={x - 7} cy={y - 19} r={9} fill="#4c9159" />
      <circle cx={x + 7} cy={y - 20} r={9} fill="#356b41" />
    </g>
  )
}

export default function OfficeScene({ staff }: { staff: Staff[] }) {
  const byId = Object.fromEntries(staff.map((s) => [s.id, s]))
  const fb = (id: string): Staff => byId[id] ?? { id, name: id, role: '', status: '待機' }

  // 床グリッド 10x8
  const COLS = 10
  const ROWS = 8
  const tiles: JSX.Element[] = []
  for (let gx = 0; gx < COLS; gx++) {
    for (let gy = 0; gy < ROWS; gy++) {
      const wood = (gx + gy) % 2 === 0 ? '#8a6038' : '#7a5331'
      tiles.push(
        <polygon
          key={`${gx}-${gy}`}
          points={poly([P(gx, gy), P(gx + 1, gy), P(gx + 1, gy + 1), P(gx, gy + 1)])}
          fill={wood}
          stroke="#6a4729"
          strokeWidth={0.6}
        />,
      )
    }
  }

  // 壁（背面2枚）
  const WALLH = 120
  const rW = {
    gA: P(0, 0), gB: P(COLS, 0), tA: P(0, 0, WALLH), tB: P(COLS, 0, WALLH),
  }
  const lW = {
    gA: P(0, 0), gB: P(0, ROWS), tA: P(0, 0, WALLH), tB: P(0, ROWS, WALLH),
  }

  // 右奥の壁に窓
  const windows: JSX.Element[] = []
  for (let i = 0; i < 4; i++) {
    const u0 = 0.12 + i * 0.21
    const u1 = u0 + 0.13
    const top0 = lerp(rW.tA, rW.tB, u0)
    const top1 = lerp(rW.tA, rW.tB, u1)
    const winTop0: [number, number] = [top0[0], top0[1] + 26]
    const winTop1: [number, number] = [top1[0], top1[1] + 26]
    const winBot0: [number, number] = [top0[0], top0[1] + 80]
    const winBot1: [number, number] = [top1[0], top1[1] + 80]
    windows.push(
      <g key={i}>
        <polygon points={poly([winTop0, winTop1, winBot1, winBot0])} fill="#2d4a6b" stroke="#16212e" strokeWidth={2} />
        <polygon
          points={poly([winTop0, lerp(winTop0, winTop1, 0.5), lerp(winBot0, winBot1, 0.5), winBot0])}
          fill="#34577d"
        />
      </g>,
    )
  }

  // サーバーラック（右側）＋LED
  const racks: { gx: number; gy: number }[] = [
    { gx: 8.3, gy: 0.3 }, { gx: 8.3, gy: 1.25 }, { gx: 8.3, gy: 2.2 },
  ]
  const rackW = 0.75
  const rackD = 0.7
  const rackH = 50
  const serverEls: { sum: number; el: JSX.Element }[] = racks.map((r, ri) => {
    const tL = P(r.gx, r.gy + rackD, rackH)
    const tR = P(r.gx + rackW, r.gy + rackD, rackH)
    const bL = P(r.gx, r.gy + rackD, 0)
    const bR = P(r.gx + rackW, r.gy + rackD, 0)
    const leds: JSX.Element[] = []
    for (let row = 0; row < 5; row++) {
      for (let col = 0; col < 2; col++) {
        const u = 0.28 + col * 0.32
        const v = 0.14 + row * 0.16
        const top = lerp(tL, tR, u)
        const bot = lerp(bL, bR, u)
        const [lx, ly] = lerp(top, bot, v)
        const green = col === 0
        leds.push(
          <circle key={`${row}-${col}`} cx={lx} cy={ly} r={2} fill={green ? '#4ade80' : '#fbbf24'}>
            <animate
              attributeName="opacity"
              values={green ? '1;0.25;1' : '0.4;1;0.4'}
              dur={green ? '1.8s' : '2.4s'}
              begin={`${((ri * 5 + row) % 7) * 0.25}s`}
              repeatCount="indefinite"
            />
          </circle>,
        )
      }
    }
    return {
      sum: r.gx + r.gy,
      el: (
        <g key={`rack-${ri}`}>
          <Box gx={r.gx} gy={r.gy} w={rackW} d={rackD} h={rackH} top="#222b38" right="#161d27" front="#1a2230" />
          {leds}
        </g>
      ),
    }
  })

  // 休憩スペース（左手前）
  const lounge: { sum: number; el: JSX.Element } = {
    sum: 0.4 + 5.0,
    el: (
      <g key="lounge">
        <polygon points={poly([P(0.2, 4.4), P(2.2, 4.4), P(2.2, 6.4), P(0.2, 6.4)])} fill="#2a1a24" opacity={0.85} />
        <Box gx={0.35} gy={4.6} w={1.5} d={0.55} h={14} top="#b5713f" right="#8c5530" front="#7a4827" />
        <Box gx={0.35} gy={4.55} w={1.5} d={0.18} h={26} top="#c47e48" right="#8c5530" front="#7a4827" />
        <Box gx={0.7} gy={5.5} w={0.7} d={0.55} h={8} top="#3a2a32" right="#28191f" front="#221318" />
      </g>
    ),
  }

  // 本棚（左奥の壁沿い）
  const shelfBooks = ['#c94f4f', '#4f86c9', '#5ec98a', '#d2b24f', '#9b6ad2', '#4fc9c9']
  const bookshelf: { sum: number; el: JSX.Element } = {
    sum: 0.2 + 2.2,
    el: (
      <g key="bookshelf">
        <Box gx={0.05} gy={1.6} w={0.35} d={1.6} h={64} top="#5a3f28" right="#3f2c1c" front="#4a3422" />
        {shelfBooks.map((bc, i) => {
          const v = 0.12 + i * 0.13
          const top = lerp(P(0.05, 1.6, 60), P(0.05, 3.2, 60), v)
          return <rect key={i} x={top[0] - 9} y={top[1] - 2} width={9} height={9} fill={bc} />
        })}
      </g>
    ),
  }

  // ワークステーション
  const seats: { id: string; gx: number; gy: number }[] = [
    { id: 'sora', gx: 1.3, gy: 1.2 },
    { id: 'erika', gx: 3.5, gy: 1.2 },
    { id: 'nana', gx: 5.7, gy: 1.2 },
    { id: 'yui', gx: 2.4, gy: 3.4 },
    { id: 'aoi', gx: 4.6, gy: 3.4 },
  ]
  const seatEls = seats.map((s) => ({
    sum: s.gx + s.gy,
    el: <Workstation key={s.id} gx={s.gx} gy={s.gy} staff={fb(s.id)} />,
  }))

  // 社長サクラ（立ち・中央手前）
  const sakura = fb('sakura')
  const sakuraEl = {
    sum: 4.0 + 5.5,
    el: (
      <g key="sakura">
        <Person gx={4.0} gy={5.5} body={SEAT.sakura.body} hair={SEAT.sakura.hair} standing />
      </g>
    ),
  }

  // 観葉植物
  const plants = [
    { gx: 6.6, gy: 0.4 }, { gx: 0.4, gy: 7.3 }, { gx: 6.8, gy: 6.6 }, { gx: 9.2, gy: 4.0 },
  ].map((p) => ({ sum: p.gx + p.gy, el: <Plant key={`p-${p.gx}-${p.gy}`} gx={p.gx} gy={p.gy} /> }))

  // sum（奥行き）でソートして奥→手前に描画
  const movable = [...seatEls, ...serverEls, ...plants, lounge, bookshelf, sakuraEl].sort(
    (a, b) => a.sum - b.sum,
  )

  // 名札（キャラ頭上・最前面で重なり知らず）
  const labels = [
    ...seats.map((s) => {
      const [x, y] = P(s.gx + 0.85, s.gy + 0.05)
      return { x, y: y - 60, name: fb(s.id).name, color: (SEAT[s.id] ?? SEAT.sora).screen }
    }),
    (() => {
      const [x, y] = P(4.0, 5.5)
      return { x, y: y - 62, name: sakura.name, color: SEAT.sakura.screen }
    })(),
  ]

  return (
    <svg viewBox="40 0 800 520" className="w-full h-auto" role="img" aria-label="office">
      <rect x="40" y="0" width="800" height="520" fill="#0a0e1a" />

      {/* 壁 */}
      <polygon points={poly([rW.tA, rW.tB, rW.gB, rW.gA])} fill="#1b2230" />
      <polygon points={poly([lW.tA, lW.tB, lW.gB, lW.gA])} fill="#141a26" />
      <polygon points={poly([P(0, 0, 8), P(COLS, 0, 8), rW.gB, rW.gA])} fill="#0e1420" />
      <polygon points={poly([P(0, 0, 8), P(0, ROWS, 8), lW.gB, lW.gA])} fill="#0b101a" />
      {windows}

      {/* 床 */}
      {tiles}

      {/* 家具・人物（奥→手前） */}
      {movable.map((m) => m.el)}

      {/* 名札（最前面・名前のみ） */}
      {labels.map((l, i) => (
        <NameTag key={i} x={l.x} y={l.y} name={l.name} color={l.color} />
      ))}
    </svg>
  )
}
