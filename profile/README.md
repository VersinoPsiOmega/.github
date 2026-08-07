<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/VersinoPsiOmega/.github/main/profile/assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/VersinoPsiOmega/.github/main/profile/assets/hero-light.svg">
  <img alt="SEMVEC — constant-cost semantic memory for LLM agents. Many conversation streams converge into one fixed-size state vector, and a single steady line leaves it." src="https://raw.githubusercontent.com/VersinoPsiOmega/.github/main/profile/assets/hero-dark.svg" width="100%">
</picture>

[![PyPI](https://img.shields.io/pypi/v/semvec.svg?label=PyPI&color=1E4670&labelColor=0A1626)](https://pypi.org/project/semvec/)
[![Python](https://img.shields.io/pypi/pyversions/semvec.svg?color=1E4670&labelColor=0A1626)](https://pypi.org/project/semvec/)
[![Docs](https://img.shields.io/badge/docs-semvec--docs.pages.dev-1E4670?labelColor=0A1626)](https://semvec-docs.pages.dev)
[![Web](https://img.shields.io/badge/web-semvec.io-E8843C?labelColor=0A1626)](https://www.semvec.io)
[![Patents](https://img.shields.io/badge/patents-applications%20pending-1E4670?labelColor=0A1626)](https://www.semvec.io)

Semvec replaces unbounded conversation history with a **fixed-size semantic state
vector** plus a tiered, content-aware memory. The input cost of every LLM call stays
constant, and the agent keeps structured access to decisions, invariants, error
patterns, and prior context across sessions.

Drop-in alternative to mem0, Letta, and LangChain Memory.

<br>

## The curve everyone else is on

```text
   input tokens per turn

   full-context replay                    semvec
   ────────────────────────────────       ────────────────────────────────
   turn      10   ▐█▌                     turn      10   ▐█▌
   turn     100   ▐████▌                  turn     100   ▐█▌
   turn   1 000   ▐█████████▌             turn   1 000   ▐█▌
   turn  10 000   ▐████████████████…      turn  10 000   ▐█▌

   O(n) · grows with history              O(1) · fixed-size state vector
```

Every other dedicated memory system on the LOCOMO leaderboard runs at least one
generative LLM pass per stored turn. Semvec runs **zero**. Ingest is a deterministic,
in-process, sub-millisecond `state.update()`.

<br>

## What actually happens to a turn

```text
   conversation ──▶ your embedder ──▶ ┌────────────────────────────────┐
                    (bring your own)  │  semvec state · 384-d / 768-d  │
                                      │  ├── short-term tier           │
                                      │  ├── medium-term tier          │
                                      │  ├── long-term tier            │
                                      │  └── verbatim cache            │
                                      │      IBANs, prices, IDs        │
                                      │      bit-exact, Decimal        │
                                      └────────────────┬───────────────┘
                                                       ▼
                                          150–350-token context block
                                                       ▼
                                             any LLM system prompt
```

No API key. No base URL. No network round-trip. No telemetry. The `semvec` package
runs entirely in-process.

<br>

## Start

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
# `context` is a 150–350-token block. Paste it into any LLM system prompt.
```

Works as a plain library, a drop-in chat proxy for any OpenAI-compatible endpoint
(vLLM, LiteLLM, OpenRouter, Ollama), a REST API server (`semvec serve`), an MCP server
for Claude Code and Cursor, and a multi-agent coordination layer.

<br>

## Multi-agent memory that does not drift

<p align="center">
  <img src="https://raw.githubusercontent.com/VersinoPsiOmega/.github/main/profile/assets/cortex-drift.webp" alt="Several agent lanes feeding one converged state, with a drift signal branching off it" width="72%">
</p>

Cortex gives several agents one aggregated view, checksum-validated state vectors, and
a vote on proposals. Every `run()` returns four signals you can wire into alerting
rather than one opaque confidence number:

```python
def is_drift(result):
    if result.get("drift_detected"):
        return True
    return result["drift_score"] >= 0.35 and result["top_similarity"] <= 0.45
```

`drift_score` alone false-fires on long varied conversations. `top_similarity` alone
false-fires on adversarial paraphrasing. The AND-gate is what makes it wireable.

<br>

## Architectural differences

Architectural properties, not measured performance. The benchmarks below were run
head-to-head against mem0 only.

| Property | **semvec** | mem0 | Letta (MemGPT) | LangChain Memory |
|---|---|---|---|---|
| Per-turn input footprint | **O(1)**, fixed-size state | O(retrieved records) | O(in-context blocks) | buffer ≈ O(n); summary ≈ bounded |
| LLM calls during ingest | **0** | fact-extraction per turn | LLM-managed page-in/out | varies by class |
| Recall procedure | deterministic (vector + literal cache) | LLM-extracted facts | LLM-managed swap | deterministic when vector-based |
| Exact values (IBANs, prices, dates) | **verbatim cache**, `Decimal` | embedded, lossy | embedded, lossy | not addressed |
| Multi-agent shared memory | **built-in**, checksummed | manual | manual | manual |

Deep dives: [vs mem0](https://semvec-docs.pages.dev/comparisons/vs-mem0/) ·
[vs Letta](https://semvec-docs.pages.dev/comparisons/vs-letta/) ·
[vs LangChain Memory](https://semvec-docs.pages.dev/comparisons/vs-langchain-memory/)

<br>

## Benchmarks, with their conditions

**LOCOMO 10-conv, 1986 QAs, gpt-4o, T = 0.0.** Semvec BM25-hybrid with cross-encoder
rerank scores **F1 0.495** including adversarial Cat 5, against 0.469 for the
dense-only baseline. Rank **2 of 8** on the published LOCOMO leaderboard.

**Against mem0.** Under the mem0 LLM-as-Judge prompt, used verbatim, semvec clears mem0
by **~12 pp** at the aggregate level. The mem0 paper excludes Cat 5; the LOCOMO paper
does not. Wall-clock is **17× shorter**, 2.77 h against ~47 h on the same suite,
because semvec issues zero LLM calls during ingest.

**Token efficiency.** **~93 % fewer input tokens per turn** than gpt-4-turbo
full-context 128K on the same config, ~1.5–2 k against ~26 k.

The harness ships in the wheel. `pip install "semvec[benchmarks,hybrid,api,mem0]"` plus
`benchmarks/run_locomo.py`, verbatim judge prompt, pinned dataset version. We have not
benchmarked head-to-head against Letta or LangChain Memory, so we publish no numbers
for them.

<br>

## In this organization

| Repository | What it is |
|---|---|
| [**Semvec-neo4j-agent-integration**](https://github.com/VersinoPsiOmega/Semvec-neo4j-agent-integration) | Persistent semantic memory for multi-agent LLM systems. Semvec drift detection combined with Neo4j knowledge graphs, as a reference implementation for regulated multi-agent workloads. |
| [**claude-powerpoint-token-reduction**](https://github.com/VersinoPsiOmega/claude-powerpoint-token-reduction) | Cutting the input-token bill of the Claude for PowerPoint add-in with semvec semantic memory behind a LiteLLM gateway. |

The semvec core is proprietary and ships as one wheel for Linux (glibc and musl),
macOS, and Windows on [PyPI](https://pypi.org/project/semvec/). Self-hosted,
air-gapped, or Versino-managed. Free Community tier included.

<br>

## Built for regulated workloads

```text
   ┌──────────────────────────────────────────────────────────────┐
   │   deterministic replay   bit-identical within a release      │
   │   GDPR Art. 17           signed deletion certificates        │
   │   audit trail            append-only event store             │
   │   exact values           verbatim Decimal cache              │
   │   prompt injection       semantic-layer anchors, QUARANTINE  │
   │   embedder               yours, no default, no lock-in       │
   │   telemetry              none                                │
   │   vendor                 EU · Versino PsiOmega GmbH          │
   └──────────────────────────────────────────────────────────────┘
```

Patent applications pending: EP 25 188 105 · EP 26 160 795 · US 19/269,195 ·
US 19/550,466.

<br>

## Next

```text
   »  website          https://www.semvec.io
   »  documentation    https://semvec-docs.pages.dev
   »  install          pip install semvec
```

<sub>Versino PsiOmega GmbH · Germany ·
[LinkedIn](https://www.linkedin.com/company/112781595)</sub>
