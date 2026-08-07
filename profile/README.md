```text
███████╗███████╗███╗   ███╗██╗   ██╗███████╗ ██████╗
██╔════╝██╔════╝████╗ ████║██║   ██║██╔════╝██╔════╝
███████╗█████╗  ██╔████╔██║██║   ██║█████╗  ██║
╚════██║██╔══╝  ██║╚██╔╝██║╚██╗ ██╔╝██╔══╝  ██║
███████║███████╗██║ ╚═╝ ██║ ╚████╔╝ ███████╗╚██████╗
╚══════╝╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚══════╝ ╚═════╝

  constant-cost semantic memory for LLM agents
  ──────────────────────────────────────────────
  turn 10 ........ same input footprint
  turn 10 000 .... same input footprint
```

[![PyPI](https://img.shields.io/pypi/v/semvec.svg?label=PyPI&color=blue)](https://pypi.org/project/semvec/)
[![Python versions](https://img.shields.io/pypi/pyversions/semvec.svg)](https://pypi.org/project/semvec/)
[![Docs](https://img.shields.io/badge/docs-semvec--docs.pages.dev-2ea44f.svg)](https://semvec-docs.pages.dev)
[![Website](https://img.shields.io/badge/web-semvec.io-black.svg)](https://www.semvec.io)
[![Patent applications pending](https://img.shields.io/badge/patents-applications%20pending-blue.svg)](https://www.semvec.io)

**Semvec** replaces unbounded conversation history with a **fixed-size semantic
state vector** plus a tiered, content-aware memory. The input cost of every LLM
call stays constant — and the agent still has structured access to decisions,
invariants, error patterns, and prior context across sessions.

Drop-in alternative to mem0, Letta, and LangChain Memory.

---

## The problem, in one picture

```text
  input tokens per turn

  full-context replay              semvec
  ───────────────────────────      ───────────────────────────
  turn 10      ▐█▌                 turn 10      ▐█▌
  turn 100     ▐████▌              turn 100     ▐█▌
  turn 1 000   ▐████████▌          turn 1 000   ▐█▌
  turn 10 000  ▐█████████████…     turn 10 000  ▐█▌

  O(n) — grows with history        O(1) — fixed-size state vector
```

Every other dedicated memory system on the LOCOMO leaderboard runs at least one
generative LLM pass per stored turn. Semvec runs **zero** — ingest is a
deterministic, in-process, sub-millisecond `state.update()`.

---

## How it works

```text
  conversation ──▶ your embedder ──▶ ┌─────────────────────────────┐
                  (bring your own)   │   semvec state (384-d/768-d)│
                                     │   ├── short-term tier       │
                                     │   ├── medium-term tier      │
                                     │   ├── long-term tier        │
                                     │   └── verbatim cache        │
                                     │       (IBANs, prices, IDs — │
                                     │        bit-exact, Decimal)  │
                                     └──────────────┬──────────────┘
                                                    ▼
                                    150–350-token context block
                                                    ▼
                                       any LLM system prompt
```

No API key. No base URL. No network round-trip. No telemetry.
The `semvec` package runs entirely in-process.

---

## Quick start

```bash
pip install semvec
```

```python
from semvec import SemvecState, SemvecConfig
from semvec.token_reduction import SemvecStateSerializer

state = SemvecState(config=SemvecConfig(dimension=768))
for text, embedding in conversation:      # bring your own embeddings
    state.update(embedding, text)         # deterministic, zero LLM calls

context = SemvecStateSerializer().serialize(state, query_text="what did we decide?")
# `context` is a 150–350-token block — paste it into any LLM system prompt.
```

Works as a plain library, a drop-in chat proxy for any OpenAI-compatible
endpoint (vLLM, LiteLLM, OpenRouter, Ollama), a REST API server
(`semvec serve`), an MCP server for Claude Code & Cursor, and a multi-agent
coordination layer (Cortex).

---

## Architectural differences vs. the field

This table compares **architectural properties**, not measured performance.

| Property | **semvec** | mem0 | Letta (MemGPT) | LangChain Memory |
|---|---|---|---|---|
| Per-turn input footprint | **O(1)** — fixed-size state | O(retrieved records) | O(in-context blocks) | buffer ≈ O(n); summary ≈ bounded |
| LLM calls during ingest | **0** | LLM fact-extraction per turn | LLM-managed page-in/out | varies by class |
| Recall procedure | deterministic (vector + literal cache) | LLM-extracted facts | LLM-managed swap | deterministic (when vector-based) |
| Exact values (IBANs, prices, dates) | **verbatim cache**, `Decimal` | embedded → lossy | embedded → lossy | not addressed |
| Multi-agent shared memory | **built-in (Cortex)**, checksummed | manual | manual | manual |

→ Deep dives: [vs mem0](https://semvec-docs.pages.dev/comparisons/vs-mem0/) ·
[vs Letta](https://semvec-docs.pages.dev/comparisons/vs-letta/) ·
[vs LangChain Memory](https://semvec-docs.pages.dev/comparisons/vs-langchain-memory/)

---

## Benchmarks — measured, with conditions

- **LOCOMO 10-conv (1986 QAs, gpt-4o, T = 0.0):** semvec BM25-hybrid +
  cross-encoder rerank scores **F1 0.495** including adversarial Cat 5
  (vs 0.469 dense-only, +2.6 pp). Rank **2 of 8** on the published LOCOMO
  leaderboard.
- **vs. mem0 on LOCOMO:** under the mem0 LLM-as-Judge prompt (verbatim),
  semvec clears mem0 by **~12 pp aggregate** (note: the mem0 paper excludes
  Cat 5; the LOCOMO paper does not). Wall-clock is **17× shorter**
  (2.77 h vs ~47 h on the same suite) — semvec issues zero LLM calls during
  ingest.
- **Token efficiency:** **~93 % fewer input tokens per turn** vs gpt-4-turbo
  full-context 128K (~1.5–2 k vs ~26 k) on the same LOCOMO config.

Every number ships with its condition, and the benchmark harness ships in the
wheel: `pip install "semvec[benchmarks,hybrid,api,mem0]"` +
`benchmarks/run_locomo.py` — verbatim judge prompt, exact dataset version.
We have not benchmarked head-to-head against Letta or LangChain Memory, so we
publish no numbers for them.

---

## What lives in this org

| Repository | What it is |
|---|---|
| [Semvec-neo4j-agent-integration](https://github.com/VersinoPsiOmega/Semvec-neo4j-agent-integration) | Persistent semantic memory for multi-agent LLM systems — semvec drift detection combined with Neo4j knowledge graphs. Reference implementation for regulated multi-agent workloads. |
| [claude-powerpoint-token-reduction](https://github.com/VersinoPsiOmega/claude-powerpoint-token-reduction) | Cutting the input-token bill of the Claude for PowerPoint add-in with semvec semantic memory behind a LiteLLM gateway. |

The semvec core is proprietary (self-hosted, air-gapped, or Versino-managed);
it ships as one wheel for Linux (glibc + musl), macOS, and Windows on
[PyPI](https://pypi.org/project/semvec/). Free Community tier included.

---

## Built for regulated workloads

```text
  ┌────────────────────────────────────────────────────────────┐
  │  deterministic replay ... bit-identical within a release   │
  │  GDPR Art. 17 ........... signed deletion certificates     │
  │  audit trail ............ append-only event store          │
  │  exact values ........... verbatim Decimal cache           │
  │  prompt injection ....... semantic-layer anchors           │
  │  telemetry .............. none                             │
  │  vendor ................. EU (Germany)                     │
  └────────────────────────────────────────────────────────────┘
```

Patent applications pending: EP 25 188 105 · EP 26 160 795 ·
US 19/269,195 · US 19/550,466.

---

## Where to go next

```text
  » website ......... https://www.semvec.io
  » documentation ... https://semvec-docs.pages.dev
  » install ......... pip install semvec
  » contact ......... https://www.semvec.io
```

<sub>Versino PsiOmega GmbH · Germany ·
[LinkedIn](https://www.linkedin.com/company/112781595)</sub>
