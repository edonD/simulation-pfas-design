# simulation-pfas-design

You are an autonomous research agent. Your goal: ai abilitiy to simulate pfas design without using cad tools

---

## Philosophy

**You are the modeler. DE is your optimizer.**

- You decide **what model topology** to use
- DE decides **what parameter values** to use
- You NEVER manually set parameter values — define ranges, let DE find them
- When DE converges but specs fail, change the model
- When all specs are met, you are done

---

## Files

| File | Role | Edit? |
|------|------|-------|
| `model.py` | **Your model. Design the equations here.** | YES |
| `parameters.csv` | **Parameter ranges (name,min,max,scale)** | YES |
| `specs.json` | Target specs | NO |
| `evaluate.py` | DE optimizer + scorer | NO |
| `results.tsv` | Experiment log | APPEND |
| `program.md` | These instructions | NO |

---

## The Experiment Loop

Run forever until score = 100%:

### 1. Evaluate
```bash
python3 evaluate.py --quick     # fast sanity check (50 gens)
python3 evaluate.py             # full run (300 gens)
```

### 2. Analyze
Read the output. For each spec:
- OK = within 5% of target
- XX = outside 5% — diagnose why

### 3. Decide
**If score = 100%:**
- Update README.md with results
- Commit: `git add -A && git commit -m "SOLVED | <model description>"`
- Stop

**If score < 100%:**
- Identify which specs fail and why
- Modify `model.py` and/or `parameters.csv`
- Commit: `git add -A && git commit -m "topology: <what changed>"`
- Go to step 1

---

## Rules

- Edit ONLY `model.py` and `parameters.csv`
- NEVER modify `evaluate.py`, `specs.json`, or `program.md`
- NEVER hardcode parameter values — use params dict + parameters.csv
- ALWAYS commit before running DE
- NEVER stop until score = 100%
