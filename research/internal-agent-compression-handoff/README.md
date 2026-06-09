# Internal agent handoff + compression lane

Linear: [CDL-1340](https://linear.app/michaelcourtney/issue/CDL-1340/hermes-compression-and-internal-agent-handoff-lane-is-ready)
Date: 2026-06-08
Audience: Mike / internal agents only

> **Internal only. Not client-facing Snowden operating documentation.**
> Do not copy this file into Snowden governance docs, break-glass docs, client reports, or ClientOS client-facing briefs. It is an internal transition and engineering-control document for Hermes/agent work.

## Mike directive captured

Mike moved this profile out of Snowden-only mode. The operating interpretation is:

- Snowden remains maintained and available for emergencies / cleanup / continuity.
- Broader internal systems work can now happen from this profile when explicitly requested.
- Compression work is an internal Hermes/system concern, not a Snowden client deliverable by default.
- Context transferred to another enterprise agent should be curated, non-client-facing, and free of secrets or client-only governance material unless Mike explicitly asks for that scope.

## Current tracking

- Active internal Linear issue: [CDL-1340](https://linear.app/michaelcourtney/issue/CDL-1340/hermes-compression-and-internal-agent-handoff-lane-is-ready)
- Parent session ops issue: [CDL-1302](https://linear.app/michaelcourtney/issue/CDL-1302/snowden-os-session-operations)
- Prior Headroom evaluation PR: <https://github.com/mkc909/hermes-agent/pull/1>

## Git/repo state snapshot

Snapshot taken during the transition sweep on 2026-06-08.

| Repo/worktree | State | Action |
|---|---|---|
| `/home/mike/.hermes/hermes-agent` | Clean and synced to `mkc909/main` after fast-forward; upstream reset to `mkc909/main` to avoid false divergence from `NousResearch/main`. | Use as canonical Hermes source checkout for internal work. |
| `/home/mike/worktrees/hermes-agent-cdl-1339-headroom` | Clean and pushed. PR #1 open. | Keep until PR is merged/closed; contains Headroom evaluation artifact. |
| `snowden-breakglass` | Clean; local commits are on GitHub; upstream reset to real `origin/master` because stale `mkcaus` remote no longer resolves. | No client-facing doc edits needed from this transition unless Mike asks. |
| `snowden-private` | Clean/synced. | Leave alone. |
| `Snowden_Client` | Clean/synced. | Leave alone. |
| `snowdenos-hermes` | Clean/synced. | Leave alone. |
| `snowdenos-app` | Dirty with real code/test edits; patch saved in `/tmp/mike_git_sync_patches_20260608/snowdenos-app.patch`. | Do not reset; inspect/attribute before commit/push. |
| `ops-os` | Dirty and behind remote; patch saved in `/tmp/mike_git_sync_patches_20260608/ops-os.patch`. | Do not pull/reset until local brand-config edits are attributed. |
| `ops-os-ui` | Dirty with real code edits; patch saved in `/tmp/mike_git_sync_patches_20260608/ops-os-ui.patch`. | Do not reset; inspect/attribute before commit/push. |

## Compression direction

Prior evaluation conclusion: **do not put Headroom in the default Hermes/Snowden request path yet.**

Recommended lane now:

1. **Keep Hermes native compression as the default.** Current source files to work from:
   - `agent/context_compressor.py`
   - `agent/conversation_compression.py`
   - `agent/context_engine.py`
   - `hermes_cli/partial_compress.py`
   - `website/docs/developer-guide/context-compression-and-caching.md`
2. **Pilot reversible compression as an optional/internal capability first.** Headroom ideas worth carrying forward:
   - content-addressed original storage / retrieval handles;
   - explicit retrieve-before-use workflow for lossy summaries;
   - per-tool and per-payload allow/deny policy;
   - stats on saved tokens and retrieval usage.
3. **Default-deny exact operational material.** Do not auto-compress:
   - SQL/D1 rows used as source of truth;
   - migrations;
   - audit logs and hash chains;
   - secrets/auth headers/tokens;
   - deploy/test failure logs where exact output matters;
   - Linear mutation payloads;
   - billing/legal/governance records;
   - user-provided exact wording.
4. **Allow only low-risk high-volume material initially:** browser snapshots, transcript-like text, repeated web/search results, code exploration excerpts, and non-authoritative notes.

## Internal context-transfer format

Use this shape when preparing context for the other enterprise agent:

```markdown
# Internal handoff: <system/topic>

Audience: internal agent only
Client-facing: no
Secrets included: no
Source boundary: <repos/docs/sessions checked>
Last verified: <date + command/source>

## Purpose
<What this system exists to do.>

## Current state
<Only verified facts. No guesses, no stale issue claims.>

## Operating rules
<Durable constraints and preferences.>

## Repos and source paths
<Repo URLs/paths, branch/worktree notes, private/public status.>

## Open work
<Linear URLs and objective titles.>

## Safe actions
<What the receiving agent can do without asking.>

## Ask Mike before
<Destructive, cross-client, client-facing, secrets, billing/legal, production deploys.>
```

## Next implementation checkpoints

- [ ] Decide whether the first internal compression implementation is a Hermes-native CCR store or a Headroom MCP-only pilot.
- [ ] Add classification tests for allow/deny payload classes before enabling any automatic compression path.
- [ ] Add retrieval-handle tests that prove exact-original recovery across session/subagent boundaries.
- [ ] Keep all transition notes in internal repo artifacts or private agent docs, not Snowden client-facing docs.
