# yoki-commvault-lab

A lab rig that makes a Commvault CommServe produce real jobs, with real
outcomes - completed, failed, killed, suspended, files that could not be
read - so that the things built on Commvault can be tested against the
real thing rather than against what we think it returns:

- **the Commvault SDK** (`yoki-py-commvault-sdk`): a new call is run in
  the lab before it is committed, and every call added in a week is run
  again in Friday's test;
- **blt** (`blt-v5-poc`): its collection, delta and reconcile logic, on
  jobs whose outcome is known because the lab caused it.

It began as `lab/` inside blt (2026-10-06) and moved here with its
history on 2026-10-14, so that it can grow for both.

The lab CommServe is `cv-toaster`, Commvault's eval OVA (11 SP46.30).
Everything the lab creates there is named `blt-lab-*` - the prefix from
its blt days, kept so that teardown still finds what is already there.

## What is in it

| Script | What it does | Changes the CommServe |
|---|---|---|
| `lab/00-preflight.sh` | Looks: version, agent, plan, storage, lab subclients, active jobs | no |
| `lab/10-setup.sh` | Creates the `blt-lab-*` subclients on the CommServe's own client | yes |
| `lab/20-noise.sh` | A round of backups that end differently (`--loop MIN` to repeat) | yes |
| `lab/30-clients.sh` | Podman containers on this machine as extra Linux clients (`--count N`) | yes |
| `lab/40-sql.sh` | A SQL Server client in a container (`--databases N`) | yes |
| `lab/45-sql-backup.sh` | Backs up its databases (`--levels Full,...`) | yes |
| `lab/50-sql-validate.sh` | Compares SQL Server's databases with what Commvault has backed up | no |
| `lab/90-teardown.sh` | Removes everything named `blt-lab-*` | yes |

Each takes an optional CommCell name (default `cv-toaster`).
`docs/lab-noise.md` is the full guide: what each stage creates, the
container images (`lab/client-image`, `lab/sql-image`), the install
media in `lab/media` (several GB, not in git), and what each run so far
has shown.

`src/commvault_lab/` is how the lab connects; `lab/cvlab.py` is the rig
itself.

## Connecting

The lab reads `config/<commcell>.env`, in the same format as blt's
files (`config/commcell.env.example`). With an access token and its
refresh token it renews the token itself and writes the new pair back
to that file, under a lock - the same code as blt's.

**The lab should have a login of its own.** Renewing a token replaces
the pair on the CommServe, so a token copied from blt's file and renewed
here leaves blt holding a dead one, and the other way round. Until the
lab has its own login and token, do not copy blt's file - point the lab
at blt's config directory instead, so that both renew the one file and
take turns through the one lock:

```
export CV_LAB_CONFIG_DIR=~/development/blt-v5-poc/config
lab/00-preflight.sh
```

(or `--config-dir` on any script). Once the lab has its own token, put
it in `config/cv-toaster.env` here and drop the variable.

## The SDK it runs

`pyproject.toml` takes `commvault-sdk` from the sibling checkout
`../yoki-py-commvault-sdk`, editable: the lab is where the SDK's new
calls are proven before they are released, so it runs whatever branch
that checkout is on. The comment beside it has the line for running
against a released tag instead.

## Development

```
uv sync
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run pytest
```

The tests cover the connection code (token write-back, locks); the rig
itself is proven by running it against the lab, and each run's findings
go in `docs/lab-noise.md`.

## Releases

The same weekly cadence as blt and the SDK, and the same branch names -
see the SDK's docs/development.md, "Releases", for the whole of it. In short: work
for the week goes on branches `<release>/F|B|H/<What_it_does>` off
`release/<release>` (named for the Monday it is released, e.g.
`2026.10.W03`), merged back with `--no-ff` by Thursday, tested Friday,
merged to `main` and tagged on Monday. Branches are deleted locally once
merged and from GitHub a month after their release. Commit small, with
tests where there is something to test, and say in each commit what
running it against the lab showed.

`docs/failure-catalogue.md` lists the ways a backup can fail, the
codes Commvault gives them, and which ones the lab can cause.

`TODO.md` has what is open.
