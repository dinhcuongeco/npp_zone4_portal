# MASTER STATE & CONTEXT PROTOCOL
## NPP Dashboard Portal — Architectural Source of Truth

> **Document Type**: Master State & Context Protocol (MSCP)
> **Audience**: Future Claude Opus sessions inheriting this project
> **Authority Level**: BINDING — Decisions logged here cannot be reversed without explicit user re-negotiation
> **Last Architect Sign-Off**: 14/06/2026
> **Architecture Class**: `Single-File HTML SPA · Client-Side · Inline Data Bundle`

---

### ⚠️ ARCHITECTURAL FRAMING (Read First)

Dự án này KHÔNG dùng SPA framework (React/Vue/Angular), KHÔNG có URL routing, KHÔNG có state store như Zustand/Redux. Toàn bộ là **một file HTML duy nhất** với:
- Data nhúng inline (`const DATA = [...]`)
- Global mutable state qua JavaScript closure variables
- DOM manipulation thủ công (vanilla JS, không virtual DOM)
- sessionStorage cho persistence (thay vì URL state)

Khi document này nói "Component" → nghĩa là một **logical section** trong HTML (ví dụ `#tipCenter`).
Khi nói "Producer/Consumer" → nghĩa là **function** đọc/ghi vào global state.
Khi nói "Props" → nghĩa là **arguments** truyền vào render function.

Future sessions cần đề xuất framework migration phải **đề xuất explicit** và chờ user approve — không tự ý refactor.

---

## 1. COMPONENT ARCHITECTURE & STATE MATRIX

### 1.1 File System Tree

```
Project Root (cloud-managed):
├── /mnt/user-data/uploads/
│   └── allocation.xlsx                  [SOURCE DATA — sheet 'vdo']
│
├── /home/claude/                        [BUILD WORKSPACE]
│   ├── npp_portal.html                  [HTML template with __DATA__ / __CREDS__ placeholders]
│   ├── rows.json                        [Serialized DATA — 3070 outlets]
│   ├── creds.json                       [Serialized CREDS — 9 NPP credentials]
│   └── (build script: Python inline replace)
│
└── /mnt/user-data/outputs/              [DELIVERABLES]
    ├── NPP_Portal.html                  [⭐ PRODUCTION — single-file bundle, ~1.25MB]
    ├── PROJECT_MEMORY.md                [Narrative context document]
    ├── SESSION_HANDOFF.md               [Engineering handoff v1]
    ├── MASTER_STATE_PROTOCOL.md         [THIS FILE — architectural source of truth]
    ├── NPP_Portal_V2.html               [Alternative editorial theme — NOT current]
    ├── Scorecard_NPP.html               [Admin multi-NPP view — NOT NPP-facing]
    ├── Dashboard_NPP_TuCapNhat.html     [Drag-drop alternative — legacy reference]
    ├── VDO_13_6_updated.xlsx            [Excel with merged columns]
    ├── Huong_Dan_Su_Dung_Dashboard.docx [End-user guide]
    └── Huong_Dan_PowerQuery_NPP.docx    [Power Query alternative path]
```

### 1.2 Logical Component Tree (within `NPP_Portal.html`)

```
NPP_Portal.html
│
├── <Style Sheet>                        [~880 lines CSS, design tokens at root]
│
├── <Login Overlay>                      #loginPage
│   ├── <LoginBanner>                    .login-banner
│   ├── <LoginCard>                      .login-card
│   │   ├── <LoginEmblem>                .login-emblem (SVG Heineken-inspired star)
│   │   ├── <LoginForm>                  #loginForm
│   │   │   ├── input#userIn             [type: text, autocomplete: username]
│   │   │   ├── input#passIn             [type: password, autocomplete: current-password]
│   │   │   └── button.login-btn         [type: submit]
│   │   └── <LoginError>                 #loginError
│   └── <LoginFoot>                      .login-foot
│
└── <Dashboard>                          #dashPage  [hidden until login success]
    │
    ├── <TopBar>                         header.top
    │   ├── <Brand>                      .top-brand
    │   ├── <PeriodStrip>                .top-period [T6/2026 · 13/30 · Time gone 43.3%]
    │   └── <UserInfo>                   .top-user
    │       ├── #userName / #userMeta / #userAvatar
    │       └── #logoutBtn
    │
    ├── <Welcome>                        .welcome
    │   └── h1#welcomeName               [NPP fullname + (code) injected at login]
    │
    ├── <KPI Strip>                      .kpis  [5 cards horizontal]
    │   ├── .kpi.k1 #kTotal              [Total outlets]
    │   ├── .kpi.k2 #kAso #kAsoBadge     [ASO count + pass/fail badge]
    │   ├── .kpi.k3 #kTip                [TIP outlet count]
    │   ├── .kpi.k4 #kAch                [Achieved target count]
    │   └── .kpi.k5 #kPace               [On-pace count]
    │
    ├── <ASO Action Banner>              #asoBanner  [pass/fail variant via class]
    │   ├── .ab-ico                      [⚠ or ✓]
    │   ├── .ab-tx                       [Title + Description]
    │   └── button#abCta                 [→ triggers F.aso='no' + scrollTo table]
    │
    ├── <TIP Module>                     #tipCenter (section.tip-module)
    │   ├── <TM-Head>                    .tm-head [eyebrow + h2 "Tiến độ TIP"]
    │   ├── <TM-Hero>                    .tm-hero [grid 2-col]
    │   │   ├── <Focus>                  .tm-focus
    │   │   │   ├── #focusNum            [Hero: outlets still needing target]
    │   │   │   ├── #focusDesc
    │   │   │   └── <ProgressBar>        #fpFill / #fpPct / #fpAchN / #fpRemainV
    │   │   └── <Breakdown>              .tm-breakdown [2x2 grid of .bd-card]
    │   │       ├── .bd-card[data-bucket="achieved"]  #bdAchN #bdAchPct
    │   │       ├── .bd-card[data-bucket="onpace"]    #bdPaceN #bdPacePct
    │   │       ├── .bd-card[data-bucket="lagging"]   #bdLagN #bdLagPct
    │   │       └── .bd-card[data-bucket="noactive"]  #bdNoN #bdNoPct
    │   └── <TM-Priority>                .tm-priority
    │       └── #priList                 [Top 8 rendered as .pri-row]
    │
    ├── <Channel Mix Module>             #channelModule (section.ch-module)
    │   ├── <CH-Head>                    .ch-head + #chStatusPill
    │   ├── <CH-Hero>                    .ch-hero [grid 2-col]
    │   │   ├── <Focus>                  .ch-focus
    │   │   │   ├── #chFocusNum / #chFocusPct / #chFocusDesc
    │   │   │   └── <Gauge>              #chGaugeFill [KPI 65% marker line]
    │   │   └── <Donuts>                 .ch-donuts [grid 2-col]
    │   │       ├── svg#donutVol         [Volume breakdown donut]
    │   │       └── svg#donutOut         [Outlet count breakdown donut]
    │   └── <CH-Recs>                    .ch-recs
    │       └── #chRecGrid               [3 .ch-rec cards — context-aware tier]
    │
    ├── <Outlet Detail Table>            .panel.tblpanel
    │   ├── <Filter Chips>               .chips
    │   │   ├── select#fAso              [yes/no/empty]
    │   │   ├── select#fType
    │   │   ├── select#fProg
    │   │   ├── select#fStatus           [achieved/onpace/lagging/noactive]
    │   │   └── select#fSR
    │   ├── input#search
    │   ├── button#exportBtn
    │   └── table.outlets
    │       ├── thead [10 columns, click-to-sort]
    │       └── tbody#outletBody         [max 300 rows visible]
    │
    ├── <Split Panel>                    .grid2
    │   ├── <TypeList>                   #typeList
    │   └── <Recap>                      #recap
    │
    └── <Meta Bar>                       .meta-bar [load time, total rows]
```

### 1.3 State Matrix

| State Variable | Type | Default | Producer (Writes) | Consumer (Reads) | Persistence |
|---|---|---|---|---|---|
| `DATA` | `Outlet[]` (frozen) | embedded JSON | Build-time inline | All render fns, filtered(), tryLogin() | Inline in HTML |
| `CREDS` | `Record<string,string>` (frozen) | embedded JSON | Build-time inline | tryLogin() | Inline in HTML |
| `CURRENT` | `CurrentSession` | `{code:'',npp:'',area:'',rows:[]}` | tryLogin(), enterDash(), logoutBtn.click | All render fns, filtered(), exportCSV() | sessionStorage (key+pass only) |
| `F` | `FilterState` | `{type:'',prog:'',status:'',sr:'',aso:''}` | Filter chip change events, abCta.click, bd-card.click, resetBtn.click | filtered() | None — session-bound |
| `search` | `string` | `''` | #search input event, priority row click | filtered(), renderTable() | None |
| `sortK` | `string` (column key) | `'actual'` | thead th.click | renderTable() | None |
| `sortDir` | `1 \| -1` | `-1` | thead th.click | renderTable() | None |
| `sessionStorage['npp_session_v2']` | `JSON({u,p})` | absent | loginForm.submit | Boot script (try restore) | Browser session |
| `META` (deprecated, V2 only) | `{loadedAt, files}` | `{}` | buildData() in dash_live | render() in dash_live | localStorage in V2 file |
| `legendOff` (deprecated, ASO_Program only) | `Set<string>` | new Set() | legend item click | renderDonut() | None |

### 1.4 State Mutation Rules (BINDING)

**Single Source of Truth principle:**
- `CURRENT.rows` is **derived** from `DATA` (filtered by nppCode) at login time. Never mutate `DATA`.
- `F` is **flat** (no nested objects). Adding new filter dimension = adding new top-level key.
- `search`, `sortK`, `sortDir` are **NOT** part of `F` because they have different reset semantics (search keeps text input value; F is reset by chip dropdowns).

**No URL state** — explicit decision (see ADR-003). All ephemeral state is in memory; only `{u,p}` persists across page reload.

---

## 2. DATA CONTRACTS

### 2.1 Primary Domain Types

```typescript
/**
 * Outlet — the atomic unit of analysis.
 * Source: allocation.xlsx sheet 'vdo' (3070 rows).
 * After build: serialized into rows.json, inlined as `const DATA`.
 * IMMUTABLE post-build.
 */
interface Outlet {
  id:        number;       // = MAAN8 (8-digit outlet code, unique within Vietnam)
  name:      string;       // Customer_Name
  addr:      string;       // Outlet_Address (may be empty string, never null)
  area:      AreaName;     // Area_Name (3 possible values)
  nppCode:   NPPCode;      // code npp — LOGIN KEY (case-insensitive match)
  npp:       string;       // ParentName with "<code>-" prefix STRIPPED via regex /^[^-]*-/
  terr:      string;       // TerritoryName
  ss:        string;       // SS_FullName, prefix stripped
  sr:        string;       // SR_FullName, prefix stripped
  type:      OutletType;   // Loại outlet — used for Direct/Indirect classification
  program:   ProgramName;  // Chương trình — 'Target Incentive' = TIP eligibility marker
  target:    number;       // Chỉ tiêu kỳ (number of cases/thùng), >= 0
  actual:    number;       // Thực tế đã bán, >= 0
  pct:       number;       // Computed: actual/target (may be 0 if target=0)
  balance:   number;       // target - actual (may be negative if over-achieved)
}

type AreaName = 'HCM 9' | 'South 12' | 'South 26';

type NPPCode =
  | 'HMcc' | 'PC' | 'BD'
  | 'BD8' | 'BD10' | 'BD11' | 'BD12' | 'BD14' | 'BD16';

type OutletType =
  | 'Grocery Store'
  | 'Grocery Store with Home Delivery'
  | 'Sub Distributor'         // ⚠️ Định danh duy nhất cho Indirect channel
  | 'Quan Nhau Economy'
  | 'Quan Nhau Mainstream'
  | 'Quan Nhau Top'
  | 'Quan An'
  | 'Beverage Retail Store'
  | 'Beer Café'
  | 'Group Social'
  | 'Food Caterer'
  | 'Wholesaler'
  | '(Chưa phân loại)';      // Fallback cho null/empty

type ProgramName =
  | 'Target Incentive'        // ⚠️ ONLY this counts as TIP
  | 'Display 20 Small Outlet'
  | 'Display Small Outlet'
  | 'Display 30 Small Outlet'
  | 'Tie-up' | 'TPO' | 'SDIP'
  | 'No Program'
  | '(Không có)';             // Fallback cho null
```

### 2.2 Login & Session Contracts

```typescript
/**
 * CREDS — credentials map. Embedded inline.
 * Key = nppCode, Value = soldTo (numeric string, no spaces).
 */
type CredentialMap = Record<NPPCode, string>;

const CREDS: CredentialMap = {
  'HMcc': '10260146', 'PC':   '10461337', 'BD':   '10260266',
  'BD8':  '10260265', 'BD10': '10260260', 'BD11': '10260261',
  'BD12': '10260262', 'BD14': '10271817', 'BD16': '10309888'
};

/**
 * CurrentSession — derived from successful login.
 * Lifetime: from enterDash() until logoutBtn.click or tab close.
 */
interface CurrentSession {
  code: NPPCode | '';   // Logged-in NPP code; '' when not logged in
  npp:  string;         // Full NPP name (from rows[0].npp)
  area: AreaName | '';  // From rows[0].area
  rows: Outlet[];       // Filtered DATA where r.nppCode === code
}

/**
 * Session restoration payload.
 * sessionStorage key: 'npp_session_v2'
 * ⚠️ Key bump to v2 because previous schema differed.
 */
interface SessionPayload {
  u: string;  // Username typed (preserved exactly, not normalized)
  p: string;  // Password typed (preserved exactly)
}
```

### 2.3 Filter & Query Contracts

```typescript
/**
 * FilterState — orthogonal filter dimensions.
 * Empty string '' = "no filter on this dimension" (semantically OFF).
 * Never use null/undefined here — always string.
 */
interface FilterState {
  type:   string | OutletType;          // '' or exact type match
  prog:   string | ProgramName;          // '' or exact program match
  status: '' | BucketKey;                // Computed via statusOf()
  sr:     string;                        // SR full name (post-strip)
  aso:    '' | 'yes' | 'no';             // ASO active selling filter
}

type BucketKey = 'achieved' | 'onpace' | 'lagging' | 'noactive' | 'na';
```

### 2.4 Computed/Derived Types

```typescript
/**
 * Result of statusOf(outlet) — core classification logic.
 * Class names must match CSS: .s-achieved, .s-onpace, .s-lagging, .s-noactive, .s-na
 */
interface StatusResult {
  key:   BucketKey;
  label: string;          // Vietnamese display text
  cls:   `s-${BucketKey}`; // CSS class hook
}

/**
 * Priority row — extended outlet for TIP push-priority ranking.
 * Generated only inside renderTipCenter().
 */
interface PriorityRow extends Outlet {
  gap:     number;   // target - actual (always > 0 in priority list)
  pctDone: number;   // actual / target (always < 1 in priority list)
}

/**
 * RecommendationCard — for renderChannelMix() output cards.
 * Generated dynamically based on Direct % tier.
 */
interface RecommendationCard {
  cls: '' | 'warn' | 'bad';  // Visual variant (border-left color)
  ic:  string;                // 1-2 char icon (✓ ! ⚠ ★ → i etc.)
  ttl: string;                // ALL CAPS Vietnamese title
  dsc: string;                // Body — may contain <b> tags
}
```

### 2.5 Constants Contract (BINDING — DO NOT CHANGE WITHOUT ADR)

```typescript
const TIMEGONE: number = 13 / 30;           // 0.4333 — calendar-day based
const KPI_ASO: number = 0.93;                // ASO threshold
const KPI_DIRECT: number = 0.65;             // Direct sales threshold
const SUB_TYPE: OutletType = 'Sub Distributor';
const TIP_PROGRAM_NAME: ProgramName = 'Target Incentive';
const DAYS_LEFT: number = 30 - 13;           // 17 — months hard-coded for T6/2026
const STORAGE_KEY: string = 'npp_session_v2';
const MAX_VISIBLE_ROWS: number = 300;        // Table virtualization cap
const TOP_PRIORITY_N: number = 8;            // TIP priority list length
```

---

## 3. ARCHITECTURAL DECISIONS LOG (ADL)

> Mỗi decision dưới đây **BINDING**. Future sessions có thể đề xuất reversal nhưng phải explicit và chờ user approve. Không tự ý đảo logic.

### ADR-001 · Single-File Client-Side Architecture
- **Decision**: Toàn bộ dashboard là 1 file HTML self-contained (~1.25MB), không backend, không build pipeline phức tạp.
- **Alternatives considered**:
  - SPA framework (React + API) → tăng infra cost, cần devops
  - Power BI / Tableau → license cost cao, NPP cần training
  - Excel + Power Query → user đã có alternative này (đã build guide)
- **Why chosen**: NPP không phải dev. Email/Zalo gửi 1 file mở-là-chạy là UX tốt nhất. Hỗ trợ offline.
- **Consequences**: 
  - ✅ Zero infrastructure, gửi qua mọi kênh
  - ⚠️ Bảo mật yếu (data + creds trong source). Chỉ phù hợp distribution nội bộ.
  - ⚠️ Không thể realtime update — phải rebuild + redistribute mỗi kỳ

### ADR-002 · Data Embedded Inline (No Fetch)
- **Decision**: `const DATA = [...]` nhúng vào HTML lúc build, không có XHR/fetch.
- **Alternatives**: External JSON file fetched at runtime
- **Why**: External file = không chạy được trên `file://` protocol (CORS). NPP có thể mở local từ Downloads.
- **Consequences**: File size ~1.25MB. Acceptable. Rebuild khi data đổi.

### ADR-003 · sessionStorage > URL State > localStorage
- **Decision**: Login persistence dùng `sessionStorage`. Filter state KHÔNG persist ở đâu cả.
- **Alternatives**:
  - URL query params (e.g. `?aso=no&type=Grocery`) → người dùng có thể share link state
  - localStorage → persist across browser sessions
  - Cookies → server-readable (nhưng không có server)
- **Why sessionStorage cho login**: Tự động hết hạn khi đóng tab → bảo mật tốt hơn localStorage. Không cần explicit logout khi share máy.
- **Why không persist filter**: Mỗi session NPP mở dashboard là "fresh start" — bắt đầu xem toàn cảnh, không bị bias bởi filter cũ. Phù hợp work-pattern morning briefing.
- **Why không URL state**: NPP không share link cho nhau. Phức tạp hóa cho 0 benefit.

### ADR-004 · ASO Definition = Actual > 0 (not SEM_Status)
- **Decision**: ASO count = outlet với `actual > 0`. KHÔNG dùng `SEM_Status === 'Active'` flag từ VDO file gốc.
- **Why**: VDO file gốc đã filter sẵn `SEM_Status === 'Active'` (3070 rows are ALL active in system). Nhưng "active in system" ≠ "actually selling". User business intent = phát sinh doanh số → dùng `actual > 0`.
- **Edge case implication**: Một outlet với target=100, actual=1 vẫn count là ASO (đã có doanh số dù nhỏ).

### ADR-005 · TIP Narrow Scope = 'Target Incentive' Program Only
- **Decision**: TIP module CHỈ tính outlet với `program === 'Target Incentive'`. Không bao gồm Display, TPO, Tie-up, SDIP.
- **User confirmed**: Câu trả lời "Chỉ outlet trong Target Incentive (TIP đúng nghĩa)".
- **Implication**: Các module khác (KPI strip, Channel Mix) tính trên TẤT CẢ outlet, chỉ TIP module và priority list mới narrow.
- **Naming**: Eyebrow ghi "Target Incentive Program" (đã rename khỏi "Trade Investment Program" sai trước đó).

### ADR-006 · Time-Gone = Calendar Days 13/30
- **Decision**: TIMEGONE = 13/30 = 43.33% (calendar days của T6/2026).
- **Alternatives**:
  - Business days (loại Chủ nhật) → 11/26 ≈ 42.3%
  - Working days theo lịch nội bộ
- **Why calendar**: Đơn giản, user xác nhận. Phù hợp với pattern "outlet bán 7 ngày/tuần" của FMCG.

### ADR-007 · TIP Module — Editorial Layout (NOT War-Room Cards)
- **Decision**: Hero metric duy nhất + breakdown chips compact + priority list. KHÔNG dùng 4 gradient cards bão hòa.
- **History**: Iteration 1 dùng "war room" gradient cards lớn — user reject vì quá "ồn", "kindergarten poster".
- **Reference**: Stripe Dashboard, Linear, Notion editorial style.
- **Implication**: Mọi module phụ sau này phải tuân theo nguyên tắc: 1 hero metric/section, supporting metrics nhỏ hơn, action items rõ.
- **DO NOT REVERSE** without explicit user approval.

### ADR-008 · 4-Color Status Palette (Vibrant Gen-Z)
- **Decision**: 4 màu status fixed:
  - `#00C896` emerald — achieved / Direct positive
  - `#4F8BFA` sky — onpace / info
  - `#FFB020` amber — lagging / warning
  - `#FF6B5E` coral — noactive / critical
  - `#8B5CF6` purple — Indirect channel (neutral distinct)
- **Why**: User yêu cầu "năng động trẻ trung". Palette inspired bởi Linear, Vercel, Stripe.
- **DO NOT** revert sang traditional palette (red/yellow/green/blue saturated).

### ADR-009 · TIP Priority Ranking = Absolute Gap DESC
- **Decision**: Sort priority list by `(target - actual)` descending. Top 8.
- **Alternatives**:
  - Sort by gap × pctDone (favor warm leads) → user không yêu cầu, complexity tăng
  - Sort by absolute gap (chosen) → "biggest opportunities first"
- **Trade-off**: Cold outlets (actual=0, target lớn) có thể không phải easy win, nhưng chúng là cơ hội lớn nhất về volume. SR đến đó để **hiểu lý do** chưa bán.
- **Mitigation**: Mỗi priority row hiển thị `pctDone` + warmness class (cold/mid/warm) để SR tự đánh giá.

### ADR-010 · Channel KPI on Volume (Not Outlet Count)
- **Decision**: `direct_pct = volume_direct / total_volume`, KPI ≥ 65% áp dụng cho VOLUME.
- **Alternatives**: Direct outlet count % (sẽ luôn rất cao vì Sub Dist chỉ chiếm ~3.8% outlet)
- **Why volume**: Volume mới là điều business muốn balance. 4 outlet Sub có thể gánh 50% volume → KPI volume mới phát hiện được vấn đề này.
- **Phụ thuộc**: Vẫn show donut Outlet Count để minh họa sự lệch (asymmetry storytelling).

### ADR-011 · Full Re-Render on Filter Change
- **Decision**: Mọi filter change call `render()` → re-render TOÀN BỘ dashboard, không incremental.
- **Alternatives**: Targeted re-render (chỉ table và donut)
- **Why**: TIP/Channel metrics depend on `CURRENT.rows`, không phải `filtered()`. KPI strip cũng vậy. Vậy chỉ table+module phụ thuộc filtered nhưng nếu user filter theo SR, TIP module nên cập nhật theo (subset of NPP scope). 
- **⚠️ NOTE**: Hiện tại TIP và Channel render dùng `CURRENT.rows` (toàn NPP, KHÔNG filter). Đây là **chủ ý** — TIP/Channel là metrics ở scope NPP-level. Nếu future session muốn TIP filter theo SR/Territory, cần explicit user approval và update ADR.

### ADR-012 · Context-Aware Recommendations (3-Tier Threshold)
- **Decision**: Channel Mix recommendations sinh động theo ngưỡng:
  - `< 65%`: FAIL — 3 cards với cảnh báo + multiplier risk + actionable plan
  - `65-75%`: BORDERLINE — 3 cards "sát ranh, mong manh"
  - `≥ 75%`: STRONG — 3 cards ngợi khen + nhân rộng best practice
- **Why**: NPP không cần generic advice. Cùng dashboard, BD14 (52%) thấy "khẩn thiết", BD8 (84%) thấy "xuất sắc" — dashboard "suy luận thay user".
- **Pattern này phải apply** cho mọi module recommendation tương lai.

### ADR-013 · Tone of Voice — Advisory, NOT Imperative
- **Decision**: Vietnamese copy dùng tone cố vấn: "Cần hỗ trợ trong tuần", "Nên ưu tiên", "Có thể cứu được nếu hành động ngay".
- **REJECTED**: "URGENT", "PUSH NGAY!", "KÍCH HOẠT NGAY!", "Trạm chỉ huy".
- **Why**: User reject war-room style. NPP cao cấp không cần bị quát — họ cần information đẹp để ra quyết định bình tĩnh.
- **Applies to**: Mọi recommendation card, banner copy, empty state messages, error messages.

---

## 4. EDGE CASES & ERROR HANDLING

### 4.1 Login Path

| Case | Behavior | Code Location |
|---|---|---|
| Empty username/password | Form `required` attribute blocks submit | HTML form validation |
| Wrong username (no match in CREDS keys) | Show #loginError, shake animation, clear errors after 800ms | `tryLogin()` returns null |
| Right username, wrong password | Same as above | `CREDS[code] !== p.trim()` check |
| Right credentials but 0 matching outlets | tryLogin returns null (defensive) | `if(!rows.length) return null` |
| Case mismatch in username (`bd8` vs `BD8`) | Case-insensitive match via `.toLowerCase()` comparison | `Object.keys(CREDS).find(k => k.toLowerCase() === u.toLowerCase())` |
| Trailing space in password | `.trim()` applied | `CREDS[code] !== p.trim()` |
| Session restore with stale/invalid creds | tryLogin returns null → stays on login screen | Boot script wraps in try/catch |
| Multiple rapid submits | No debounce — relies on form natural submission | Acceptable for current scale |

### 4.2 statusOf() Edge Cases

```javascript
// Order of checks matters! Test sequence:
if (d.actual === 0) return 'noactive';   // [1] Zero sales — highest priority
if (d.target === 0) return 'na';          // [2] No target assigned (non-TIP)
if (d.actual >= d.target) return 'achieved'; // [3] Met/exceeded
if (d.actual/d.target >= TIMEGONE) return 'onpace';
return 'lagging';
```

| Case | Returned | Note |
|---|---|---|
| actual=0, target=0 | `noactive` | Check [1] hits first — "Chưa phát sinh" wins over "Không có Target" |
| actual=100, target=0 | `na` | Has sales but no target — likely a non-TIP outlet sold spontaneously |
| actual=target=100 (exact match) | `achieved` | `>=` includes equality |
| actual > target (over-achieve, e.g. 150/100) | `achieved` | No special bucket for over-achievers; visualization caps progress bar at 100% |
| Negative actual or target | Undefined behavior | Data contract assumes >= 0. Pre-build guard in Python (`.fillna(0)`). |

### 4.3 Aggregation Edge Cases

| Case | Handling |
|---|---|
| NPP has 0 TIP outlets | `renderTipCenter()` hides funnel, shows empty state "Chưa có outlet TIP" |
| NPP has 0 Sub Distributor outlets | Channel donut shows 100% Direct, no error |
| NPP has 0 total volume | `chFocusDesc = "Chưa có dữ liệu sản lượng"`, donut shows "—" empty state |
| Priority list empty (all achieved) | Shows celebration empty state "Hoàn thành toàn bộ" |
| All TIP outlets have target=0 | They're not classified as TIP semantically anyway (target=0 → 'na' bucket) |
| Division by zero in pct calculations | Guarded via `T ? cA/T : 0` pattern everywhere |
| `multiplier` (avgIndirect/avgDirect) when avgDirect=0 | `multiplier = 0`, recommendation skips multiplier line |

### 4.4 UI Robustness

| Case | Handling |
|---|---|
| Outlet name contains `<script>` or HTML | `esc()` function escapes `& < > "` before render |
| Outlet name extremely long | CSS `max-width: 220px; white-space: normal; line-height: 1.3` |
| Address > 80 chars in priority list | Substring + ellipsis: `${d.addr.substring(0,80)}${d.addr.length>80?'…':''}` |
| Empty SR/Territory | Fallback `'—'` via `(d.sr \|\| '—')` |
| Filter returns 0 rows | Table body shows `<tr><td colspan="10">Không có outlet nào khớp bộ lọc</td></tr>` |
| Filter returns > 300 rows | Render first 300 + footer note "Hiển thị 300 / X dòng đầu" |
| Sort on null/undefined values | `(x \|\| '')` and `(x \|\| 0)` patterns prevent NaN |
| Number with Vietnamese locale | `Math.round(n).toLocaleString('vi-VN')` for thousands separator |
| CSV export with comma/quote/newline in cell | Quote-escape via `if(/[,\n"]/.test(s)) s='"'+s+'"'`; BOM prefix `\ufeff` for Excel encoding |
| Progress bar with pct > 100% | CSS `width: ${Math.min(100, pct*100)}%` caps |
| Animate from 0 on first render | `countUp()` reads `el.dataset.curr || '0'` as starting point |

### 4.5 Browser/Environment

| Case | Behavior |
|---|---|
| Open via `file://` protocol | Works fully (no external resources) |
| Open in incognito/private mode | Works, but sessionStorage cleared on close (expected) |
| sessionStorage disabled (privacy mode) | Falls through silently — user re-logins each visit |
| JS disabled | Page shows but is non-functional (no graceful fallback — acceptable for internal tool) |
| Browser < ES6 (IE11) | NOT supported (uses arrow functions, template literals, optional chaining) |
| Screen < 700px | Mobile layout: kpis 2-col, ch-hero single col, hide some priority row columns |

### 4.6 Unhandled / Known Gaps

These are NOT currently handled — document for future awareness:

- **Concurrent logins same browser**: 2 tabs → second tab login overwrites sessionStorage. Acceptable.
- **Data updated mid-session**: User would need to refresh — no live-reload mechanism. Acceptable for FMCG cycle (weekly/monthly).
- **i18n**: Only Vietnamese. English fallback NOT implemented.
- **Print stylesheet**: Not specifically designed. Default print may look poor.
- **Accessibility (ARIA)**: Not audited. Has semantic HTML but no aria-labels on icons.
- **Keyboard navigation through priority list**: Click-only, no Tab + Enter handlers.

---

## 5. BOUNDARY HANDOVER FOR OPUS

### 5.1 Actionable Prompt — Paste at Start of Next Session

```
TÔI ĐANG TIẾP TỤC DỰ ÁN NPP DASHBOARD PORTAL.

Bạn là Principal System Architect kế thừa dự án. Trước khi action:

1. ĐỌC tài liệu MASTER_STATE_PROTOCOL.md (file này) — ĐÂY LÀ KHÁNG NGHỊ ARCHITECTURAL.
2. ĐỌC SESSION_HANDOFF.md để biết engineering state.
3. ĐỌC PROJECT_MEMORY.md để biết narrative context.
4. Mở NPP_Portal.html xem source thực tế.

TUYỆT ĐỐI KHÔNG được thay đổi:
- File `statusOf()` 5-tier bucket logic [ADR-007/009]
- Constants: TIMEGONE=13/30, KPI_ASO=0.93, KPI_DIRECT=0.65 [Section 2.5]
- CREDS structure và 9 NPP credentials [ADR-001]
- Định danh `SUB_TYPE = 'Sub Distributor'` cho Indirect [ADR-010]
- Định danh `TIP_PROGRAM_NAME = 'Target Incentive'` (KHÔNG đảo về 'Trade Investment') [ADR-005]
- 4-color status palette (#00C896 / #4F8BFA / #FFB020 / #FF6B5E / #8B5CF6) [ADR-008]
- Tone Vietnamese ADVISORY, không IMPERATIVE [ADR-013]
- FilterState interface flat structure [Section 2.3]
- sessionStorage key 'npp_session_v2' [ADR-003]

TASK ƯU TIÊN #1 (chưa làm — bắt đầu từ đây):
Implement "Super Premium Theme" — đã được user yêu cầu:
- Palette: đen sâu + xanh rừng + vàng champagne
- Typography: SERIF cho display (Playfair Display / Cormorant / DM Serif Display)
- SVG sản phẩm bia generic (chai/lon — KHÔNG dùng logo Heineken thật)
- Layout: one-page scrolling với section delineation rõ ràng
- Effect: fade-in mượt mà từng section khi scroll (IntersectionObserver)
- Feel: magazine cover, đẳng cấp, không "tech dashboard"

Approach gợi ý cho fade-in:
const io = new IntersectionObserver(entries => {
  entries.forEach(e => e.isIntersecting && e.target.classList.add('in-view'));
}, { threshold: 0.15 });
document.querySelectorAll('.section').forEach(s => io.observe(s));

.section { opacity:0; transform:translateY(24px); transition:all 1s cubic-bezier(.2,.7,.2,1); }
.section.in-view { opacity:1; transform:none; }

KHI HOÀN THÀNH:
- Tạo file mới (e.g. NPP_Portal_Premium.html) — KHÔNG ghi đè NPP_Portal.html hiện tại
- Cập nhật SESSION_HANDOFF.md (status mới)
- Cập nhật Section 2.2 của MASTER_STATE_PROTOCOL.md nếu thêm State/Component mới
- Thêm ADR mới nếu có decision logic mới

BẮT ĐẦU BẰNG: Xác nhận đã đọc 3 file documentation. Tóm tắt cho tôi state hiện tại + plan implement Super Premium theme.
```

### 5.2 Boundary Protection Rules

Future sessions phải tuân thủ:

**Rule 1 · State Matrix là Single Source of Truth**
Thêm biến state mới → MUST update Section 1.3 + define interface in Section 2 + cite in ADR.

**Rule 2 · Constants là BINDING**
Thay đổi TIMEGONE, KPI thresholds, etc. → MUST add new ADR explaining why + get user confirmation.

**Rule 3 · Type Contracts là FROZEN**
Đổi `Outlet` interface schema → MUST verify với data team rằng vdo sheet columns chưa đổi. Adding optional fields OK; removing/renaming required fields = breaking change.

**Rule 4 · Reject Patterns Stay Rejected**
War-room gradient cards, imperative tone, lặp thông tin (funnel+breakdown đồng thời) — ĐÃ REJECT — DO NOT propose again.

**Rule 5 · One Hero Per Module**
Mỗi module (TIP, Channel, future modules) chỉ có 1 hero metric. Supporting metrics nhỏ hơn rõ ràng. KHÔNG có 4 elements ngang nhau cạnh tranh attention.

**Rule 6 · Filter Triggers Full Render**
Filter change → `render()` re-renders all. KHÔNG implement incremental update (sẽ phá đồng nhất TIP/Channel scope).

**Rule 7 · Tone Vietnamese Advisory**
Mọi copy mới phải pass check: "Đây có phải giọng cố vấn không, hay đang quát?"

**Rule 8 · No External Dependencies Without ADR**
Self-contained là ADR-001. Thêm CDN/API/font external → MUST ADR + user approve.

### 5.3 Quick Reference — Things You Almost Certainly Need

```javascript
// To filter outlets to current NPP scope:
CURRENT.rows.filter(d => d.program === TIP_PROGRAM_NAME)

// To classify an outlet:
const status = statusOf(outlet);  // {key, label, cls}

// To split Direct vs Indirect:
const isIndirect = outlet.type === SUB_TYPE;

// To check KPI pass:
const asoPass = (CURRENT.rows.filter(d => d.actual > 0).length / CURRENT.rows.length) >= KPI_ASO;

// To calculate gap to ASO KPI:
const gap = Math.max(0, Math.ceil(KPI_ASO * total) - asoCount);

// To trigger re-render after state change:
F.someKey = newValue;
render();  // ⚠️ ALWAYS call render(), not just renderTable()

// To scroll user to results after filter set:
document.querySelector('.tbl-scroll').scrollIntoView({ behavior: 'smooth', block: 'start' });
```

### 5.4 Build & Output Conventions

```bash
# Build workflow (Python inline replace)
SOURCE: /home/claude/npp_portal.html (with __DATA__ and __CREDS__ placeholders)
INPUT:  /home/claude/rows.json + /home/claude/creds.json
OUTPUT: /mnt/user-data/outputs/NPP_Portal.html

# To rebuild after edits:
python -c "
html=open('/home/claude/npp_portal.html').read()
data=open('/home/claude/rows.json').read()
creds=open('/home/claude/creds.json').read()
html=html.replace('__DATA__','const DATA='+data+';').replace('__CREDS__','const CREDS='+creds+';')
open('/mnt/user-data/outputs/NPP_Portal.html','w').write(html)
"
```

### 5.5 Documentation Update Protocol

Sau khi hoàn thành work:

1. **NPP_Portal.html** — file artifact mới
2. **SESSION_HANDOFF.md** — update Section 2 (CURRENT STATUS) move done items, set next priorities
3. **MASTER_STATE_PROTOCOL.md** — update:
   - Section 1.3 State Matrix (if new state)
   - Section 2 Data Contracts (if new interface)
   - Section 3 ADL (if new architectural decision)
   - Section 4 (if new edge cases discovered)
   - Section 5.1 Actionable Prompt (update next task)
4. **PROJECT_MEMORY.md** — KHÔNG cần update thường xuyên (narrative ổn định)

---

## 📌 SIGN-OFF

This protocol is the **architectural contract** between the human user and AI sessions working on this project. Any deviation requires explicit re-negotiation.

**Document integrity check**: Before making changes, verify this file's last-modified date and last-architect sign-off. If unsure whether changes are within scope, ASK user before proceeding.

---

**Architecture Class**: `Single-File HTML SPA · Client-Side · Inline Data Bundle`
**Version**: 1.0 (14/06/2026)
**Supersedes**: SESSION_HANDOFF.md sections related to architecture (handoff doc remains valid for engineering state, this doc binds architectural decisions)

> **END OF PROTOCOL.**
