# Autonomous Bioelectronic Nanomicrosystem Design

You are an autonomous research agent. Your goal: design one compelling biomedical nanotechnology/microsystem system with strong scientific plausibility and high performance under the provided evaluation specs.

**Recommended system to pursue:** a **closed-loop implantable bioelectronic nanomicrosystem** that combines:
- nanoscale sensing of biochemical state,
- microfluidic transport and buffering,
- adaptive signal processing,
- feedback-controlled actuation or release,
- failure-aware behavior under drift, fouling, saturation, and noise.

This is the most interesting target because it naturally integrates sensing, transport, control, and biointerface dynamics in one architecture.

---

## Philosophy

**You are the modeler and system designer.** Optimization is a tool, not the goal.

- You decide **what model topology** to use
- You decide **whether an optimizer is needed**, and if so, how to structure the search
- You NEVER manually set parameter values — define ranges, let the optimizer find them
- When optimization converges but specs fail, change the model
- When all specs are met, you are done

Think like a biomedical nanotechnology researcher:
- prioritize physically plausible mechanisms
- favor modularity: sensing, transport, reaction, feedback, and failure modes
- search for architectures that can represent implantable sensors, lab-on-chip interfaces, drug-delivery microsystems, and bioelectronic control loops
- prefer models that capture nanoscale surface effects, microscale transport, and system-level adaptation

---

## Files

| File | Role | Edit? |
|------|------|-------|
| `model.py` | **Your model. Design the equations here.** | YES |
| `parameters.csv` | **Parameter ranges (name,min,max,scale)** | YES |
| `specs.json` | Target specs | NO |
| `evaluate.py` | Evaluation and optimization harness | NO |
| `results.tsv` | Experiment log | APPEND |
| `program.md` | These instructions | NO |

---

## The Experiment Loop

Run forever until all specs are met.

### 1. Evaluate
Use the evaluation harness exactly as provided.

- Start with a quick run if available for sanity checking
- Then run the full evaluation

```bash
python3 evaluate.py --quick
python3 evaluate.py
```

If the harness supports multiple optimizers or search modes, use the one that best fits the current model. Do not assume DE is always the right choice.

### 2. Analyze
Read the output carefully. For each spec:
- **OK** = within tolerance
- **XX** = outside tolerance — diagnose the failure mode

When analyzing failures, think in terms of biomedical nano/microsystem behavior:
- insufficient sensitivity or dynamic range
- poor selectivity or cross-talk
- slow transport or diffusion-limited response
- unstable feedback or oscillation
- saturation, hysteresis, drift, or noise amplification
- weak coupling between sensing and actuation
- unrealistic scaling across micro/nano regimes
- fouling, leakage, degradation, or recovery failure

### 3. Decide
**If all specs are met:**
- Update `README.md` with the final result
- Commit: `git add -A && git commit -m "SOLVED | <system description>"`
- Stop

**If any spec fails:**
- Identify which specs fail and why
- Decide whether the issue is:
  - parameter range problem
  - missing mechanism
  - wrong topology
  - insufficient nonlinearity
  - missing feedback or buffering
  - poor timescale separation
- Modify `model.py` and/or `parameters.csv`
- Commit: `git add -A && git commit -m "topology: <what changed>"`
- Go back to step 1

---

## Design Strategy

Use a biomedical nanotechnology and microsystems mindset.

### Recommended system architecture
Build around a **closed-loop implantable bioelectronic nanomicrosystem** with these modules:

1. **Nanosensor interface**
   - biochemical binding or transduction
   - surface functionalization
   - selectivity and cross-talk suppression
   - drift and fouling terms

2. **Microscale transport layer**
   - diffusion/advection or effective transport delay
   - buffering and residence time
   - capture and release dynamics

3. **Signal conditioning**
   - filtering
   - thresholding
   - gain control
   - saturation handling

4. **Feedback actuation**
   - drug release
   - stimulation
   - gating
   - adaptive control

5. **Failure-aware adaptation**
   - degradation
   - recovery
   - leakage
   - compensation for drift and noise

### Model-building rules
- Start with the simplest topology that can plausibly satisfy the specs
- If convergence stalls, increase expressiveness by adding:
  - nonlinearities
  - coupled states
  - saturation terms
  - feedback loops
  - multi-timescale dynamics
- Keep equations interpretable and physically motivated
- Use dimensionless or normalized states when helpful
- Ensure parameter ranges are broad enough for search, but not so broad that search becomes random
- If a spec is about speed, add time constants or transport terms
- If a spec is about accuracy, add calibration, filtering, or selectivity structure
- If a spec is about robustness, add damping, redundancy, or negative feedback
- If a spec is about efficiency, add resource/power/energy penalties and optimize tradeoffs

---

## Optimization Policy

Do **not** assume one optimizer is sufficient.

- Use the optimizer built into `evaluate.py` if it is appropriate
- If the harness supports alternative search strategies, choose the one most suitable for the current failure mode
- If the model is smooth and low-dimensional, a global optimizer may be enough
- If the model is multimodal, stiff, or highly coupled, prefer a more robust search strategy
- If the search repeatedly converges to poor local optima, change the topology before increasing search effort

**Important:** optimization is secondary to model design. The agent should decide when to rely on optimization and when to redesign the system.

---

## Rules

- Edit ONLY `model.py` and `parameters.csv`
- NEVER modify `evaluate.py`, `specs.json`, or `program.md`
- NEVER hardcode parameter values — use `params` dict + `parameters.csv`
- ALWAYS commit before running evaluation
- NEVER stop until all specs are met
- NEVER give up early because one optimizer failed
- If the current approach stalls, redesign the model rather than forcing the same topology

---

## Practical Guidance

When a model fails, diagnose the failure mode before changing topology:

- **Too slow** → reduce transport resistance, shorten time constants, increase coupling
- **Too noisy / unstable** → add damping, filtering, or negative feedback
- **Too weak** → increase gain, surface coupling, or amplification
- **Too saturated** → add nonlinear compression or wider operating range
- **Too brittle** → add redundancy, buffering, or adaptive thresholds
- **Poor selectivity** → add competing pathways or discrimination terms
- **Poor recovery** → add reversible binding or regeneration dynamics
- **Poor closed-loop control** → strengthen sensor-to-actuator coupling and add state estimation
- **Poor implant compatibility** → add drift compensation, fouling resistance, and bounded actuation

Prefer changes that improve multiple specs at once.

---

## End Condition

You are done only when:
- every spec is satisfied
- the model is stable and interpretable
- the final design reflects a credible biomedical nanomicrosystem architecture
- the solution is robust enough that further optimization is unnecessary

Then commit the solution and stop.