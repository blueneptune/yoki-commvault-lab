# Failure catalogue

The ways a Commvault backup can fail, which of them this lab can make
happen on purpose, and what each one is for. A scenario here becomes a
lab command (`lab/60-fail.sh <id>`, TODO item 9) that causes the
failure, waits for the job to end, and records what Commvault said - so
the Commvault SDK can prove its job calls on that failure and blt has a
job whose right answer is known.

Started 2026-10-14. Nothing in the "To produce" table has been run yet.

## Where the codes come from

Commvault writes an error code as two numbers, `19:1132`: the first is
the component that raised it (19 is the Job Manager, 17 file system
scan, 30 the database agents, 32 media management, 82 data transfer),
the second the error. It does not publish one list of them. Each code
has its own article in the knowledge base (kb.commvault.com), and some
appear on the per-agent troubleshooting pages of the documentation. The
SDK reads the code as `Job.pending_reason_code` and in
`JobExplanation.reason_codes`.

So each row below says where its code came from:

- **lab** - seen on cv-toaster (11 SP46.30), with the job count.
- **KB** / **docs** - Commvault documents it for this situation; not
  seen here yet. A KB link was found by search and not read in full
  (the knowledge base does not serve pages to scripted fetches).
- **?** - the situation is real but the code is not known; the lab
  will find out.

The one-line descriptions are ours, not Commvault's text. Commvault's
own wording for a job is in its reason (`Job.reasons`).

## Seen in the lab

From the listing of all 303 lab jobs, 2026-10-14.

| Code | Status | What | Jobs | How the lab caused it |
|---|---|---|---|---|
| `19:1132` | Failed to Start | Another backup already running for the same database subclient ([KB 54113](https://kb.commvault.com/article/54113)) | 28 | SQL backups started on top of each other |
| `19:2586` | Failed to Start | Another backup job already running for the same file-system subclient | 14 | Noise rounds on container clients overlapping |
| `17:158` | Failed | Configured content does not exist (scan fails) | 12 | `blt-lab-missing` |
| `19:861` | Killed | Killed by an administrator | 5 | Noise rounds with `drama` |
| (none) | Committed | Killed after some data was already written | 2 | Noise rounds with `drama` |
| `19:601` | Completed w/ one or more errors | Job Manager service restarted under the job | 1 (DR backup) | The VM restarting - not on purpose |
| `19:2571` | Failed / Failed to Start | Data aging refused after the system clock changed | 3 (data aging) | The VM's clock being fixed - not on purpose |
| `13:63` | Failed | A CommServe database query failed | 2 (DDB verification) | Not on purpose |

The 42 jobs that failed to start also carry `jobSubmitErrorCode` 8 in
their summary; what 8 means is not known.

## To produce

**P** is priority: 1 first. **Risk** is to the lab, and what undoes it.

| ID | Scenario | How the lab would cause it | Expected status and code | P | Risk / undo |
|---|---|---|---|---|---|
| F01 | Client unreachable at start | Stop a container client, then start its backup | Pending, then Failed; `30:388` failed to start backup on agent ([KB 54306](https://kb.commvault.com/article/54306)) or `19:1131` waiting for services (docs) | 1 | Low; start the container |
| F02 | Client lost mid-backup | Pause or disconnect a container once its backup is in the backup phase | Pending, retried; `82:142` connection closed ([KB 54231](https://kb.commvault.com/article/54231)) or `19:1597` phase failed on network error (docs); killed with `19:1924` after the client's maximum offline time ([KB 64068](https://kb.commvault.com/article/64068)) | 1 | Low; resume or reconnect |
| F03 | Too many restarts | F02 repeated within one job until the attempts run out | Failed; `19:1253` number of restarts exceeded the maximum ([KB 54299](https://kb.commvault.com/article/54299)) | 2 | Low |
| F04 | Files vanish mid-backup | Item 5: delete files and folders after the scan has listed them | Completed w/ one or more errors; ? | 1 | Low; nothing to undo |
| F05 | Many failed files | F04 with a few thousand files | Completed w/ one or more errors; ? - does `failed_items()` cut the list short or go to CSV? | 1 | Low |
| F06 | Content missing | Already: `blt-lab-missing` | Failed; `17:158` (lab). Older releases document `17:11` for the same thing | - | Exists |
| F07 | Another backup running | Already: start a backup on a subclient that has one running | Failed to Start; `19:2586` / `19:1132` (lab) | - | Exists |
| F08 | Killed by an administrator | Already: noise rounds | Killed; `19:861` (lab) | - | Exists |
| F09 | Suspended, then resumed | Already: noise rounds | Completed, with a suspended attempt (`explain()` not `clean`) | - | Exists |
| F10 | SQL database offline | `cvlab.py sql-offline`, then back up the instance | Completed w/ one or more errors or Failed; ? | 2 | Low; `sql-online` |
| F11 | SQL login refused | Give the SQL instance a credential with a wrong password, then back up | Failed; ? | 2 | Low; set the right credential back |
| F12 | SQL login without sysadmin | A credential whose login lacks the sysadmin role | Failed; `30:436` insufficient SQL Server role (docs) | 3 | Low; set the right credential back |
| F13 | SQL log backup with no full | Log backup of a database that has never had a full | Converted to a full - not a failure; the requested and run levels differ (`JobTask.requested_level`) | 2 | Low |
| F14 | SQL log backup in simple recovery | Log backup of a database set to simple recovery | Skipped or Failed for that database; ? | 2 | Low; set full recovery back |
| F15 | SQL database in use | A database held in single-user mode by another session during backup | Failed for that database; ? (docs: concurrency restriction) | 3 | Low; end the session |
| F16 | Job timeout | A subclient or plan job timeout shorter than the backup | Killed or Failed; ? (docs: SQL0008, SQL0014) | 3 | Medium: a plan setting; set it back |
| F17 | Storage unreachable | Take the disk library's mount path offline, start a backup | Pending; `32:406` device not accessible to the MediaAgent ([KB 53870](https://kb.commvault.com/article/53870)) | 3 | **Medium**: the only storage in the lab; every backup waits until it is back |
| F18 | Data path disabled | Disable the plan's data path | Pending; `32:406` data path is disabled ([KB 53882](https://kb.commvault.com/article/53882)) | 3 | Medium; enable it |
| F19 | Storage full | A mount path with a small reserve | Pending; `32:406` mount path does not have enough space ([KB 53880](https://kb.commvault.com/article/53880)) | 4 | **High**: easy to leave the lab unable to back up |
| F20 | Deduplication database unavailable | Stop or mark the DDB offline | Pending; `40:120` SIDB in incorrect state ([KB 53993](https://kb.commvault.com/article/53993)) | 4 | **High** |
| F21 | VSS snapshot fails (Windows) | Too little shadow storage, or a stopped VSS service, on the CommServe | Failed or with errors; `17:55` failed to create VSS snapshot (docs) | 4 | Medium; on the CommServe itself |
| F22 | File in use (Windows, VSS off) | Item 6: a file held open with no sharing | Completed w/ one or more errors; ? | 3 | Low; by hand on the VM |
| F23 | Blackout window | An operation window over the time of the backup | Queued or Failed to Start; ? | 3 | Medium: a CommCell or plan setting |
| F24 | Job Manager restarted | Restart the CommServe's services during a backup | Completed w/ errors or Failed; `19:601` (lab, on a DR backup) | 4 | **High**: stops every job in the CommCell |

Not planned, because the lab cannot cause them safely or at all:
authentication between client and CommServe (`9:38` to `9:42`, `9:90`),
corrupted media (`13:127`, `62:469`), tape libraries, and virtual
machine and cloud agents (no hypervisor or cloud account here).

## What each run records

For each scenario run, the stage writes the job id and what Commvault
said, so it can go in the table above and in `docs/lab-noise.md`:

- the job's status, `pending_reason_code` and reason text from the
  listing (`Job`);
- `explain()`: reasons, codes, incomplete attempts, major events;
- `attempts()`, `events()`, and `failed_items()` for F04, F05 and F22;
- what blt collected for the job, when blt is pointed at the lab.

A row moves from **?** or **KB**/**docs** to **lab** when it has been
seen here, with the date and job ids. A scenario whose code differs
from the documented one keeps both.
