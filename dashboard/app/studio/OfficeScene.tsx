// オフィス俯瞰シーン（SVG・サーバーコンポーネントでOK）
// 参考画像に寄せた: 木目フロア＋デスク(デュアルモニタ)＋着席キャラ＋休憩室/サーバ室/資料室/窓/観葉植物

interface Staff {
  id: string
  name: string
  role: string
  status: string
}

const SEAT: Record<string, { fill: string; screen: string }> = {
  sora: { fill: '#3aa6c9', screen: '#7fd0e6' },
  erika: { fill: '#3f72c9', screen: '#9ec3ff' },
  nana: { fill: '#3fb98a', screen: '#86e8c0' },
  yui: { fill: '#d2a23a', screen: '#ffe08a' },
  aoi: { fill: '#9b59c9', screen: '#d3a0ff' },
  sakura: { fill: '#d96aa6', screen: '#ffc4e0' },
}

function Plant({ x, y, s = 1 }: { x: number; y: number; s?: number }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <ellipse cx="0" cy="20" rx="14" ry="5" fill="#00000055" />
      <rect x="-8" y="6" width="16" height="14" rx="2" fill="#8a5a3a" />
      <circle cx="0" cy="0" r="13" fill="#3f7d4a" />
      <circle cx="-6" cy="4" r="9" fill="#4c9159" />
      <circle cx="6" cy="3" r="9" fill="#356b41" />
    </g>
  )
}

function Desk({ x, y, staff }: { x: number; y: number; staff: Staff }) {
  const c = SEAT[staff.id] ?? SEAT.sora
  const active = staff.status === '完了' || staff.status === '巡回中'
  return (
    <g transform={`translate(${x} ${y})`}>
      <ellipse cx="0" cy="96" rx="34" ry="11" fill="#00000055" />
      <g transform="translate(0 40)">
        <rect x="-22" y="0" width="44" height="40" rx="16" fill={c.fill} />
        <circle cx="0" cy="-6" r="15" fill="#caa57f" />
        <path d="M-15 -10 a15 15 0 0 1 30 0 z" fill="#3a2a20" />
      </g>
      <rect x="-58" y="-6" width="116" height="30" rx="5" fill="#b07f4e" />
      <rect x="-58" y="18" width="116" height="8" rx="3" fill="#8a6038" />
      {[-30, 8].map((mx) => (
        <g key={mx} transform={`translate(${mx} -34)`}>
          <rect x="0" y="0" width="40" height="26" rx="3" fill="#1c2530" />
          <rect x="3" y="3" width="34" height="20" rx="2" fill={active ? c.screen : '#33414f'} />
          <rect x="17" y="26" width="6" height="6" fill="#2a333d" />
        </g>
      ))}
      <g transform="translate(0 70)">
        <rect x="-52" y="0" width="104" height="18" rx="4" fill="#0d1016" stroke="#2b3340" />
        <text x="0" y="13" textAnchor="middle" fontSize="11" fill="#e6edf3">
          {staff.name}（{staff.role.split(' ')[0]}）
        </text>
      </g>
    </g>
  )
}

export default function OfficeScene({ staff }: { staff: Staff[] }) {
  const byId = Object.fromEntries(staff.map((s) => [s.id, s]))
  const fb = (id: string): Staff => byId[id] ?? { id, name: id, role: '', status: '待機' }

  return (
    <svg viewBox="0 0 1000 600" className="w-full h-auto" role="img" aria-label="office">
      <rect width="1000" height="600" fill="#0a0e1a" />

      <rect x="40" y="70" width="600" height="500" rx="10" fill="#161b26" />
      {[80, 250, 420, 520].map((wx) => (
        <g key={wx} transform={`translate(${wx} 86)`}>
          <rect width="120" height="58" rx="3" fill="#0e1622" stroke="#2a3445" />
          <rect x="4" y="4" width="54" height="50" fill="#2d4a6b" opacity="0.8" />
          <rect x="62" y="4" width="54" height="50" fill="#34577d" opacity="0.8" />
        </g>
      ))}
      <rect x="56" y="160" width="568" height="394" rx="6" fill="#7a5331" />
      {[200, 250, 300, 350, 400, 450, 500].map((ly) => (
        <line key={ly} x1="56" y1={ly} x2="624" y2={ly} stroke="#6a4729" strokeWidth="2" />
      ))}

      <g transform="translate(70 250)">
        <text x="22" y="-8" fontSize="11" fill="#8b94a3">資料室</text>
        <rect x="0" y="0" width="14" height="64" rx="2" fill="#5a3f28" />
        {['#c94f4f', '#4f86c9', '#5ec98a', '#d2b24f', '#9b6ad2', '#4fc9c9'].map((c, i) => (
          <rect key={i} x="2" y={3 + i * 10} width="10" height="8" fill={c} />
        ))}
      </g>

      <Desk x={185} y={230} staff={fb('sora')} />
      <Desk x={345} y={230} staff={fb('erika')} />
      <Desk x={505} y={230} staff={fb('nana')} />
      <Desk x={265} y={420} staff={fb('yui')} />
      <Desk x={445} y={420} staff={fb('aoi')} />

      <g transform="translate(360 350)">
        <ellipse cx="0" cy="34" rx="20" ry="7" fill="#00000055" />
        <rect x="-16" y="-6" width="32" height="40" rx="13" fill={SEAT.sakura.fill} />
        <circle cx="0" cy="-16" r="13" fill="#caa57f" />
        <path d="M-12 -22 l4 -8 l4 6 l4 -8 l4 8 z" fill="#ffd34d" />
        <g transform="translate(0 40)">
          <rect x="-46" y="0" width="92" height="18" rx="4" fill="#0d1016" stroke="#3a2230" />
          <text x="0" y="13" textAnchor="middle" fontSize="11" fill="#ffd0e6">サクラ（社長）</text>
        </g>
      </g>

      <rect x="660" y="70" width="300" height="500" rx="10" fill="#10141d" />

      <g transform="translate(680 110)">
        <text x="130" y="-2" textAnchor="middle" fontSize="11" fill="#8b94a3">休憩スペース</text>
        <rect x="0" y="8" width="260" height="180" rx="8" fill="#2a1a24" stroke="#5a2f45" />
        <rect x="24" y="40" width="120" height="36" rx="8" fill="#b5713f" />
        <rect x="24" y="120" width="120" height="36" rx="8" fill="#b5713f" />
        <rect x="170" y="64" width="60" height="20" rx="4" fill="#3a2a32" />
        <Plant x={228} y={150} s={0.8} />
      </g>

      <g transform="translate(680 360)">
        <text x="130" y="120" textAnchor="middle" fontSize="11" fill="#8b94a3">サーバ室</text>
        {[0, 1, 2].map((i) => (
          <g key={i} transform={`translate(${150 + i * 34} 30)`}>
            <rect width="26" height="78" rx="3" fill="#1a2230" stroke="#2b3340" />
            {[0, 1, 2, 3, 4].map((j) => (
              <g key={j}>
                <rect x="4" y={6 + j * 14} width="18" height="9" rx="1.5" fill="#0f1622" />
                <circle cx="8" cy={10.5 + j * 14} r="1.6" fill="#4ade80">
                  <animate attributeName="opacity" values="1;0.25;1" dur="1.8s" begin={`${((i * 5 + j) % 7) * 0.25}s`} repeatCount="indefinite" />
                </circle>
                <circle cx="13" cy={10.5 + j * 14} r="1.6" fill="#fbbf24">
                  <animate attributeName="opacity" values="0.4;1;0.4" dur="2.4s" begin={`${((i * 5 + j) % 5) * 0.3}s`} repeatCount="indefinite" />
                </circle>
              </g>
            ))}
          </g>
        ))}
      </g>

      <Plant x={70} y={120} s={0.9} />
      <Plant x={610} y={140} s={0.9} />
      <Plant x={120} y={540} s={1} />
      <Plant x={300} y={552} s={0.9} />
      <Plant x={470} y={548} s={1} />
      <Plant x={600} y={300} s={0.85} />
    </svg>
  )
}
