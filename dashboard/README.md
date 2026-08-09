# CyberLab Command Center

Local, dependency-free dashboard for tracking the CyberLab repository from Termux.

## What it shows

- discovered LAB folders
- completed/in-progress lab state
- count of `VERIFIED` markers in `observations.md`
- roadmap phase status
- current Git branch and dirty/clean working tree state
- recent commits
- Red Team / Victim / Blue Team learning model

The dashboard is read-only. It does not run scans, execute labs, modify files, or contact remote systems.

## Run on Termux

From the repository root:

```bash
python dashboard/serve.py
```

Then open this address in the tablet browser:

```text
http://127.0.0.1:8765
```

Stop with `Ctrl+C`.

## Security model

The web server binds only to `127.0.0.1`, so it is not exposed to the Wi-Fi/LAN interface.

The `/api/status` endpoint reads only local repository metadata and lab documentation. It uses Python's standard library plus local `git` commands.

## Data detection

A directory matching `lab-<number>-...` is discovered automatically. A lab is currently considered complete when both `README.md` and a non-empty `observations.md` exist. The UI counts explicit `VERIFIED` markers in the observations file.

This heuristic can later be replaced by structured `lab.json` manifests without changing the dashboard design.
