# Reliable Core Releases & Editor Dependency Delivery

**Status:** accepted design; audited 2026-07-23; implementation not authorized

**Program Epic:** [editor-assistant#38](https://github.com/lanmogu98/editor-assistant/issues/38)

**GitHub Project:** [Reliable Core Releases & Editor Dependency Delivery](https://github.com/users/lanmogu98/projects/11)

## Purpose and authority

Create a reproducible cross-repository delivery path in which
`llm-exec-core` publishes validated, immutable Python artifacts through GitHub
Releases and `editor-assistant` consumes, tests, and proposes upgrades to those
artifacts without following Core `main`.

This document, the Project, and its Issues are planning contracts. They do not
authorize workflow implementation, repository-setting changes, releases,
pull requests, merges, secrets, approvals, bypasses, or direct updates to
`main`. Every child needs a later explicit dispatch for its exact actor, scope,
branch/PR delivery, and any separately withheld owner action.

## Audited current state

- Core `main` is version `0.4.1`; its version also appears in
  `llm_exec_core.__version__`, the root `uv.lock` package entry, and version
  assertions.
- Core tags use bare versions such as `0.4.1`, not `v0.4.1`.
- Core has locked, provider-offline CI on Python 3.10 and 3.13, but no Release
  workflow. Its required checks are `CI / python-3.10` and
  `CI / python-3.13`.
- Existing Release `0.4.1` predates this program. GitHub Release immutability
  applies only to future Releases, so `0.4.1` is not an eligible Editor
  artifact.
- Editor declares `llm-exec-core>=0.4.1,<0.5.0`, then overrides it with the
  editable sibling path `../llm-exec-core` in `[tool.uv.sources]`; `uv.lock`,
  `README.md`, and `DEVELOPER_GUIDE.md` encode that local layout.
- Editor has no CI workflow and no active `main` Ruleset tied to real checks.
- The 2026-07-23 local feasibility baseline on Python 3.13 completed
  `uv sync --locked`, 183 unit tests, Black, Flake8, and mypy successfully.
  Python 3.10 remains a required real CI result.

"Provider-offline" means tests perform no provider/live/paid LLM calls and
receive no provider credentials. Runner bootstrap still downloads declared
package and Release artifacts over HTTPS.

## Accepted decisions

1. Publish Core distributions through public GitHub Releases, not PyPI.
2. Core tags are exact normalized PEP 440 versions without a `v` prefix.
3. Enable GitHub Release immutability before any program Release. Convention,
   checksums, and an unmoved tag are not substitutes for the platform control.
4. Build wheel and sdist from one exact reviewed `main` commit and verify all
   intentional version loci plus distribution metadata.
5. Editor consumes one immutable Release wheel through a PEP 508 HTTPS URL
   ending in `#sha256=<verified-wheel-digest>`; it never follows Core `main`.
6. The GitHub asset digest, `SHA256SUMS`, downloaded bytes, URL fragment,
   wheel metadata, package `__version__`, Release tag, and tag target must
   agree.
7. Stable immutable Releases below `0.5.0` are eligible for routine update
   PRs. Crossing `0.5.0` opens one boundary-keyed compatibility assessment and
   never changes the dependency automatically.
8. Generated dependency PRs are neither approved nor auto-merged.
9. Editor CI exposes three stable checks and executes candidate code only with
   a read-only token.
10. Editor `main` uses a solo-maintainer Ruleset with zero approvals, strict
    GitHub-Actions-sourced checks, resolved conversations, no force/delete,
    and no bypass actor.
11. Repository default `GITHUB_TOKEN` permissions stay read-only. Release
    immutability and Actions-created-PR capability are explicit, separate
    owner-setting prerequisites rather than hidden workflow assumptions.
12. Updater production mutation is additionally gated by the repository
    variable `LLM_EXEC_CORE_UPDATER_ENABLED`. It remains absent or `false`
    through #44 and is enabled only inside the explicitly dispatched #43
    rehearsal, preventing scheduled runs from mutating state between gates.

## Program structure and dependency order

GitHub native parent/sub-issue and blocked-by relations are the dependency
source of truth. Project `Sequence` mirrors them and is sorted ascending.

| Sequence | Repository | Contract | Depends on | Observable result |
| ---: | --- | --- | --- | --- |
| 0 | Editor | [Epic #38](https://github.com/lanmogu98/editor-assistant/issues/38) | — | Program coordination and final acceptance |
| 1 | Core | [#39](https://github.com/lanmogu98/llm-exec-core/issues/39) | Existing Core CI | Reviewed Release workflow and post-merge dry run |
| 2 | Core | [#41](https://github.com/lanmogu98/llm-exec-core/issues/41) | Core #39 | Future Releases made immutable by owner setting |
| 3 | Core | [#42](https://github.com/lanmogu98/llm-exec-core/issues/42) | Core #41 | Legitimate compatible version commit on `main` |
| 4 | Core | [#40](https://github.com/lanmogu98/llm-exec-core/issues/40) | Core #42 | First immutable workflow-produced stable Release |
| 5 | Editor | [#39](https://github.com/lanmogu98/editor-assistant/issues/39) | Core #40 | Hash-bearing immutable dependency and lock |
| 6 | Editor | [#40](https://github.com/lanmogu98/editor-assistant/issues/40) | Editor #39 | Stable quality and Python compatibility checks |
| 7 | Editor | [#41](https://github.com/lanmogu98/editor-assistant/issues/41) | Editor #40 | Active `main` Ruleset using observed check names |
| 8 | Editor | [#42](https://github.com/lanmogu98/editor-assistant/issues/42) | Editor #41 | Reviewed updater and non-mutating post-merge dry run |
| 9 | Editor | [#44](https://github.com/lanmogu98/editor-assistant/issues/44) | Editor #42 | PR switch enabled while mutation stays inactive |
| 10 | Editor | [#43](https://github.com/lanmogu98/editor-assistant/issues/43) | Editor #44 | Controlled activation and production rehearsal |

```mermaid
flowchart LR
    C1["Core #39<br/>Release workflow"] --> C2["Core #41<br/>Immutable Releases"]
    C2 --> C3["Core #42<br/>Version preparation"]
    C3 --> C4["Core #40<br/>First immutable Release"]
    C4 --> E1["Editor #39<br/>Immutable dependency"]
    E1 --> E2["Editor #40<br/>Provider-offline CI"]
    E2 --> E3["Editor #41<br/>main Ruleset"]
    E3 --> E4["Editor #42<br/>Updater implementation"]
    E4 --> E5["Editor #44<br/>Actions PR setting"]
    E5 --> E6["Editor #43<br/>Activation + rehearsal"]
```

No child starts before its native blocker closes. The Epic closes only after
sequence 10 passes and its evidence is recorded.

## Contract details

### 1. Core Release workflow — Core #39

Add `.github/workflows/release.yml`, manually dispatched with exact `version`
and Boolean `dry_run` inputs. It must:

1. run only for the dispatched current `main` SHA;
2. use a bare no-`v` tag;
3. match input, `pyproject.toml`, `llm_exec_core.__version__`, the root
   `uv.lock` entry, wheel/sdist metadata, and intended tag;
4. reject non-normalized input and existing tags/Releases/assets before
   mutation;
5. run Core's canonical locked gates on Python 3.10 and 3.13;
6. build wheel and sdist once, then clean-install each distribution separately
   on both Pythons with import/metadata/version assertions;
7. generate `SHA256SUMS`;
8. upload ordinary workflow artifacts only in dry-run mode;
9. in publish mode, create the tag and draft, attach the complete assets,
   publish, then read back tag target, asset digests, and `immutable: true`;
10. serialize release attempts without cancelling an in-flight publish.

Actions are full-SHA pinned. Defaults are read-only; only the publication job
gets `contents: write`. No provider key, PAT, live call, untrusted PR code, or
`pull_request_target` is allowed.

`workflow_dispatch` only receives events after the workflow exists on the
default branch. Therefore the implementation PR first passes existing CI and
independent exact-head review, the maintainer merges, and then a dry run on the
resulting `main` SHA closes #39. A failure requires a repair PR. #39 creates no
stable Release.

### 2. Release immutability — Core #41

After #39's dry run, the maintainer enables **Settings → General → Releases →
Enable release immutability**. UI and
`GET /repos/lanmogu98/llm-exec-core/immutable-releases` must read back enabled.
The Issue records the prior state, retrieval date, and owner-enforcement state.

This Issue creates no tag or Release and changes no workflow permission.
Existing `0.4.1` remains mutable/ineligible because the setting is prospective.

### 3. Legitimate version preparation — Core #42

Prepare one focused version-only PR after release-worthy product changes are
already reviewed on `main`. The version must be stable, newer than `0.4.1`,
below `0.5.0`, absent from tags/Releases, and justified by compatibility impact.

The bounded surface is `project.version`, `llm_exec_core.__version__`, the root
package version in `uv.lock`, direct version assertions, and minimal
changelog/release-note preparation. Refreshing the lock may change only that
root version; third-party versions, sources, and hashes remain identical.
Runtime, catalog, schema, dependency, workflow, and unrelated lock changes are
excluded. The PR passes `uv lock --check`, canonical CI, and independent
review; it creates no Release or tag. If no legitimate compatible version is
ready, the program waits.

### 4. First immutable Release — Core #40

On Core #42's exact merged `main` SHA, run dry-run and then owner-dispatched
publish mode. Record:

- source SHA, no-`v` tag, tag target, Release/run URLs;
- agreeing Core `pyproject.toml`, `__version__`, root `uv.lock`, and
  distribution versions;
- `immutable: true` and successful Release-attestation verification;
- wheel, sdist, `SHA256SUMS`, GitHub asset digests, and matching local hashes;
- generated notes range; and
- Python 3.10/3.13 clean-install, import, and version evidence for both wheel
  and sdist.

The consumer URL must support appending `#sha256=<wheel digest>`. A public bad
Release is preserved and superseded; it is never rewritten.

### 5. Immutable Editor dependency — Editor #39

Replace the range plus sibling override with:

```toml
"llm-exec-core @ https://github.com/lanmogu98/llm-exec-core/releases/download/X.Y.Z/llm_exec_core-X.Y.Z-py3-none-any.whl#sha256=<verified-wheel-digest>"
```

Regenerate `uv.lock` without a global upgrade. Lock changes must be limited to
the Editor root requirement, Core, and dependency-closure changes required by
the new Core metadata; unrelated locked versions, sources, and hashes remain
unchanged. Update both languages in `README.md`, the stale sibling and `0.1.0`
instructions in `DEVELOPER_GUIDE.md`, and the existing dependency contract
tests. Those tests parse the direct URL/version/hash, reject local sources, and
enforce a stable pin below `0.5.0`; crossing the boundary requires an explicit
assessment plus an intentional policy-test change. Validate from clean
no-sibling checkouts with:

- `uv sync --locked`;
- `uv run --frozen pytest tests/unit/`;
- `uv build` plus Editor wheel metadata inspection; and
- `pip install .` and public-import/version smoke tests on Python 3.10/3.13.

The updater owns the `<0.5.0` policy; a direct URL cannot carry a simultaneous
range specifier.

### 6. Editor CI — Editor #40

Add `.github/workflows/ci.yml` for every PR to `main`, push to `main`, and
manual dispatch, with no path or commit skip. Pin uv and all Actions; run
`uv sync --locked`, then frozen commands. Default permission is
`contents: read`.

Stable job/check names:

- `Quality` — Python 3.13; Black on `src/ tests/`, Flake8 on `src/`, mypy on
  `src/`;
- `Unit tests (Python 3.10)` — full `tests/unit/`;
- `Unit tests (Python 3.13)` — the same suite.

The matrix uses `fail-fast: false`. Integration/stress/live/paid tests and
provider credentials are excluded. A baseline problem becomes a focused
blocker instead of a weakened check or hidden cleanup.

### 7. `main` Ruleset — Editor #41

After recent real checks exist, create active `Protect main` targeting `main`:

- PR required, 0 approvals, conversations resolved;
- all three exact checks required from the GitHub Actions expected source;
- branch current with `main` before merge;
- force push and deletion blocked;
- no bypass actor.

Signed commits, linear history, deployments, code owners, auto-merge, and
unrelated gates stay off. A safe PR proves pending/current-head enforcement;
force/delete controls are verified by readback, not destructive tests.

### 8. Compatible Release updater — Editor #42

Add:

- `.github/workflows/update-llm-exec-core.yml`;
- `scripts/update_llm_exec_core.py` for deterministic PEP 440 selection,
  integrity validation, and rewrite planning;
- `tests/unit/test_update_llm_exec_core.py` with offline fixtures; and
- an explicit `packaging` development dependency plus lock update.

The updater runs daily and by manual dry run, with one concurrency group. A
write-capable path runs only when repository variable
`LLM_EXEC_CORE_UPDATER_ENABLED` is exactly `true`. When the variable is absent
or false, scheduled and non-dry-run invocations stop after read-only discovery
and create no branch, PR, assessment Issue, or dependency-file mutation. Every
updater invocation must use the workflow and source ref from current `main`;
another ref fails before a write-capable job can start. It:

1. paginates public Releases and parses versions with `packaging.version`;
2. selects the greatest newer stable public version below `0.5.0` before any
   integrity filtering, then requires that exact Release to be immutable and
   complete;
3. independently detects the `0.5.0` boundary, even in the same run;
4. requires the wheel, sdist, checksum file, attestation, tag provenance,
   `immutable: true`, and agreeing GitHub/file/download digests;
5. fails rather than falling back when that greatest version is mutable,
   malformed, incomplete, or internally inconsistent;
6. rewrites the hash-bearing URL, performs a minimal non-global lock update,
   checks it, enforces a two-file diff allowlist, and rejects lock changes
   outside the Editor/Core dependency closure;
7. owns one branch, `automation/update-llm-exec-core`, and at most one active
   same-repository PR targeting `main`; an active PR advances to the greatest
   candidate using guarded force-with-lease semantics;
8. does not recreate a deliberately closed PR for the same candidate;
9. keeps one assessment Issue keyed to boundary `0.5.0`; and
10. never approves, auto-merges, bypasses, or pushes to `main`.

Only the mutation job has `contents: write`, `pull-requests: write`,
`issues: write`, and `actions: write`; it is conditioned on both current
`main` and the activation variable. Candidate code is not installed or
executed in that privileged job. Tags, filenames, notes, and API JSON are
untrusted data and are never evaluated as shell code.

After a generated branch/PR exists, the updater explicitly dispatches
`.github/workflows/ci.yml` on that branch with
`return_run_details=true`, requires the HTTP 200 response's
`workflow_run_id`/URLs, and asserts event, branch, head SHA, and all three job
names/results. It does not rely on the approval-required PR run generated by a
`GITHUB_TOKEN` event or ambiguous after-the-fact run matching.

Because the new updater also needs to exist on the default branch, #42 closes
after its implementation PR is merged and a fixture-backed non-mutating dry run
succeeds. Tests must prove the absent/false activation gate prevents every
mutation and a non-`main` dispatch cannot enter the privileged job. Production
remains inactive through #44.

### 9. Actions-created PR setting — Editor #44

After reviewing every workflow permission, the maintainer enables **Allow
GitHub Actions to create and approve pull requests** while retaining read-only
default workflow permissions. The combined GitHub switch does not authorize
this workflow to approve anything; no approval or auto-merge code is present.
The activation variable remains absent or `false`, so this setting gate cannot
race a schedule into a production branch, PR, or assessment Issue.

UI, `GET /repos/lanmogu98/editor-assistant/actions/permissions/workflow`, and
`GET /repos/lanmogu98/editor-assistant/actions/variables` must agree. This
setting-only Issue creates no PR and introduces no PAT, App key, deploy key, or
provider secret. #43 owns changing `LLM_EXEC_CORE_UPDATER_ENABLED` to `true`,
reading it back through the named-variable endpoint, and the first production
run.

### 10. Production rehearsal — Editor #43

Use a later legitimate stable Core Release below `0.5.0`—not the initial
Release already pinned by Editor #39. After all preconditions are re-read, the
maintainer changes `LLM_EXEC_CORE_UPDATER_ENABLED` from absent/false to `true`,
records UI and
`GET /repos/lanmogu98/editor-assistant/actions/variables/LLM_EXEC_CORE_UPDATER_ENABLED`
readback, and from that point #43 owns either the next scheduled run or an
explicit production dispatch. Prove:

1. immutable Release and artifact evidence;
2. updater discovery and exactly one hash-bearing dependency PR;
3. explicit CI dispatch run ID on the exact PR head;
4. Ruleset block while checks are pending;
5. all three checks passing;
6. maintainer manual merge and green post-merge `main` CI.

Use read-only fixture/dry-run input for the `0.5.0+` path, including the case
where compatible and boundary Releases coexist. Do not create a fake Release
or fake production assessment Issue.

Open a rollback PR to the preceding validated immutable URL/hash, regenerate
the lock, and let it reach green/mergeable Ruleset state. Record evidence and
close it unmerged unless rollback is actually needed. This exercises recovery
without deliberately leaving `main` behind.

## Failure and rollback semantics

- Metadata, tag, immutability, attestation, asset, digest, or lock mismatch
  fails closed before consumer mutation.
- Core validation failure creates no public Release. An incomplete draft may
  be inspected/removed only by the maintainer.
- A bad immutable public Release is marked unsuitable and superseded by a new
  version; tag/asset rewriting is forbidden.
- Closing a generated Editor PR leaves the current dependency unchanged and
  suppresses recreation for the same candidate.
- Editor rollback uses the immediately preceding validated URL/hash through a
  normal PR, identical CI, and the Ruleset.
- Before updater recovery or permission rollback, set
  `LLM_EXEC_CORE_UPDATER_ENABLED=false` first so scheduled runs become
  read-only before any other control changes.
- Direct `main` pushes, Ruleset bypass, tag reuse, and asset replacement are
  never recovery mechanisms.

## Security boundaries

- No provider API keys, paid calls, PATs, or production environment files.
- Defaults are read-only; write scopes exist only on the two narrowly scoped
  publication/updater jobs.
- All external Actions are full-SHA pinned and uv is version-pinned.
- Candidate Core code executes only in read-only Editor CI, never in the
  write-capable updater job.
- Public Release metadata and notes are untrusted input.
- Required Ruleset checks accept GitHub Actions as the expected source.
- No credential alternative is introduced without a new focused design and
  explicit maintainer approval.

## Known distribution constraint

PEP 508 direct URLs are valid for pip/uv integration, and pip accepts them when
Editor is installed locally or from a URL. Standards-conformant indexes such as
PyPI reject uploaded distributions whose metadata contains direct URL
dependencies. Publishing Editor itself to PyPI is therefore out of scope and
would require revisiting Core distribution.

## Non-goals

- Publishing Core or Editor to PyPI in this program.
- Tracking Core `main`, a floating tag, or an unversioned/mutable asset.
- Bot approval, automatic merge, or Ruleset bypass.
- Live integration/provider tests in required CI.
- Core catalog/schema/pricing/execution-boundary work.
- Signed-commit or linear-history mandates.
- Implementing any workflow or changing any setting as part of this planning
  audit.

## Program completion criteria

The program is complete only when all ten native child contracts close in
order, Project `Sequence` agrees, Editor #43 records exact evidence, and the
Epic #38 acceptance checklist passes. Until then, the Project is coordination;
each child Issue is the only implementation authority for its bounded concern.

## Audit corrections incorporated

The 2026-07-23 audit corrected these gaps and drifts:

- changed design examples from a prefixed tag placeholder to the repository's
  actual no-`v` `X.Y.Z` contract;
- separated Release immutability, Core version preparation, and Actions PR
  authorization into distinct Issues;
- required actual GitHub immutable Releases and attestations;
- added the PEP 508 `#sha256=` fragment and multi-source digest agreement;
- added all Core version loci and wheel/sdist metadata checks;
- handled the default-branch-only `workflow_dispatch` constraint explicitly;
- made dependency synchronization enforce lock consistency with
  `uv sync --locked`;
- clarified provider-offline versus dependency-download network access;
- bound required checks to the GitHub Actions source;
- specified exact-head CI dispatch/run-ID verification for bot PRs;
- required `return_run_details=true` so the dispatched CI run is identified
  from the HTTP 200 response rather than timing-based lookup;
- prevented candidate-code execution in the updater's write-capable job;
- defined greatest-version, one-active-PR, closed-candidate, concurrent-run,
  and boundary-deduplication behavior;
- required wheel and sdist clean-install smoke tests on both supported Pythons;
- required minimal lock diffs and a CI-enforced below-`0.5.0` dependency
  policy, closing global-upgrade and manual-edit bypasses;
- added an explicit repository-variable activation gate to prevent scheduled
  mutation between updater merge, PR authorization, and production rehearsal;
- reconciled rollback proof with a green unmerged rollback PR; and
- promoted native sub-issue/blocked-by relations as dependency source of truth.

## External references

- [GitHub: Immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)
- [GitHub: Preventing changes to releases](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes)
- [GitHub: Release REST API](https://docs.github.com/en/rest/releases/releases)
- [GitHub: `GITHUB_TOKEN` event behavior](https://docs.github.com/en/actions/concepts/security/github_token)
- [GitHub: Triggering workflows](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
- [GitHub: Workflows REST API](https://docs.github.com/en/rest/actions/workflows)
- [GitHub: Required ruleset checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [GitHub: Managing Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
- [GitHub: Actions variables REST API](https://docs.github.com/en/rest/actions/variables)
- [GitHub: Adding sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)
- [GitHub: Creating issue dependencies](https://docs.github.com/en/enterprise-cloud@latest/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)
- [Python Packaging: Dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
- [Python Packaging: Version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/)
- [Setuptools: Dependency management](https://setuptools.pypa.io/en/stable/userguide/dependency_management.html)
- [uv: Project dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)
