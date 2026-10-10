# Plan: Boss Agent + Multistep Verification Upgrade

Status: proposed (not yet implemented)
Date: 2026-07-13

Goal: close the two unverified links in the ticket workflow's verification chain - (1) does the spec faithfully capture the original ask, and (2) does the delivered outcome actually match the intent behind the spec, not just its letter - and introduce a "boss" agent (Fable-tier) at the points where a whole-chain judgment earns its cost.

## 1. Where the verification chain has holes today

The pipeline verifies three links well and two not at all:

| Link | Today |
|---|---|
| spec -> plan | wf-planner (opus) + SPEC_GAPS feedback loop |
| plan -> diff | wf-reviewer (opus), acceptance criteria + test-quality bar |
| criteria -> behavior | wf-verifier runs real commands, evidence per criterion |
| **original ask -> spec** | **Nothing.** In `--linear` mode the spec persists with no human confirmation, and `UPDATE_DESCRIPTION` replaces the description - the original ask survives only in Linear's edit history, invisible to every downstream agent. |
| **outcome -> intent** | **Nothing.** Reviewer and verifier are both anchored on the acceptance criteria - the letter of the spec. If the criteria are weak or miss an implicit requirement, the whole loop goes green on work the ticket author would not accept. |

## 2. Spec fidelity gate in /wf-spec (highest leverage, cheapest)

Before step 5 (Persist), run one check comparing the original description + comments + user answers against the final spec, on three questions:

- **Coverage** - every requirement and constraint in the ask appears in the spec.
- **No invention** - everything in the spec traces to the ask, the answers, or repo facts, not the builder's imagination.
- **Criteria adequacy** - the acceptance criteria are testable and actually capture the intent (they are what the entire downstream loop anchors on).

On FAIL, re-spawn `wf-spec-builder` once with the findings; still failing -> park the ticket instead of persisting.

Design points:

- **Persist the original ask.** The spec should include a collapsed `## Original request` section. Without it, "does the outcome match the original ask" is unanswerable downstream because the ask no longer exists anywhere agents can read.
- Mandatory in `--linear` mode (no human confirms there); optional in inline mode (the human already reviews before writing).
- Model: Sonnet. This is a diff-of-intents check, not architecture.

## 3. Acceptance gate in the inner loop - where the boss agent earns its keep

Do NOT build the boss as a supervisor that watches every stage. That duplicates the orchestrator, re-derives context (violating the "context flows forward, never re-derived" invariant), and burns tokens on the majority of tickets that are fine.

Instead: a **final acceptance judge** inside `wf-runner`, after reviewer and verifier both PASS.

- **Input:** original ask + spec + plan GOAL + final diff + the verifier's evidence block. All forward-flowing artifacts - zero re-exploration, no tool loops.
- **Question:** "Would the person who wrote this ticket accept this outcome?" Catches letter-vs-spirit misses, hollow-but-green criteria, and scope that quietly narrowed during fix rounds.
- **Verdict:** `ACCEPT`, or a short `INTENT_GAP` list feeding one additional combined fix round (then re-run reviewer + verifier + acceptor together - a fix invalidates all three verdicts). Still gapped -> `NEEDS_HUMAN: acceptance`.
- **Model: Fable 5** - the one place it fits. The tiering doctrine is "opus for judgment, sonnet for execution"; a whole-chain intent judgment is the highest-judgment, lowest-volume call in the pipeline: one invocation per ticket, bounded input, last line before a PR goes outward. Everything else stays on its current tier.
- **Implementation home:** `wf-runner.md` only (loop policy lives there per the known-limitations note), which automatically covers both sequential and `--parallel` modes.
- **Prototype exists:** `wf-judge` is ~80% of this agent - same shape (score output against a rubric, binary verdict), just pointed at a live ticket instead of an eval case.

## 4. Optional third use of the boss: NEEDS_HUMAN triage

When `wf-runner` exhausts its 2 fix rounds, a Fable triage pass classifies before interrupting the human:

- Reviewer over-blocking (opus reviewers get picky) -> resolve autonomously.
- Flaky verify -> resolve autonomously.
- Genuine human decision -> surface it.

Build this only after sections 2 and 3 prove out. It reduces interrupts but adds a path where an agent overrides the reviewer, which needs a tight rubric so it does not become a rubber stamp for weakening the gate.

## 5. Guardrails that must hold

- **False-block budget.** Every new blocking gate adds latency and a new way to wrongly stall a good ticket. Keep both gates at the reviewer's bar ("high and precise"), one fix round each. Roll out advisory-first: run logging-only for a batch of tickets, inspect the verdicts, then flip to blocking.
- **Untrusted input rule extends to the boss.** It consumes ticket-derived text end to end; same rule as SPEC_GAPS - its output goes into run artifacts and data logs, never into agent instruction files. It never touches Linear or GitHub (single-owner boundaries hold).
- **The eval harness gates the change.** Before flipping anything on: add cases where the spec drifts from the ask, and where a diff meets every criterion but misses intent (e.g. criteria say "endpoint returns 200" while the ask wanted validation). Baseline, then `/wf-eval` gates the prompts like everything else. If the acceptance judge shares lineage with `wf-judge`, re-run `/wf-calibrate` after the split.

## 6. Cost analysis

Per-token prices (as of 2026-07):

| Model | Input $/1M | Output $/1M |
|---|---|---|
| Fable 5 | $10 | $50 |
| Opus 4.8 | $5 | $25 |
| Sonnet 5 | $3 ($2 intro through 2026-08-31) | $15 ($10 intro) |
| Haiku 4.5 | $1 | $5 |

The expensive agents in the pipeline today are expensive because of volume, not rate: wf-planner and wf-reviewer (both opus) run multi-step tool loops that can chew through 100-300k input tokens per ticket. The proposed agents are the opposite shape - single-shot judgments over bounded, forward-flowing artifacts. No repo exploration, no tool loops.

Estimated per-ticket increments:

| Addition | Model | Typical tokens | Est. cost/ticket |
|---|---|---|---|
| Spec fidelity gate | Sonnet 5 | ~12k in / 1.5k out | ~$0.04-0.06 |
| Acceptance judge | Fable 5 | ~25-60k in / 5-12k out | ~$0.55-1.20 |
| Same judge on Opus 4.8 | Opus 4.8 | same | ~$0.30-0.60 |
| NEEDS_HUMAN triage | Fable 5 | fires on ~10-20% of tickets | pennies amortized |

Total: roughly **$0.60-1.30 per ticket**, about a 10-25% increase over the current opus-heavy pipeline. (Run through Claude Code this is subscription usage rather than an invoice, but the proportions hold for rate limits too.)

Fable-specific cost notes:

1. **Fable's premium is 2x Opus per token, and thinking is always on** (billed as output; cannot be disabled). Control depth with `effort` - `medium` or `high` is plenty for a single judgment over pre-gathered evidence.
2. **Cap the diff input.** Pass the diff stat plus hunks; truncate beyond a threshold (~50k tokens) and note the truncation in the prompt. The reviewer already read every line; the judge checks intent, not code.
3. **Prove Fable earns its 2x before committing.** During the advisory-first rollout, run the acceptance gate logging-only on both Opus 4.8 and Fable over a batch of tickets and check whether Fable catches intent gaps Opus misses on the eval cases. If they agree, run on Opus. A middle path: Opus by default, Fable only on large or ambiguous tickets.

The gate can also save money: a PR shipped with a missed-intent bug costs a full re-run of the inner loop later (several dollars in executor + reviewer + verifier rounds) plus human review time. Catching one intent miss per ~10 tickets roughly pays for the judge on all 10.

## 7. Build order

1. Original-ask preservation + fidelity gate in `/wf-spec` (small; protects the unconfirmed linear-mode persist path today) - edit `wf-spec.md`, add a small checker agent.
2. `wf-acceptor` agent (from `wf-judge` lineage) + `wf-runner.md` hook, **advisory mode** (logging-only, dual-run Opus 4.8 vs Fable).
3. Eval cases (spec-drift, letter-vs-intent) + baseline promotion.
4. Flip both gates to blocking once verdict quality is proven.
5. NEEDS_HUMAN triage later, if interrupt volume justifies it.
