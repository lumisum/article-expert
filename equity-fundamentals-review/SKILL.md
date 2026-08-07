---
name: equity-fundamentals-review
description: 资深证券基本面与财报高级审读技能（Equity Fundamentals Review）。面向美股（SEC 10-K/10-Q）、A股（巨潮 CNINFO）等上市公司的财报、招股书、业绩电话会及公告，进行审计级研究判断。严格区分“事实、管理层表述、分析推理”，拆解商业模式、增长质量、现金流转换及竞争风险，输出带五色视觉信号系统（🟢🔴🟡🔵⚪）的专业研报。
---

# Equity Fundamentals Review

Produce an audit-ready research judgment, not a generic document summary. Separate reported fact, management assertion, and analyst inference at all times. Do not present investment advice, price targets, or certainty.

## Inputs and evidence

1. Identify the company, ticker, reporting period, document type, filing date, currency, and fiscal calendar.
2. Prefer primary sources in this order: regulatory filing or prospectus; official earnings release and presentation; official call transcript or recording. Treat secondary summaries only as leads.
3. For every material conclusion, retain an evidence pointer: document, section/page or timestamp, reporting period, and exact metric. Do not call a source missing until the retrieval ladder below is exhausted.
4. For financial comparisons, use comparable periods: quarterly versus same quarter last year, year-to-date versus prior year-to-date, and annual versus annual. Do not compare a quarter with a nine-month cumulative amount.
5. State whether figures are GAAP/IFRS or adjusted/non-GAAP. Reconcile adjusted figures when the filing provides a reconciliation.

## Default source routing

Use a source or document explicitly supplied by the user as the starting material, then verify material figures against the applicable official filing. When the user does not specify an information source, route by the requested listing:

- **U.S.-listed or SEC-reporting company:** use SEC EDGAR as the default primary source. Resolve the correct legal registrant and CIK, retrieve the requested or latest applicable `10-K`, `10-Q`, `20-F`, `40-F`, `8-K`, or `6-K` through the SEC submissions data or filing index, and open the filing's primary document. Use the issuer IR site for the matching earnings release, presentation, webcast, and prepared remarks.
- **Mainland A-share company:** use 巨潮资讯网（CNINFO）as the default primary source. Search by the exact stock code and issuer, select the original periodic report or announcement for the requested reporting period, and open or download the complete official PDF rather than an announcement list, summary, or media copy. Use the Shanghai, Shenzhen, or Beijing exchange disclosure page as a cross-check or fallback when needed.
- **Dual- or cross-listed company:** follow the listing and reporting regime named by the user. If the request is ambiguous, identify the legal entity and security before retrieval; do not silently mix an ADR filing, an A-share report, and an H-share report. Compare filings only when the accounting period and scope are genuinely comparable.
- **Other markets:** use the corresponding exchange or securities regulator as the default primary source, followed by the issuer IR site.

Do not ask the user for a public filing merely because no link was supplied. Infer the market from the ticker, exchange, security name, and filing form when unambiguous, then execute the corresponding default route.

## Reading workflow

### 1. Establish the business model

Read the business overview and prospectus risk disclosures first. Explain what the company sells, who pays, the revenue model, value-chain position, segment economics, geographic exposure, and the mechanisms that create or erode bargaining power.

### 2. Read the financial statements before the narrative

Extract revenue, gross profit, operating income, net income, operating cash flow, capital expenditure, free cash flow, cash, debt, receivables, inventory, share count, and stock-based compensation. Calculate only where inputs and definitions are disclosed. Flag accounting changes, acquisitions, disposals, impairments, one-off gains/losses, factoring, or working-capital distortions.

### 3. Read MD&A and notes for drivers

Identify the stated driver for each material change, then test whether the statements support it. Focus on volume/price/mix, segment revenue, unit economics, customer concentration, backlog/RPO, inventory, receivables, capital allocation, capacity, and margin bridge.

### 4. Read the call as a forward-looking evidence layer

Separate prepared remarks from Q&A. Extract guidance, demand indicators, supply constraints, pricing, competitive changes, capital allocation, and management answers that narrow or contradict prior statements. Label calls as management assertions unless corroborated.

### 5. Form the investment case and disconfirm it

Write a base thesis in one sentence. Then identify the two or three observable conditions that would invalidate it. Seek contrary evidence before assigning a conclusion. Do not turn high growth into a positive conclusion without testing durability, cash conversion, balance-sheet risk, and valuation context.

## Evidence retrieval ladder

Do not end a review with “need to fetch” or merely ask the user to supply a public document. Retrieve it before finalizing whenever tools permit.

1. Execute the default source route above. For SEC filings, use the structured submissions data or filing index and open the primary filing HTML, not XBRL XML, an unrelated exhibit, or a landing page. For A-share reports, open the complete original CNINFO PDF and confirm the stock code, issuer, reporting period, report type, disclosure date, currency, unit, and whether the report is audited.
2. Retrieve the matching earnings release, presentation, webcast/replay, and call transcript from the issuer investor-relations site and the same-day 8-K/6-K attachments. Search the issuer site by filing date, quarter, `results`, `earnings`, `webcast`, and `transcript`.
3. If API requests, direct fetches, or ordinary page extraction are blocked, incomplete, JavaScript-rendered, or trapped behind an intermediate page, use the available CDP/real-browser capability to visit the official site. Expand document lists, open the visible source document, and extract the rendered text, title, date, and source URL.
4. Use the browser only for the missing evidence after checking whether a purpose-built API, connector, or CLI can retrieve it. Never treat one failed URL, a JavaScript viewer, or an XBRL file as proof that the material is unavailable.
5. For a third-party/paywalled call transcript, seek the issuer webcast, prepared remarks, 8-K exhibit, and investor presentation first. Report the transcript as unavailable only after these official alternatives fail or do not exist; say exactly which sources were checked.
6. Record the market, default source, retrieval route, filing identifier or announcement metadata, and final document URL in the output. Label a gap `未公开披露` only when the applicable regulator or disclosure platform and issuer sources have both been checked; label it `访问受限` when it exists but cannot be legally or technically accessed.

## Senior-review tests

- **Growth quality:** Is growth volume-, price-, mix-, acquisition-, FX-, or accounting-driven? Is it broad across segments and customers?
- **Margin quality:** Is margin movement structural, cyclical, or temporary? Is it consistent with pricing, mix, utilization, and operating leverage?
- **Cash conversion:** Does operating cash flow support earnings after adjusting for working capital, capex, acquisitions, and stock-based compensation?
- **Balance sheet:** Could debt maturities, lease liabilities, inventory, receivables, customer concentration, or dilution constrain the thesis?
- **Competitive position:** What gives pricing power? What observable evidence would show share loss or technological displacement?
- **Management credibility:** Compare current guidance and language with prior disclosed outcomes; distinguish direct answers from evasions.
- **Industry read-through:** State which observation is company-specific and which can reasonably be generalized to peers. Never infer an industry trend from one company alone.

## Output contract

Read [the output template](references/research-output-template.md) before delivering a research result. Complete every section; use `未公开披露`、`访问受限` or `证据不足` rather than filling gaps with assumptions. Keep the executive conclusion short and place detailed tables below it.

Read [the metric guide](references/metric-dictionary.md) when classifying financial quality or deriving ratios. Preserve the source's original units and disclose all formulas.

## Visual signal system

Use the output template's visual labels so a reader can scan material positives and risks before reading the detail. Apply a label only to a specific, evidenced observation; do not color an entire company or investment conclusion.

- `🟢 **确认利好**` — disclosed fact supports growth quality, margin, cash conversion, competitive position, or a positive catalyst.
- `🔴 **确认风险**` — disclosed fact shows deterioration, balance-sheet pressure, dilution, concentration, competitive loss, or another thesis risk.
- `🟡 **待验证**` — management assertion, early signal, mixed evidence, or a conclusion requiring a next-period check.
- `🔵 **中性事实**` — relevant reported fact without a directional conclusion.
- `⚪ **证据缺口**` — material information is not public, is inaccessible, or cannot be compared reliably.

Use bold for the signal label and the affected metric, followed by one concise explanation and an inline source. When the output renderer supports safe inline color, pair green/red/amber/blue/gray with the matching icon; the icon and bold label are mandatory fallbacks. Never mark management guidance `确认利好` or `确认风险` until it is corroborated by reported data or clearly state it remains `待验证`.

## Communication rules

- Use Chinese unless the user requests otherwise; preserve company names and filing section names where helpful.
- Put dates beside every historical figure and label the fiscal period precisely.
- Cite a source inline for every non-obvious quantitative or strategic claim.
- Mark each statement as `事实`、`管理层表述`、or `分析判断` where confusion is likely.
- End with the next evidence required only after executing the evidence retrieval ladder; state the completed retrieval attempts and the exact reason for every remaining gap.
