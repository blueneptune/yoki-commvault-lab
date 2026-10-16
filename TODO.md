# TODO

What has been worked on and what is open. A done item is struck through
and names the commit it was done in and the release branch that
commit is on.

## Setting up the repository

| | Item | Commit | Release |
|---|---|---|---|
| ~~1~~ | ~~Stand-alone: own connection code, project, README~~ | `58a5e90`, `084724e`, `6c2ece3` | 2026.10.W03 |
| ~~2~~ | ~~On GitHub~~ | | 2026.10.W03 |
| 3 | A login of the lab's own on cv-toaster | | |
| ~~4~~ | ~~`lab/` removed from blt, pointing here~~ | blt `d8c6c84` | blt 2026.10.W03 |

1. ~~**Stand-alone.**~~ **Done 2026-10-14.** The lab's five commits from blt, replayed here with
   their authors and dates; then its own copy of blt's settings, token
   write-back and lock code (`src/commvault_lab/`), its own
   `pyproject.toml` taking the SDK from the sibling checkout, and this
   repository's README. Branch `2026.10.W03/F/Standalone_lab`.
   Preflight run against cv-toaster from here, on blt's token file:
   passed, and the token renewal it did on the way was saved to
   blt's file correctly.

2. ~~**On GitHub.**~~ **Done 2026-10-14.**
   `git@github.com:blueneptune/yoki-commvault-lab.git`, created by hand
   (no `gh` on this machine); `main`, `release/2026.10.W03` and
   `2026.10.W03/F/Standalone_lab` pushed.

3. ~~**A token of the lab's own.**~~ **Done 2026-10-16**: an access
   token and refresh token of its own for cv-toaster, created in
   Command Center, in `config/cv-toaster.env` here; proven read-only
   the same day. Needed now rather than later: blt's cv-toaster token
   moved into its Prefect block, so the copy in
   `blt-v5-poc/config/cv-toaster.env` went stale and
   `CV_LAB_CONFIG_DIR` pointed at it no longer works.

4. ~~**Out of blt.**~~ **Done 2026-10-14**, blt `d8c6c84`, merged into
   blt's `release/2026.10.W03`. In `blt-v5-poc`, on its release branch: remove
   `lab/` and `docs/lab-noise.md`, and point its README, `TODO.md`,
   `docs/commvault-sdk.md`, `docs/blt-flow.md` and
   `docs/production-setup.md` here. `lab/media` and `lab/.state` were
   copied here (media hard-linked), so removing blt's copy frees
   nothing until both are gone.

## The rig

5. **Files that vanish mid-backup** (catalogue F04, F05). A stage that gives a container
   client a subclient over a folder of a few thousand files, starts a
   backup, waits for it to leave the scan phase, then deletes files,
   folders and a large batch. Produces what the lab cannot today:
   - files and folders that failed in the backup phase, not the scan,
     for the SDK's `jobs.failed_items()` (its TODO item 6), and a long
     list, to see whether Commvault cuts it short or turns
     `isFailedItemsCSV` on;
   - a running job to watch, for the SDK's item 7;
   - a dependable "Completed w/ one or more errors" for blt.

6. **A file in use on Windows** (catalogue F22). A file held open with no sharing on the
   CommServe, under a subclient with VSS turned off, gives the realistic
   "being used by another process" failure. Needs a process started on
   the VM by hand; optional.

7. **Live tests for the SDK.** An opt-in suite here that runs the SDK's
   calls against the lab and checks what comes back against what the lab
   did - step 2 of the SDK's Friday test, instead of scratch scripts.

8. **The `blt-lab-` prefix.** Kept so teardown finds what exists. If it
   is ever renamed, teardown has to know both names for a while.

## Failure catalogue

`docs/failure-catalogue.md`: the ways a backup can fail, the codes
Commvault gives each (from the lab, or from its knowledge base and
documentation where not seen here yet), and which ones the lab can
cause on purpose - F01 to F24, with a priority and the risk of each.
Requested 2026-10-14. Purpose: a known, repeatable failure for each
kind, so the SDK's job calls are proven on it and blt's answer for it
can be checked.

9. **A failure stage: `lab/60-fail.sh <id>`.** One command per
   catalogue scenario that causes the failure, waits for the job to
   end, undoes what it changed, and records the job id, status, code,
   reasons, attempts, events and failed items (catalogue, "What each
   run records"). Each scenario's undo is part of it, and runs even when
   the scenario fails. Built once, then a scenario at a time.

10. **Priority 1: F01, F02, F04, F05.** Client unreachable at start,
    client lost mid-backup, files vanishing mid-backup, many failed
    files. All on container clients, all undone by restarting or
    reconnecting a container. Between them they prove the SDK's
    `failed_items()` on backup-phase failures (its item 6) and give it
    running and pending jobs (its item 7) - the pending-and-retried path
    has not been seen at all yet.

11. **Priority 2: F03, F10, F11, F13, F14.** Too many restarts, and the
    SQL Server scenarios - mostly on the SQL container, using
    `sql-offline` / `sql-online` and the instance credential that exist.

12. **Priority 3 and 4: the rest.** Storage, deduplication, VSS, job
    timeouts, blackout windows, a Job Manager restart. Each changes
    something the whole lab depends on, so each is run only with its
    undo checked first, and F19, F20 and F24 only if they are wanted.

13. **Codes from the catalogue into the SDK.** Once codes are seen
    here, a table of them in the SDK's guide ("Why a job failed"), so a
    caller can tell an unreachable client from a full disk by
    `pending_reason_code` without reading reason text. Not a lookup of
    every Commvault code - the ones the lab has proven.

