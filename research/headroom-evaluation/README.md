# Headroom evaluation for Hermes/Snowden agents

Linear: [CDL-1339](https://linear.app/michaelcourtney/issue/CDL-1339/snowdenhermes-agents-have-a-verified-headroom-compression)

Date: 2026-06-08

## Executive recommendation

**Do not put Headroom in the default Hermes/Snowden request path yet.** It is promising, installable, local-first, and its reversible CCR storage works in a contained test, but the current behavior is uneven on the exact payload classes Snowden agents rely on.

Recommended next step: **pilot Headroom as an optional MCP/manual compression tool first**, not as an automatic proxy/wrapper. Use it for large browser snapshots, transcript-like text, and code exploration payloads where lossy compression is acceptable and a retrieval key is available. Keep exact outputs such as SQL/D1 results, migrations, audit rows, auth material, Linear payloads, and deploy/test logs on Hermes' native uncompressed or explicit summarization path until a policy layer can classify them safely.

## Sources checked

- YouTube talk: `https://youtu.be/UOWSHg18cL0?si=NrGTeE3OgW_40NtS`
- Repository: `https://github.com/chopratejas/headroom`
- Local inspected checkout: `01762b1ec79174f943557a9768a0c0f373ed1f99`
- Installed package in isolated virtualenv: `headroom-ai==0.23.0`
- README claims: library, proxy, agent wrap, MCP, cross-agent memory, `headroom learn`, reversible CCR, local-first, Apache-2.0. README lines 47-55 and 63-82 in the inspected checkout describe the modes and CCR architecture.
- Quickstart docs: `pip install headroom-ai`, `headroom proxy --port 8787`, SDK simulate/audit, tool-output compression, and per-tool skip profiles.
- Compression docs: Universal Compression detects JSON/code/log/text, preserves structure, stores originals through CCR, and exposes `ccr_key` for retrieval.
- MCP docs: `headroom_compress`, `headroom_retrieve`, and `headroom_stats`; MCP-only mode stores originals locally and allows retrieval by hash.
- Docker docs: wrapper keeps Headroom in Docker while mounting `~/.headroom`, `~/.claude`, `~/.codex`, and `~/.gemini`; proxy default port is 8787.

## Contained benchmark setup

- No global install was performed.
- Used a temporary checkout under `/tmp/headroom-inspect` and a temporary virtualenv `/tmp/headroom-venv`.
- Ran with `HEADROOM_TELEMETRY=off`.
- Started the proxy only for health/stats verification on `127.0.0.1:8787`; no agent traffic or provider credentials were routed through it.
- Benchmark script: [`bench_headroom.py`](./bench_headroom.py)
- Raw results: [`benchmark-results.json`](./benchmark-results.json)

Representative samples:

1. Synthetic Snowden D1/API JSON result rows with `CDL-*`, capture IDs, workflow IDs, statuses, and verbose Quick Capture notes.
2. Synthetic Cloudflare Worker log stream with request IDs, capture IDs, one repeated `AiError 5006`-style failure, and route/status fields.
3. Real Hermes context compressor code excerpt from `agent/context_compressor.py`.
4. Transcript-like Headroom talk text fetched with the existing Hermes YouTube transcript helper.
5. Browser snapshot-like accessibility/tool-output text with repeated refs, labels, and deliverable IDs.

## Benchmark results

| Sample | Content type detected | Handler | Tokens before | Tokens after | Saved | Notes |
|---|---:|---:|---:|---:|---:|---|
| `json_d1_results` | JSON | json | 39,021 | 31,421 | 19.5% | Structure/IDs preserved; not a large win for dense operational JSON. |
| `worker_logs` | JSON | json | 13,549 | 13,549 | 0.0% | Misdetected plain logs as JSON and did not compress. This is a blocker for automatic log-path adoption. |
| `hermes_context_compressor_code` | CODE | code | 14,042 | 7,571 | 46.1% | Useful for code exploration; preserve imports/signatures/body shape. |
| `headroom_video_transcript` | JSON | json | 17,948 | 3,906 | 78.2% | Strong savings on transcript-like payload, but detector treated transcript envelope as JSON. |
| `browser_snapshot_like` | UNKNOWN | noop | 21,300 | 9,160 | 57.0% | Strong savings despite noop handler because repeated whitespace/phrasing collapses. |

A CCR retrieval smoke test stored a synthetic log payload, retrieved it by `ccr_key`, and confirmed exact equality with the original payload, including the embedded `AiError 5006` marker.

Proxy smoke test:

```json
{
  "service": "headroom-proxy",
  "status": "healthy",
  "ready": true,
  "version": "0.23.0"
}
```

`/stats` returned zero proxied API requests, as expected for a no-provider, local health-only verification.

## Security and governance assessment

Positive:

- Apache-2.0 project.
- Local-first architecture: the proxy and MCP server run locally; CCR originals are local by default.
- Multiple integration modes allow a low-risk MCP-only pilot before any proxy/wrapper routing.
- Per-tool skip profiles exist in docs, which is important for D1, auth, and deploy/test exactness.
- Docker-native install exists if we want runtime isolation.

Risks / open concerns:

- Automatic compression is lossy unless the agent knows when to retrieve by CCR hash.
- Detector behavior is not yet reliable enough for operational logs: the Worker log sample was detected as JSON and saved 0%.
- Dense JSON D1/API outputs saved only 19.5%, so the token win may not justify risk on exact operational records.
- Global wrappers/proxy could accidentally intercept sensitive provider traffic or agent calls if configured broadly.
- Docker-native mode mounts multiple agent homes (`~/.headroom`, `~/.claude`, `~/.codex`, `~/.gemini`), which is convenient but not the right default for Snowden governance without a narrow profile/container policy.
- CCR TTL/retrieval behavior must be aligned with Hermes session lifecycle before relying on it during long-running Discord sessions or subagent work.

## Adoption path

1. **MCP/manual pilot only**
   - Add Headroom only as an optional MCP server/tool in a disposable Snowden/Hermes profile.
   - Do not configure `ANTHROPIC_BASE_URL`, `OPENAI_BASE_URL`, `headroom wrap`, or persistent service defaults for production agents.

2. **Policy allowlist**
   - Allow compression for: browser snapshots, large transcripts, repeated search results, code exploration snippets, non-authoritative web extracts.
   - Skip compression for: SQL/D1 results used as source of truth, migrations, audit logs, secrets/auth headers, deploy output, failing test output, Linear mutation payloads, financial/billing data, legal/governance records, and any user-provided exact wording.

3. **Hermes-native integration candidate**
   - The safest long-term path may be a Hermes-native CCR-style compression layer, not the full Headroom proxy.
   - Hermes already has context compression. The useful Headroom ideas are: reversible content-addressed originals, explicit retrieval handles, type-aware compression policies, and stats. Those can be adopted without routing all model traffic through a separate proxy.

4. **Acceptance criteria before wider rollout**
   - Classification policy tests for D1 JSON, logs, code, transcript, browser snapshot, and secret-like payloads.
   - Exact retrieval proof across session/subagent boundaries.
   - Default-deny tool profile behavior.
   - Confirm telemetry/offline behavior from source/config, not only environment variable convention.
   - No broad home-directory mounts in Snowden runtime profiles unless approved.

## Decision

**Recommended decision for CDL-1339:** close as evaluated with a guarded pilot recommendation.

- **Use now:** optional MCP/manual compression in a sandbox profile.
- **Do not use now:** default proxy/wrapper for Snowden OS, ClientOS, or Hermes production agents.
- **Build next if needed:** a Hermes-native reversible compression policy inspired by Headroom's CCR/MCP pattern.
