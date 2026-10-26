# Start the Demonstration Server

The server must be started from the **repository root**: the folder that contains `src/`, `README.md`
and `requirements.txt`. Running it from `src/` or from a parent folder will fail.

## Windows (this machine)

```bat
cd C:\Uni\Emerging Trends\Capstone Project\repo_live
python src\web_ui.py
```

Expected output:

```text
====================================================================
 Group A Day | Student Support Case Agent | demonstration UI
 Planner: scripted | Student: 2300701098
 URL: http://127.0.0.1:7860/
 Synthetic data only. Press Ctrl+C to stop.
====================================================================
```

Open **http://127.0.0.1:7860/** in a browser. The browser usually opens automatically.

## Any machine after cloning

```bash
git clone https://github.com/OpiyoOscar01/group_A_ai_agentic_capstone_assignment.git
cd group_A_ai_agentic_capstone_assignment
python src/web_ui.py
```

## Mode and dependencies

- **Default is scripted mode.** It is deterministic and needs no API key and no third-party packages.
- **Live Gemini mode is optional:**

  ```bat
  pip install -r requirements.txt
  set GEMINI_API_KEY=your-key-here
  python src\web_ui.py --planner gemini
  ```

- The server tries ports `7860` to `7869` and prints the URL it actually uses. Use the printed URL.

## Stop the server

Press `Ctrl+C` in the terminal. If it was started in the background:

```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 7860).OwningProcess
```

## Common errors

| Error | Cause | Fix |
|---|---|---|
| `can't open file ... src\web_ui.py` | Wrong working directory | `cd` to the repository root first |
| `no free port in range` | Ports 7860-7869 are occupied | Close the other servers, then retry |
| `ModuleNotFoundError: google.generativeai` | Live mode without dependencies | Run scripted mode, or `pip install -r requirements.txt` |
| Empty or stale conversation | Previous demo state | Press **Reset demo data and conversation** |

The full presenter sequence is in [`demo/DEMO_GUIDE.md`](demo/DEMO_GUIDE.md).
