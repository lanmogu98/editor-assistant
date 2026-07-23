# Reliable Core Releases & Editor Dependency Delivery

**Status:** accepted PyPI pivot; audited 2026-07-23; Project revision and
Core #39 redispatch authorized; owner-controlled settings and publication
remain separately gated

**Program Epic:** [editor-assistant#38](https://github.com/lanmogu98/editor-assistant/issues/38)

**GitHub Project:** [Reliable Core Releases & Editor Dependency Delivery](https://github.com/users/lanmogu98/projects/11)

## Purpose and authority

Create a reproducible cross-repository delivery path in which
`llm-exec-core` publishes validated Python distributions to public PyPI through
GitHub OIDC Trusted Publishing, while `editor-assistant` consumes a bounded
index dependency, locks exact files with uv, tests upgrades, and proposes
routine compatible updates without following Core `main`.

PyPI is the authoritative distribution channel for this program. A GitHub
Release may later present release notes, but it is non-authoritative,
non-blocking, and ignored by the Editor updater.

This document, the Project, and its Issues are execution contracts. A child
starts only after its native blockers close and its exact implementation or
owner-action dispatch is recorded. No child implicitly authorizes a
repository setting, PyPI setting, package publication, pull-request merge,
bypass, approval, secret, or direct update to `main`.

## Audited current state

- Core `main` is version `0.4.1`, but contains multiple reviewed changes after
  tag `0.4.1`. The first PyPI distribution therefore needs a new legitimate
  version rather than publishing different source under the old version.
- Core has locked, provider-offline CI on Python 3.10 and 3.13. Its observed
  checks are `CI / python-3.10` and `CI / python-3.13`.
- Core has no PyPI publishing workflow, no `pypi` GitHub environment, and no
  PyPI Trusted Publisher.
- A read-only request to PyPI's normalized `llm-exec-core` JSON endpoint
  returned 404 on 2026-07-23. This is evidence only, not a reservation:
  PyPI pending publishers do not reserve names before first publication.
- Editor declares `llm-exec-core>=0.4.1,<0.5.0`, then overrides it with the
  editable sibling path `../llm-exec-core` in `[tool.uv.sources]`. Its lock and
  setup documentation therefore depend on a local sibling checkout.
- Editor has no CI workflow and no active `main` Ruleset tied to observed
  checks.
- The 2026-07-23 Editor feasibility baseline on Python 3.13 completed
  `uv sync --locked`, 183 unit tests, Black, Flake8, and mypy. Python 3.10
  remains a required real CI result.

"Provider-offline" means tests perform no live or paid LLM calls and receive
no provider credentials. Runner bootstrap may download declared packages from
PyPI over HTTPS.

## Accepted decisions

1. Public PyPI, not a GitHub Release asset, is Core's authoritative Python
   distribution channel.
2. Publish with PyPI Trusted Publishing bound to
   `lanmogu98/llm-exec-core`, `.github/workflows/release.yml`, and the protected
   `pypi` environment. Store no PyPI API token.
3. The publishing job alone gets `id-token: write`; it only downloads
   previously validated distributions and invokes the official PyPA publish
   action pinned to a full commit SHA.
4. Build wheel and sdist once from one exact reviewed Core `main` SHA. Verify
   source versions, distribution metadata, filenames, hashes, and clean
   installs before publication.
5. PyPI's non-reusable filenames and release provenance replace the former
   GitHub Release immutability/App-preflight design. A bad or partial public
   version is yanked and superseded, never replaced or reused.
6. Editor declares a standard index requirement
   `llm-exec-core>=FIRST_PYPI_VERSION,<0.5.0`. `uv.lock` records the exact
   selected version, registry files, sizes, and SHA-256 hashes.
7. Stable, non-yanked, attested releases below `0.5.0` are eligible for
   routine lockfile PRs. Any stable release at or above `0.5.0` opens one
   boundary assessment and never widens the dependency automatically.
8. Generated dependency PRs are neither approved nor auto-merged.
9. Editor CI exposes three stable provider-offline checks. Candidate package
   code executes only in read-only CI, never in the updater's write-capable
   job.
10. Editor `main` uses a solo-maintainer Ruleset with zero approvals, strict
    current-head GitHub Actions checks, resolved conversations, no
    force/delete, and no bypass actor.
11. Core publication and Editor updater mutation each have a repository
    variable kill switch. Both remain absent or `false` until their dedicated
    activation issue.
12. TestPyPI is not a prerequisite. The dry-run path validates the exact
    distributions without creating and maintaining a second publisher
    identity.

## Program structure and dependency order

GitHub native parent/sub-issue and blocked-by relations are the dependency
source of truth. Project `Sequence` records dependency depth and is sorted
ascending; equal values are intentionally parallel lanes.

| Sequence | Repository | Contract | Depends on | Observable result |
| ---: | --- | --- | --- | --- |
| 0 | Editor | [Epic #38](https://github.com/lanmogu98/editor-assistant/issues/38) | — | Program coordination and final acceptance |
| 1 | Core | [#39](https://github.com/lanmogu98/llm-exec-core/issues/39) | Existing Core CI | Reviewed Trusted Publishing workflow and post-merge dry run |
| 2 | Core | [#41](https://github.com/lanmogu98/llm-exec-core/issues/41) | Core #39 | Protected `pypi` GitHub environment |
| 3 | Core | [#42](https://github.com/lanmogu98/llm-exec-core/issues/42) | Core #41 | Legitimate first public PyPI version on `main` |
| 4 | Core | [#43](https://github.com/lanmogu98/llm-exec-core/issues/43) | Core #42 | Exact pending PyPI Trusted Publisher |
| 5 | Core | [#40](https://github.com/lanmogu98/llm-exec-core/issues/40) | Core #43 | First attested public PyPI release |
| 6 | Editor | [#39](https://github.com/lanmogu98/editor-assistant/issues/39) | Core #40 | Bounded index requirement and exact uv lock |
| 7 | Core | [#47](https://github.com/lanmogu98/llm-exec-core/issues/47) | Editor #39 | Next natural compatible version prepared |
| 7 | Editor | [#40](https://github.com/lanmogu98/editor-assistant/issues/40) | Editor #39 | Stable quality and Python compatibility checks |
| 8 | Editor | [#41](https://github.com/lanmogu98/editor-assistant/issues/41) | Editor #40 | Active `main` Ruleset using observed check names |
| 9 | Editor | [#42](https://github.com/lanmogu98/editor-assistant/issues/42) | Editor #41 | Reviewed PyPI updater and non-mutating post-merge dry run |
| 10 | Editor | [#44](https://github.com/lanmogu98/editor-assistant/issues/44) | Editor #42 | Actions PR switch enabled while updater stays inactive |
| 11 | Core | [#48](https://github.com/lanmogu98/llm-exec-core/issues/48) | Core #47 and Editor #44 | Real updater-rehearsal version published |
| 12 | Editor | [#43](https://github.com/lanmogu98/editor-assistant/issues/43) | Core #48 | Controlled activation and full production rehearsal |

```mermaid
flowchart LR
    C1["Core #39<br/>Trusted Publishing workflow"] --> C2["Core #41<br/>Protected pypi environment"]
    C2 --> C3["Core #42<br/>Version preparation"]
    C3 --> C4["Core #43<br/>PyPI publisher identity"]
    C4 --> C5["Core #40<br/>First PyPI release"]
    C5 --> E1["Editor #39<br/>Bounded index dependency"]
    E1 --> E2["Editor #40<br/>Provider-offline CI"]
    E1 --> C6["Core #47<br/>Next compatible version"]
    E2 --> E3["Editor #41<br/>main Ruleset"]
    E3 --> E4["Editor #42<br/>PyPI updater"]
    E4 --> E5["Editor #44<br/>Actions PR setting"]
    C6 --> C7["Core #48<br/>Rehearsal release"]
    E5 --> C7
    C7 --> E6["Editor #43<br/>Activation + rehearsal"]
```

No child starts before its native blocker closes. Core #47 version preparation
and the Editor CI/updater lane can proceed in parallel after Editor #39. Core
#48 waits for both Core #47 and Editor #44, then proceeds immediately into the
sequence-12 rehearsal so no intervening compatible release changes its
candidate. The Epic closes only after that convergence evidence is recorded.

## Contract details

### 1. Trusted Publishing workflow — Core #39

Add exactly:

- `.github/workflows/release.yml`;
- `.github/release-build-constraints.txt`;
- `docs/governance/pypi-release.md`; and
- focused governance contract tests.

The workflow is manually dispatched with an exact normalized `version`, the
40-character `expected_sha`, and a Boolean `dry_run`. It must:

1. reject every ref except `refs/heads/main`, require
   `expected_sha == github.sha ==` the repository's current default-branch
   SHA at preflight, and bind all jobs to that exact source;
2. match the input against `pyproject.toml`,
   `llm_exec_core.__version__`, the Core root entry in `uv.lock`, wheel and
   sdist metadata, and expected filenames;
3. reject a non-stable or non-normalized version and detect an already
   published PyPI version before entering publication;
4. run Core's canonical locked gates on Python 3.10 and 3.13;
5. build wheel and sdist once with sources disabled, using an exact Python
   patch version, exact uv version, and hash-locked release build constraint
   for every isolated build-backend requirement; record those versions, then
   separately clean-install each distribution on both supported Pythons with
   import/metadata/version assertions;
6. produce and retain SHA-256 evidence for both distributions;
7. upload ordinary GitHub workflow artifacts in dry-run mode and create no
   tag, GitHub Release, PyPI project, or package version;
8. fail clearly before the publish job when `dry_run` is false and repository
   variable `LLM_EXEC_CORE_PYPI_PUBLISH_ENABLED` is not exactly `true`;
9. use environment `pypi` and grant `id-token: write` only to the minimal
   publish job, whose only steps download the validated artifact and invoke
   `pypa/gh-action-pypi-publish` pinned to a full SHA;
10. leave attestations enabled and store no username, password, API token,
    PAT, or environment secret; and
11. serialize attempts without cancelling an in-flight publication.

All other jobs and workflow defaults are read-only. No provider credential,
live call, untrusted PR code, arbitrary ref, `pull_request_target`, dynamic
shell evaluation, or `skip-existing` behavior is allowed.

The repository's consumer-facing build-system requirement remains
`setuptools>=64.0`, but the release build may not resolve that open range.
`.github/release-build-constraints.txt` pins the selected backend distribution
and its accepted hashes, and the workflow passes that file through uv's build
constraint plus required-hash path. Governance tests reject an unconstrained
isolated release build, a floating Python/uv version, or a backend constraint
without hashes. This program does not claim byte-for-byte reproducibility
across separate runs; it requires one build per run, exact within-run artifact
reuse, a controlled builder, recorded hashes, and PyPI provenance without
changing sdist consumers' metadata.

`workflow_dispatch` becomes usable only after the workflow reaches the default
branch. The implementation PR therefore passes Core CI and exact-head review,
is merged by the maintainer, and then completes a dry run on the resulting
`main` SHA. #39 does not enter the protected environment and publishes
nothing.

### 2. Protected publishing environment — Core #41

After #39's dry run, the maintainer creates GitHub environment `pypi` with:

- deployment branches restricted to `main`;
- the maintainer as required reviewer;
- self-review prevention left off for the solo-maintainer workflow;
- no environment secrets; and
- no unrelated deployment rules.

The Issue records prior state, UI/API readback, reviewer identity, deployment
branch policy, and date. `LLM_EXEC_CORE_PYPI_PUBLISH_ENABLED` remains absent
or `false`. This setting-only issue dispatches no workflow and publishes
nothing.

If the current GitHub plan cannot enforce this exact environment policy, stop
and revise the design; do not silently weaken the gate.

### 3. First PyPI version preparation — Core #42

Prepare one focused version PR after release-worthy changes are already
reviewed on `main`. Because current `main` differs from tag `0.4.1`, the
candidate must be a new stable version greater than `0.4.1`, below `0.5.0`,
and absent from PyPI and Core tags.

The bounded surface is `project.version`, `llm_exec_core.__version__`, the root
package version in `uv.lock`, direct version assertions, and minimal
changelog/release-note preparation. Refreshing the lock may change only that
root version; third-party versions, sources, and hashes remain identical.
Runtime, catalog, schema, dependency, workflow, and unrelated lock changes are
excluded.

The PR passes `uv lock --check`, canonical CI, and independent review. It
creates no PyPI release, tag, GitHub Release, or setting. If no legitimate
compatible version is ready, the program waits rather than inventing a
version.

### 4. PyPI Trusted Publisher — Core #43

Do not execute this owner action until #42 is complete and #40 has a separately
approved, immediately available publication window. The maintainer rechecks
that #42's recorded source SHA is still the current `main` head and normalized
project name `llm-exec-core` is still unregistered, then creates one pending
PyPI GitHub publisher with the exact identity:

- PyPI project: `llm-exec-core`;
- GitHub owner: `lanmogu98`;
- repository: `llm-exec-core`;
- workflow: `release.yml`; and
- environment: `pypi`.

The owning PyPI account must have verified email, two-factor authentication,
and maintainer-controlled recovery material before registration. Record only
the control state, never a recovery code or authentication secret.

Record redacted UI evidence and the registration time. Add no long-lived API
token and no broader publisher. A pending publisher does not reserve the
project name, so proceed directly to #40 in the same owner operation window
rather than leaving the pending identity idle.

If the name is taken or any identity field cannot be matched exactly, stop.
Do not publish under another name, remove the environment constraint, or fall
back to a token without a new design and explicit approval.

### 5. First public PyPI release — Core #40

On Core #42's exact merged `main` SHA, the maintainer:

1. reruns dry-run mode for the exact version and source SHA and confirms every
   non-mutating gate;
2. changes `LLM_EXEC_CORE_PYPI_PUBLISH_ENABLED` from absent/false to `true`
   and records API/UI readback;
3. dispatches publish mode for the exact version and `main` SHA; and
4. explicitly approves the `pypi` environment deployment.

If Core `main` no longer equals #42's recorded SHA before dispatch, stop and
return to version/source preparation. Do not publish intervening source under
the already prepared version.

After upload, read back and record:

- source SHA and workflow run URL;
- PyPI project/version URLs and normalized metadata;
- wheel and sdist filenames, sizes, upload times, and SHA-256 digests;
- agreement between the exact files validated and uploaded within the publish
  run, plus agreement with all source version loci;
- non-yanked status;
- successful cryptographic `pypi-attestations verify pypi` verification for
  both files, followed by Integrity API claim checks for the exact repository,
  workflow, environment, source SHA, subject filenames, and subject digests;
- conversion of the pending publisher to the project's normal publisher;
- the intended PyPI owner/maintainer roster and absence of any unexpected
  publisher identity; and
- clean public-index installs and import/version checks for wheel and sdist
  on Python 3.10 and 3.13.

Package publication is the release. A GitHub tag or Release is optional and
cannot be used as acceptance evidence for PyPI.

### 6. Bounded Editor index dependency — Editor #39

Replace the sibling override with a standard PyPI dependency:

```toml
"llm-exec-core>=FIRST_PYPI_VERSION,<0.5.0"
```

Use the exact Core #40 version as `FIRST_PYPI_VERSION`. Remove Core's
`[tool.uv.sources]` path entry and regenerate `uv.lock` without a global
upgrade. The locked Core entry must use the public PyPI registry and record
the exact selected version plus wheel/sdist URLs, sizes, and SHA-256 hashes.
Lock changes are limited to the Editor root requirement, Core, and dependency
closure changes required by Core metadata; unrelated packages remain fixed.

Update both languages in `README.md`, stale sibling and `0.1.0` instructions
in `DEVELOPER_GUIDE.md`, and dependency contract tests. Tests parse the
specifier, reject local/direct/Git/VCS sources, enforce the `<0.5.0` boundary,
and validate the locked PyPI source/version/hashes.

Validate from a clean checkout with no sibling repository:

- `uv lock --check`;
- `uv sync --locked`;
- `uv run --frozen pytest tests/unit/`;
- `uv build` plus Editor wheel metadata inspection; and
- clean `pip install` plus public import/version smoke tests on Python
  3.10 and 3.13.

This removes the former direct-URL metadata constraint, so publishing Editor
to an index becomes possible in principle, but remains outside this program.

### 7. Editor CI — Editor #40

Add `.github/workflows/ci.yml` for every PR to `main`, push to `main`, and
manual dispatch, with no path or commit skip. Pin uv and all Actions; run
`uv sync --locked`, then frozen commands. Default permission is
`contents: read`.

Stable job/check names:

- `Quality` — Python 3.13; Black on `src/ tests/`, Flake8 on `src/`, mypy on
  `src/`;
- `Unit tests (Python 3.10)` — full `tests/unit/`; and
- `Unit tests (Python 3.13)` — the same suite.

The matrix uses `fail-fast: false`. Integration/stress/live/paid tests and
provider credentials are excluded. A baseline problem becomes a focused
blocker instead of a weakened check.

### 8. Editor `main` Ruleset — Editor #41

After recent real checks exist, create active `Protect main` targeting `main`:

- pull request required with 0 approvals and resolved conversations;
- all three exact current-head checks required from GitHub Actions;
- branch current with `main` before merge;
- force push and deletion blocked; and
- no bypass actor.

Signed commits, linear history, deployments, code owners, auto-merge, and
unrelated gates stay off. A safe PR proves pending/current-head enforcement;
force/delete controls are verified by readback, not destructive tests.

### 9. Compatible PyPI updater — Editor #42

Add:

- `.github/workflows/update-llm-exec-core.yml`;
- `scripts/update_llm_exec_core.py`;
- `tests/unit/test_update_llm_exec_core.py`; and
- only the explicit development dependency and lock changes needed by the
  updater.

The updater runs daily and by manual dry run with one concurrency group. A
write-capable path runs only when repository variable
`LLM_EXEC_CORE_UPDATER_ENABLED` is exactly `true`. When absent or false,
scheduled and non-dry-run invocations stop after read-only discovery and
create no branch, PR, assessment Issue, or dependency-file mutation. Every
invocation uses workflow and source code from current `main`; another ref
fails before a write-capable job can start.

Using PyPI JSON/Simple and Integrity APIs as untrusted input, it:

1. reads the current exact Core version from `uv.lock` and parses versions
   with `packaging.version`;
2. permits HTTPS only, fixes API hosts to `pypi.org` and artifact hosts to
   `files.pythonhosted.org`, rejects userinfo/nonstandard ports and redirects,
   applies explicit connection/read timeouts and bounded API/artifact response
   sizes, requires PyPI JSON and Simple JSON to agree on release inventory,
   version, filename, URL, size, SHA-256, and yanked state, and requires
   downloaded bytes to match those sizes and hashes;
3. independently discovers the greatest newer stable non-yanked release below
   `0.5.0` and whether any stable non-yanked release crosses that boundary;
4. requires the selected compatible release to contain one expected pure
   Python wheel and one sdist with normalized names, versions, sizes, and
   SHA-256 digests;
5. cryptographically verifies each downloaded file and its provenance with
   the pinned `pypi-attestations verify pypi --repository
   https://github.com/lanmogu98/llm-exec-core <file-url>` path, including
   signatures, certificate chain, transparency evidence, and subject digest;
   after cryptographic verification, it requires the Integrity route and
   signed subject to agree on project, version, filename, and SHA-256, then
   additionally requires claims for `.github/workflows/release.yml`,
   environment `pypi`, and the source SHA;
6. fails rather than falling back if the greatest otherwise eligible
   compatible release is malformed, incomplete, unprovenanced, or internally
   inconsistent;
7. freezes the verified candidate snapshot, runs a targeted
   `uv lock --upgrade-package "llm-exec-core==<candidate>"` without changing
   the declared range, then re-parses the final lock and requires its exact
   Core version, file URLs, sizes, and SHA-256 hashes to equal that snapshot;
   it rejects every production diff outside `uv.lock`; the only allowed
   package-node changes are the union of nodes reachable from Core in the old
   and proposed lock graphs, including every marker and source variant, so
   shared, added, and removed transitive dependencies have an unambiguous
   closure boundary;
8. owns branch `automation/update-llm-exec-core` and at most one active
   same-repository PR targeting `main`; a newer candidate advances the active
   PR with guarded force-with-lease semantics;
9. does not recreate a deliberately closed PR for the same candidate;
10. owns one assessment Issue keyed to boundary `>=0.5.0`; and
11. never approves, auto-merges, bypasses, or pushes to `main`.

It also checks the currently locked release. If that release or its exact
locked files become yanked, unavailable, or lose verifiable provenance, the
updater fails closed and creates or updates one deduplicated health Issue. A
newer valid compatible candidate may still be proposed, but the updater never
silently downgrades or rewrites the declared range as recovery.

Discovery, network parsing, cryptographic verification, and exact lock
planning run in a read-only job. It emits a checksummed candidate/lock plan
bound to the exact base SHA. Only the mutation job has `contents: write`,
`pull-requests: write`, `issues: write`, and `actions: write`; it revalidates
the artifact digest, plan, and unchanged `main` base before applying/pushing.
Candidate Core code is never installed, imported, or executed in that job.
Filenames, metadata, API JSON, and package descriptions are never evaluated as
shell code.

After a generated branch/PR exists, the updater explicitly dispatches
`.github/workflows/ci.yml` on that branch with
`return_run_details=true`, requires the dispatch response's HTTP 200 run
identity/URLs, and asserts event, branch, head SHA, all three job names, and
results. Any `gh` CLI path is pinned to a version supporting that response
contract. It does not rely on the PR event suppressed for
`GITHUB_TOKEN`-created PRs or on a timing-based run search.

Editor #42 closes after its implementation PR is merged and a fixture-backed,
non-mutating post-merge dry run succeeds. Tests cover absent/false activation,
non-`main` dispatch, yanked files, missing provenance, malicious metadata,
greatest-version failure, compatible-plus-boundary coexistence, one-PR
idempotency, deliberately closed candidates, candidate-discovery/lock
resolution races, cryptographically invalid provenance, hostile redirects or
URLs, oversized/slow responses, cross-API metadata conflicts, and
dependency-closure diff enforcement. Production remains inactive through
#44.

### 10. Actions-created PR setting — Editor #44

After reviewing every workflow permission, the maintainer enables **Allow
GitHub Actions to create and approve pull requests** while retaining read-only
default workflow permissions. The combined GitHub switch does not authorize
this workflow to approve anything; no approval or auto-merge code is present.

The activation variable remains absent or `false`, so this setting cannot race
a schedule into a production mutation. UI and Actions-permissions API readback
must agree. This setting-only Issue creates no PR and introduces no PAT, App
key, deploy key, provider secret, or PyPI token.

### 11. Next compatible version — Core #47

After Editor #39 has locked the first PyPI release and real new Core changes
have landed, prepare the next natural stable version above that release and
below `0.5.0`. Core #47 repeats #42's focused version-only contract: every
source/lock/package version agrees, the lock changes only the root version,
the version is absent from PyPI/tags, and exact-head Core CI/build/review pass.

The version may not be fabricated for the rehearsal. Core #47 is a native
parallel child blocked by Editor #39 and blocks Core #48. It authorizes no
publication or owner action.

### 12. Updater-rehearsal publication — Core #48

After both Core #47 and Editor #44 close, publish Core #47's exact
current-`main` SHA through the already proven Trusted Publishing workflow
under a separate maintainer dispatch and protected environment approval.
Repeat dry-run, public-index, file hash, non-yanked, cryptographic provenance,
publisher-claim, and Python 3.10/3.13 install evidence. A GitHub Release
remains optional and non-authoritative.

Core #48 is a second production use of the workflow, not a fake package or
fixture. A partial/bad version follows the same yank-and-supersede rules. It
blocks Editor #43 and must be followed immediately by that rehearsal. No other
compatible Core publication may intervene; if one does, stop and prepare a
fresh explicit rehearsal release rather than violating greatest-candidate
selection.

### 13. Production rehearsal — Editor #43

Use the greatest eligible newer stable Core version below `0.5.0`, which at
activation must be the just-published Core #48 version, not the initial PyPI
version already locked by Editor #39. Editor #43 depends natively on Core #48
(which itself depends on Editor #44) and coordinates the evidence without
authorizing or fabricating a Core release.

After all preconditions are re-read, the maintainer changes
`LLM_EXEC_CORE_UPDATER_ENABLED` from absent/false to `true`, records exact
readback, and owns either the next schedule or an explicit production
dispatch. Prove:

1. PyPI file hashes and exact Trusted Publisher provenance;
2. updater discovery and exactly one lockfile-only dependency PR;
3. explicit CI dispatch identity on the exact PR head;
4. Ruleset block while current-head checks are pending;
5. all three checks passing;
6. maintainer manual merge and green post-merge `main` CI; and
7. no dependency specifier widening and no GitHub Release dependency.

Use offline fixtures for the `>=0.5.0` path, including compatible and boundary
releases in the same discovery result. Do not create a fake public package
version or fake production assessment Issue.

Open a rollback PR that restores the preceding validated Core version in
`uv.lock`, let it reach green/mergeable Ruleset state, record evidence, and
close it unmerged unless rollback is actually needed. This exercises recovery
without deliberately leaving `main` behind.

## Failure and rollback semantics

- Source version, distribution metadata, filename, hash, provenance, registry,
  or lock mismatch fails closed before consumer mutation.
- Core validation failure creates no public version. A failed OIDC request
  introduces no long-lived credential to rotate.
- A partial, bad, or compromised PyPI version is yanked and superseded by a
  new version. It is not deleted as recovery; existing filenames and version
  content are never overwritten, skipped, or reused.
- If the PyPI name is claimed before first publication, stop the program and
  redesign; a pending publisher is not proof of reservation.
- Closing a generated Editor PR leaves the current dependency unchanged and
  suppresses recreation for the same candidate.
- Editor rollback selects the immediately preceding validated, available
  version through a normal lockfile PR, identical CI, and the Ruleset.
- Before updater recovery, set
  `LLM_EXEC_CORE_UPDATER_ENABLED=false`. Before publisher recovery, set
  `LLM_EXEC_CORE_PYPI_PUBLISH_ENABLED=false`, then disable the environment or
  revoke the Trusted Publisher if necessary.
- Direct `main` pushes, Ruleset bypass, mutable dependency sources, version
  reuse, `skip-existing`, and artifact replacement are never recovery
  mechanisms.

## Security boundaries

- No provider API keys, paid calls, PATs, PyPI tokens, or production
  environment files.
- Repository defaults are read-only. OIDC exists only in the minimal
  protected publish job; updater write scopes exist only in its gated mutation
  job.
- All external Actions are full-SHA pinned and uv is version-pinned.
- The protected environment and exact PyPI publisher identity are both
  required; neither substitutes for the other.
- Candidate Core code executes only in read-only Editor CI.
- PyPI API data, filenames, metadata, descriptions, and provenance documents
  are untrusted input until parsed and verified.
- Required Ruleset checks accept GitHub Actions as the expected source and
  apply to the PR's current head.
- No credential alternative or publisher broadening is introduced without a
  focused design and explicit maintainer approval.

## Non-goals

- Tracking Core `main`, a branch, a floating tag, or an unversioned artifact.
- Using GitHub Releases as Editor's dependency discovery or integrity source.
- Publishing Editor itself to PyPI.
- Bot approval, automatic merge, or Ruleset bypass.
- Live integration/provider tests in required CI.
- Core catalog/schema/pricing/execution-boundary work.
- Signed-commit or linear-history mandates.
- TestPyPI and a second Trusted Publisher.
- Automatic widening across `0.5.0`.

## Program completion criteria

The program is complete only when all thirteen native child contracts close
in dependency order, Project `Sequence` agrees, Editor #43 records exact
production and rollback evidence, and Epic #38's acceptance checklist passes.
Until then, each child Issue is the only authority for its bounded
implementation or owner action.

## PyPI pivot corrections incorporated

The 2026-07-23 pivot removes the failure-prone direct GitHub asset path and:

- makes PyPI the authoritative package source and restores standard dependency
  metadata;
- replaces Release immutability and an Administration-reading GitHub App with
  PyPI's non-reusable files, OIDC identity, and per-file provenance;
- separates workflow implementation, GitHub environment protection, version
  preparation, PyPI publisher registration, and first publication into five
  ordered Core gates;
- keeps the exact workflow/environment identity narrow and removes all
  long-lived publishing credentials;
- makes Core #43 meaningful by repurposing it from GitHub App provisioning to
  pending Trusted Publisher registration;
- preserves the `<0.5.0` explicit-assessment boundary while allowing routine
  compatible lock-only PRs;
- changes Editor's integrity SSOT from a manually copied URL fragment to
  `uv.lock` registry file hashes plus PyPI Integrity API provenance;
- removes every GitHub Release immutability/App prerequisite from the critical
  path;
- handles the pending-publisher name-race by preparing the version first and
  registering/publishing in one owner operation window;
- makes the real second compatible Core release an explicit two-Issue native
  lane instead of an untracked prerequisite for the final rehearsal;
- handles partial public uploads, yanks, and non-reusable filenames without
  unsafe `skip-existing`; and
- preserves activation kill switches, explicit CI dispatch, one-PR
  idempotency, Ruleset enforcement, and rollback rehearsal.

## External references

- [PyPI: Creating a project with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
- [PyPI: Publishing with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
- [PyPI: Trusted Publishing security model](https://docs.pypi.org/trusted-publishers/security-model/)
- [PyPI: Producing attestations](https://docs.pypi.org/attestations/producing-attestations/)
- [PyPI: Integrity API](https://docs.pypi.org/api/integrity/)
- [PyPI Help: file and filename reuse](https://pypi.org/help/)
- [GitHub: OIDC in PyPI](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-pypi)
- [GitHub: Deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
- [GitHub: `GITHUB_TOKEN` event behavior](https://docs.github.com/en/actions/concepts/security/github_token)
- [GitHub: Triggering workflows](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
- [GitHub: Required ruleset checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [Python Packaging: Dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
- [Python Packaging: Version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/)
- [uv: Project dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)
