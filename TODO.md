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
| 4 | `lab/` removed from blt, pointing here | | |

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

3. **A login of the lab's own.** A Commvault user for the lab on
   cv-toaster, with an access token and refresh token, in
   `config/cv-toaster.env` here. Until then the lab runs on blt's token
   file through `CV_LAB_CONFIG_DIR` (README, "Connecting"). Done in
   Command Center, by hand.

4. **Out of blt.** In `blt-v5-poc`, on its release branch: remove
   `lab/` and `docs/lab-noise.md`, and point its README, `TODO.md`,
   `docs/commvault-sdk.md`, `docs/blt-flow.md` and
   `docs/production-setup.md` here. `lab/media` and `lab/.state` were
   copied here (media hard-linked), so removing blt's copy frees
   nothing until both are gone.

## The rig

5. **Files that vanish mid-backup.** A stage that gives a container
   client a subclient over a folder of a few thousand files, starts a
   backup, waits for it to leave the scan phase, then deletes files,
   folders and a large batch. Produces what the lab cannot today:
   - files and folders that failed in the backup phase, not the scan,
     for the SDK's `jobs.failed_items()` (its TODO item 6), and a long
     list, to see whether Commvault cuts it short or turns
     `isFailedItemsCSV` on;
   - a running job to watch, for the SDK's item 7;
   - a dependable "Completed w/ one or more errors" for blt.

6. **A file in use on Windows.** A file held open with no sharing on the
   CommServe, under a subclient with VSS turned off, gives the realistic
   "being used by another process" failure. Needs a process started on
   the VM by hand; optional.

7. **Live tests for the SDK.** An opt-in suite here that runs the SDK's
   calls against the lab and checks what comes back against what the lab
   did - step 2 of the SDK's Friday test, instead of scratch scripts.

8. **The `blt-lab-` prefix.** Kept so teardown finds what exists. If it
   is ever renamed, teardown has to know both names for a while.
