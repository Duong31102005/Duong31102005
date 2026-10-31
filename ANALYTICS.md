# Analytics methodology

Snapshot: **2026-10-31T05:37:40Z**. Window: **2026-04-30T17:00:00Z** through the snapshot timestamp.

- Scope: the seven explicitly selected public project repositories linked in the profile. The profile repository and private repositories are excluded.
- Owned repository means hosted under `Duong31102005`; it does not claim sole authorship. Team repositories belong to `namp12` and are projects the profile owner participates in.
- Commits come from GitHub REST `/repos/OWNER/REPO/commits`, filtered with `author=Duong31102005` on each default branch. All pages are read. Only author timestamps within the window are counted.
- Overall charts deduplicate commit SHA across repositories. Per-project counts are specific to that repository. This is a scoped activity view, not GitHub's full contribution-calendar total.
- Hours, weekdays, and active days use author timestamps converted to UTC+07:00. These timestamps do not measure working hours or productivity.
- Language charts sum GitHub `/languages` byte counts separately for owned and team repositories, excluding forks. They describe repository contents, including code from teammates and any detectable vendored/generated files; they do not represent individual contribution shares or skill ratings. Empty language responses are retained as empty, not estimated.
- The window covers six calendar months including the current partial month. Failed API reads stop the update and preserve the previous published snapshot.

[Source data](data/metrics.json) · [Refresh script](scripts/update_profile.py)

## Repository activity

| Repository | Your commits | Repository last pushed (UTC) | Code bytes |
|:---|---:|:---|---:|
| [Duong31102005/AI_Robot](https://github.com/Duong31102005/AI_Robot) | 39 | 2026-08-07T01:02:52Z | 184,660 |
| [namp12/robot_main](https://github.com/namp12/robot_main) | 106 | 2026-08-21T02:06:22Z | 1,388,985 |
| [namp12/Robot_web](https://github.com/namp12/Robot_web) | 56 | 2026-08-07T01:03:00Z | 411,845 |
| [namp12/Robot_Tu_Hanh](https://github.com/namp12/Robot_Tu_Hanh) | 31 | 2026-08-06T22:06:13Z | 304,249 |
| [namp12/cang_tin_truong_hoc](https://github.com/namp12/cang_tin_truong_hoc) | 0 | 2026-08-28T12:05:58Z | 884,822 |
| [Duong31102005/btl_Nhom11](https://github.com/Duong31102005/btl_Nhom11) | 0 | 2026-06-28T13:36:16Z | 420,154 |
| [Duong31102005/Quan-li-khoa-hoc](https://github.com/Duong31102005/Quan-li-khoa-hoc) | 0 | 2025-07-01T15:30:58Z | 0 |
