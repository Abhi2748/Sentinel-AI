<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Sentinel-AI 2.0 – Cursor Build Specification

*Save this file as `SENTINEL_AI_2_0_SPEC.md` at the root of your repo so Cursor can index it.*

## 1  Feature-Freeze Baseline

The following capabilities **MUST ship exactly as described** in your original document. Any new ideas appear later as *optional extensions*.


| Category | Frozen Core Feature |
| :-- | :-- |
| Cost | 75% average cost reduction via real-time routing + prompt optimisation |
| Reliability | 99.9% uptime with automatic circuit breakers \& multi-provider fallbacks |
| Compliance | Full audit trail, request-level logging, GDPR--ready redaction |
| Routing | IntelligentRouter with ComplexityAnalyzer → ModelSelector → Router |
| Caching | 3-tier cache (L1 memory 1 GB 5 min -  L2 Redis 10 GB 1 h -  L3 Postgres 100 GB 24 h) |
| Budget | Hierarchical BudgetController (user → team → company) |
| Prompt | PromptOptimizer with ≥ 50% token reduction target |
| Metrics | Provider metrics, request metrics, cache hit rate, cost analytics |

## 2  High-Level Architecture (unchanged)

```
Client SDK / REST / LangChain
            │
┌────────────┤ API Gateway ├────────────┐
│  Auth • Rate-Limit • Trace • JWT      │
└───────┬───────────────────────────────┘
        │
┌────────────┐ Intelligent Routing ┌────────────┐
│ QueryAnalyzer → ComplexityScorer │
│ ModelSelector → Router → Fallback │
└───────┬───────────────────────────┘
        │
┌──────────────┐ Provider Managers ┌──────────────┐
│ OpenAI • Anthropic • Groq • Local │
└───────┬───────────────────────────┘
        │
┌────────────┐ Data Layer ┌─────────┐
│ L1 • L2 • L3 Cache       │
│ Postgres + Analytics     │
└────────────┴─────────────┘
```


## 3  Project Directory Layout

```
sentinel-ai/
├── README.md
├── SENTINEL_AI_2_0_SPEC.md      ← this file
├── .cursorrules
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI routes
│   │   ├── core/                # core logic
│   │   │   ├── router.py
│   │   │   ├── complexity.py
│   │   │   ├── providers.py
│   │   │   ├── prompt_opt.py
│   │   │   ├── budget.py
│   │   │   └── cache.py
│   │   ├── models/              # Pydantic schemas & ORM
│   │   └── services/            # helpers
│   ├── db/                      # migrations & schema.sql
│   └── tests/
├── frontend/                    # React 18 + Vite
├── sdk/
│   ├── python/
│   └── javascript/
├── ml/                          # future ML enhancements
└── infrastructure/              # Docker & K8s
```


## 4  Blueprint-Level Code Stubs

Cursor will fill in the TODOs.

### 4.1  `backend/app/core/router.py`

```python
"""
IntelligentRoutingEngine
Keeps cost, reliability and compliance guarantees.
"""

from .complexity import ComplexityAnalyzer
from .providers   import ProviderRegistry
from .cache       import CacheManager
from .budget      import BudgetController
from .prompt_opt  import PromptOptimizer

class IntelligentRouter:
    def __init__(self):
        self.analyzer  = ComplexityAnalyzer()
        self.registry  = ProviderRegistry()
        self.cache     = CacheManager()
        self.budget    = BudgetController()
        self.optimizer = PromptOptimizer()

    async def route_request(self, request: AIRequest) -> AIResponse:  # TODO: define AIRequest
        # 1. Optimise prompt
        optimised_prompt = self.optimizer.optimise(request.prompt)

        # 2. Check budget
        auth = await self.budget.check_authorization(request)
        if not auth.approved:
            return AIResponse(error="Budget exceeded", success=False)

        # 3. Try cache
        if cached := await self.cache.lookup(optimised_prompt):
            return cached

        # 4. Analyse complexity & pick provider
        score = self.analyzer.analyse(optimised_prompt)
        decision = self.registry.select(score, request.requirements)

        # 5. Execute with fallbacks (circuit breaker inside)
        response = await decision.execute_chain(optimised_prompt)

        # 6. Store cache & metrics
        await self.cache.store(optimised_prompt, response)
        return response
```

*(similar stubs for other core modules)*

## 5  Database Schema Starter (`backend/db/schema.sql`)

Contains your original tables **unchanged**. Add the following two extra columns only to aid Cursor queries; everything else stays as in the PDF.

```sql
ALTER TABLE requests
  ADD COLUMN prompt_embedding VECTOR(384),
  ADD COLUMN cache_hit_level VARCHAR(10);
```


## 6  `.cursorrules`

```yaml
# Cursor code-generation preferences
project_name: Sentinel-AI 2.0
backend:
  language: python@3.11
  framework: fastapi
  async: true
frontend:
  language: typescript@5
  framework: react
style:
  python_lint: ruff
  typing: mypy
  docstrings: google
patterns:
  - clean-architecture
  - dependency-injection
tests:
  framework: pytest
security:
  - validate_inputs
  - never_log_pii
prompts:
  default_temperature: 0.2
```


## 7  Cursor AI Usage Guide

### 7.1  Bootstrapping

1. `git clone` the repo and open the folder in **Cursor**.
2. Cursor indexes `SENTINEL_AI_2_0_SPEC.md` and `.cursorrules`.
3. When prompted, run “Install recommended Python/Node dependencies”.

### 7.2  Generating Code

| Task | Example Prompt (in Cursor chat) |
| :-- | :-- |
| Create new FastAPI route | “Generate CRUD endpoints for `/v1/teams` in `@backend/app/api/teams.py` using existing patterns.” |
| Flesh out stub | “Complete logic in `@backend/app/core/cache.py` to support 3-layer cache as per spec.” |
| Tests | “Write pytest cases for `@backend/app/core/budget.py` covering limit breach.” |
| Refactor | “Refactor `@providers.py` to use adapter pattern; keep API unchanged.” |
| Docs | “Generate OpenAPI description for all routes under prefix `/v1`.” |

### 7.3  Daily Loop

1. Draft feature prompt → Cursor generates code.
2. Review + edit ↔ ask Cursor for small fixes.
3. Run `pytest -q` in integrated terminal.
4. Commit with Cursor-suggested message.

## 8  Optional Extensions (keep core intact)

You may ask Cursor to implement these **after** MVP ships.


| Extension | Why \& When |
| :-- | :-- |
| Semantic cache with pgvector | +15% hit rate once ≥ 50 k requests stored |
| ML-based provider predictor | Needed when >3 providers + large traffic |
| Edge deployment support | Adds offline selling point for regulated clients |

## 9  Sprint-0 Checklist

- [ ] Scaffold repo with folders above
- [ ] Add this spec \& `.cursorrules`
- [ ] Cursor prompt: “Generate FastAPI boilerplate with health check route.”
- [ ] Commit \& push → ensure CI (GitHub Actions) green

You now have a **single importable document** that preserves every original product feature while giving Cursor AI crystal-clear instructions to generate the codebase. Open the project in Cursor and start prompting. Happy building!

<div style="text-align: center">⁂</div>

[^1]: system-design-document.pdf

