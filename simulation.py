from __future__ import annotations

from typing import Dict, List, Any
import numpy as np
import pandas as pd


# -----------------------------
# Defaults (edit these anytime)
# -----------------------------
DEFAULT_CONFIG: Dict[str, Any] = {
    "n_patients": 2000,
    "seed": 7,
    "max_attempts": 5,
    "lambda_per_week": 40.0,
    "populations": {
        "Population 1": {"weight": 0.25},
        "Population 2": {"weight": 0.25},
        "Population 3": {"weight": 0.25},
        "Population 4": {"weight": 0.25},
    },
    # Global method touchpoints (used for all populations)
    "avg_touchpoints_by_method": {
        "Method 1": 2.0,
        "Method 2": 3.0,
        "Method 3": 1.0,
        "Method 4": 4.0,
        "Method 5": 2.0,
    },
    # Global allocated time per visit category
    "allocated_minutes_by_visit_category": {
        "VisitCat 1": 15,
        "VisitCat 2": 20,
        "VisitCat 3": 30,
        "VisitCat 4": 40,
        "VisitCat 5": 60,
        "VisitCat 6": 10,
    },
    # Per-population method distribution + probabilities + lognormal params
    # mu/sigma are lognormal mean/stdev in log-space
    "population_params": {
        "Population 1": {
            "methods": [
                {"method": "Method 1", "likelihood": 0.2, "p_schedule": 0.8, "p_complete": 0.85, "mu": 1.0, "sigma": 0.5, "mu2": 1.2, "sigma2": 0.55},
                {"method": "Method 2", "likelihood": 0.2, "p_schedule": 0.75, "p_complete": 0.8, "mu": 1.1, "sigma": 0.5, "mu2": 1.3, "sigma2": 0.6},
                {"method": "Method 3", "likelihood": 0.2, "p_schedule": 0.7, "p_complete": 0.75, "mu": 1.0, "sigma": 0.45, "mu2": 1.1, "sigma2": 0.55},
                {"method": "Method 4", "likelihood": 0.2, "p_schedule": 0.65, "p_complete": 0.7, "mu": 1.2, "sigma": 0.55, "mu2": 1.35, "sigma2": 0.65},
                {"method": "Method 5", "likelihood": 0.2, "p_schedule": 0.78, "p_complete": 0.82, "mu": 1.05, "sigma": 0.5, "mu2": 1.25, "sigma2": 0.6},
            ],
            "visit_categories": [
                {"category": "VisitCat 1", "prob": 0.2},
                {"category": "VisitCat 2", "prob": 0.2},
                {"category": "VisitCat 3", "prob": 0.2},
                {"category": "VisitCat 4", "prob": 0.2},
                {"category": "VisitCat 5", "prob": 0.1},
                {"category": "VisitCat 6", "prob": 0.1},
            ],
        },
        "Population 2": {
            "methods": [
                {"method": "Method 1", "likelihood": 0.25, "p_schedule": 0.75, "p_complete": 0.8, "mu": 1.1, "sigma": 0.55, "mu2": 1.3, "sigma2": 0.65},
                {"method": "Method 2", "likelihood": 0.15, "p_schedule": 0.7, "p_complete": 0.75, "mu": 1.2, "sigma": 0.55, "mu2": 1.4, "sigma2": 0.7},
                {"method": "Method 3", "likelihood": 0.2, "p_schedule": 0.78, "p_complete": 0.82, "mu": 1.0, "sigma": 0.5, "mu2": 1.2, "sigma2": 0.6},
                {"method": "Method 4", "likelihood": 0.2, "p_schedule": 0.6, "p_complete": 0.68, "mu": 1.3, "sigma": 0.6, "mu2": 1.45, "sigma2": 0.75},
                {"method": "Method 5", "likelihood": 0.2, "p_schedule": 0.72, "p_complete": 0.76, "mu": 1.15, "sigma": 0.55, "mu2": 1.35, "sigma2": 0.7},
            ],
            "visit_categories": [
                {"category": "VisitCat 1", "prob": 0.15},
                {"category": "VisitCat 2", "prob": 0.25},
                {"category": "VisitCat 3", "prob": 0.2},
                {"category": "VisitCat 4", "prob": 0.15},
                {"category": "VisitCat 5", "prob": 0.15},
                {"category": "VisitCat 6", "prob": 0.1},
            ],
        },
        "Population 3": {
            "methods": [
                {"method": "Method 1", "likelihood": 0.2, "p_schedule": 0.7, "p_complete": 0.75, "mu": 1.2, "sigma": 0.6, "mu2": 1.35, "sigma2": 0.7},
                {"method": "Method 2", "likelihood": 0.2, "p_schedule": 0.68, "p_complete": 0.72, "mu": 1.25, "sigma": 0.6, "mu2": 1.4, "sigma2": 0.75},
                {"method": "Method 3", "likelihood": 0.2, "p_schedule": 0.8, "p_complete": 0.84, "mu": 1.05, "sigma": 0.5, "mu2": 1.2, "sigma2": 0.6},
                {"method": "Method 4", "likelihood": 0.2, "p_schedule": 0.58, "p_complete": 0.65, "mu": 1.35, "sigma": 0.65, "mu2": 1.5, "sigma2": 0.8},
                {"method": "Method 5", "likelihood": 0.2, "p_schedule": 0.74, "p_complete": 0.78, "mu": 1.15, "sigma": 0.55, "mu2": 1.3, "sigma2": 0.65},
            ],
            "visit_categories": [
                {"category": "VisitCat 1", "prob": 0.25},
                {"category": "VisitCat 2", "prob": 0.15},
                {"category": "VisitCat 3", "prob": 0.25},
                {"category": "VisitCat 4", "prob": 0.1},
                {"category": "VisitCat 5", "prob": 0.15},
                {"category": "VisitCat 6", "prob": 0.1},
            ],
        },
        "Population 4": {
            "methods": [
                {"method": "Method 1", "likelihood": 0.15, "p_schedule": 0.65, "p_complete": 0.7, "mu": 1.3, "sigma": 0.65, "mu2": 1.45, "sigma2": 0.8},
                {"method": "Method 2", "likelihood": 0.25, "p_schedule": 0.7, "p_complete": 0.74, "mu": 1.25, "sigma": 0.6, "mu2": 1.4, "sigma2": 0.75},
                {"method": "Method 3", "likelihood": 0.2, "p_schedule": 0.78, "p_complete": 0.82, "mu": 1.1, "sigma": 0.55, "mu2": 1.25, "sigma2": 0.65},
                {"method": "Method 4", "likelihood": 0.2, "p_schedule": 0.55, "p_complete": 0.62, "mu": 1.4, "sigma": 0.7, "mu2": 1.55, "sigma2": 0.85},
                {"method": "Method 5", "likelihood": 0.2, "p_schedule": 0.72, "p_complete": 0.75, "mu": 1.2, "sigma": 0.6, "mu2": 1.35, "sigma2": 0.75},
            ],
            "visit_categories": [
                {"category": "VisitCat 1", "prob": 0.1},
                {"category": "VisitCat 2", "prob": 0.2},
                {"category": "VisitCat 3", "prob": 0.2},
                {"category": "VisitCat 4", "prob": 0.2},
                {"category": "VisitCat 5", "prob": 0.2},
                {"category": "VisitCat 6", "prob": 0.1},
            ],
        },
    },
}


def _normalize_probs(probs: List[float]) -> List[float]:
    arr = np.array(probs, dtype=float)
    s = float(arr.sum())
    if s <= 0:
        raise ValueError("Probabilities must sum to a positive number.")
    return (arr / s).tolist()


def validate_config(cfg: Dict[str, Any]) -> None:
    for k in ["n_patients", "seed", "max_attempts"]:
        if int(cfg[k]) <= 0:
            raise ValueError(f"{k} must be > 0.")
    if float(cfg["lambda_per_week"]) <= 0:
        raise ValueError("lambda_per_week must be > 0.")

    pop_weights = [float(cfg["populations"][p]["weight"]) for p in cfg["populations"]]
    if any(w < 0 for w in pop_weights):
        raise ValueError("Population weights must be nonnegative.")
    if sum(pop_weights) <= 0:
        raise ValueError("Population weights must sum to > 0.")

    for pop, pp in cfg["population_params"].items():
        m_probs = [float(m["likelihood"]) for m in pp["methods"]]
        v_probs = [float(v["prob"]) for v in pp["visit_categories"]]
        if sum(m_probs) <= 0:
            raise ValueError(f"{pop}: method likelihoods must sum > 0.")
        if sum(v_probs) <= 0:
            raise ValueError(f"{pop}: visit category probs must sum > 0.")


def sample_categorical(rng: np.random.Generator, items: List[Any], probs: List[float]):
    probs = np.array(probs, dtype=float)
    probs = probs / probs.sum()
    return items[rng.choice(len(items), p=probs)]


def simulate(cfg: Dict[str, Any]) -> pd.DataFrame:
    validate_config(cfg)

    n_patients = int(cfg["n_patients"])
    seed = int(cfg["seed"])
    max_attempts = int(cfg["max_attempts"])
    lam_per_week = float(cfg["lambda_per_week"])

    rng = np.random.default_rng(seed)

    inter = rng.exponential(scale=1.0 / lam_per_week, size=n_patients)
    arrival_time_weeks = np.cumsum(inter)
    week = np.ceil(arrival_time_weeks).astype(int)

    pop_names = list(cfg["populations"].keys())
    pop_weights_raw = [float(cfg["populations"][p]["weight"]) for p in pop_names]
    pop_weights = np.array(_normalize_probs(pop_weights_raw), dtype=float)
    pops = rng.choice(pop_names, size=n_patients, p=pop_weights)

    avg_tp_map = cfg["avg_touchpoints_by_method"]
    alloc_map = cfg["allocated_minutes_by_visit_category"]

    rows = []
    for i in range(n_patients):
        pop = pops[i]
        pp = cfg["population_params"][pop]

        methods = pp["methods"]
        m_items = [m["method"] for m in methods]
        m_probs = [float(m["likelihood"]) for m in methods]
        m_lookup = {m["method"]: m for m in methods}

        vcs = pp["visit_categories"]
        v_items = [v["category"] for v in vcs]
        v_probs = [float(v["prob"]) for v in vcs]

        attempts = []
        for a in range(1, max_attempts + 1):
            method = sample_categorical(rng, m_items, m_probs)
            visit_cat = sample_categorical(rng, v_items, v_probs)

            mean_tp = float(avg_tp_map.get(method, 0.0))
            if mean_tp <= 0:
                touchpoints = 0
            else:
                touchpoints = int(1 + rng.poisson(lam=max(mean_tp - 1.0, 0.0)))

            p_schedule = float(m_lookup[method]["p_schedule"])
            scheduled = rng.random() <= p_schedule

            if scheduled:
                mu, sigma = float(m_lookup[method]["mu"]), float(m_lookup[method]["sigma"])
                t_sched = float(rng.lognormal(mean=mu, sigma=sigma))
                alloc_min = float(alloc_map[visit_cat])

                p_complete = float(m_lookup[method]["p_complete"])
                completed = rng.random() <= p_complete

                if completed:
                    mu2, sigma2 = float(m_lookup[method]["mu2"]), float(m_lookup[method]["sigma2"])
                    t_comp = float(rng.lognormal(mean=mu2, sigma=sigma2))
                else:
                    t_comp = np.nan
            else:
                t_sched = np.nan
                alloc_min = np.nan
                completed = False
                t_comp = np.nan

            attempts.append({
                "attempt": a,
                "method": method,
                "visit_cat": visit_cat,
                "touchpoints": touchpoints,
                "scheduled": scheduled,
                "completed": (completed if scheduled else np.nan),
                "t_sched_days": t_sched,
                "alloc_min": alloc_min,
                "t_comp_days": t_comp,
            })

            if scheduled and completed:
                break

        out = {
            "Patient #": i + 1,
            "Population": pop,
            "Week": int(week[i]),
            "num_attempts": len(attempts),
            "Tot. Time": float(np.nansum([x["t_sched_days"] for x in attempts] + [x["t_comp_days"] for x in attempts])),
            "Tot. Allocated Time": float(np.nansum([x["alloc_min"] for x in attempts])),
            "Tot. Touchpoints": int(sum(x["touchpoints"] for x in attempts)),
            "Appt Completed": "Y" if any(x.get("completed") is True for x in attempts) else "N",
        }

        for att in attempts:
            a = att["attempt"]
            suf = "" if a == 1 else f" {a}"
            out[f"Scheduling Method{suf}"] = att["method"]
            out[f"Visit Category{suf}"] = att["visit_cat"]
            out[f"Touchpoints{suf}"] = att["touchpoints"]
            out[f"Success (Y/N){suf}"] = "Y" if att["scheduled"] else "N"
            out[f"Time to Schedule (Days){suf}"] = att["t_sched_days"]
            out[f"Allocated Appt. Time (min){suf}"] = att["alloc_min"]
            if pd.isna(att["completed"]):
                out[f"Completion (Y/N){suf}"] = np.nan
            else:
                out[f"Completion (Y/N){suf}"] = "Y" if att["completed"] else "N"
            out[f"Time to Completion{suf}"] = att["t_comp_days"]

        rows.append(out)

    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> Dict[str, Any]:
    completed_rate = float((df["Appt Completed"] == "Y").mean())
    by_pop = (
        df.assign(completed=(df["Appt Completed"] == "Y").astype(int))
          .groupby("Population")
          .agg(
              completion_rate=("completed", "mean"),
              avg_touchpoints=("Tot. Touchpoints", "mean"),
              avg_total_time=("Tot. Time", "mean"),
              n=("completed", "size"),
          )
          .reset_index()
          .to_dict(orient="records")
    )

    return {
        "completed_rate": completed_rate,
        "avg_touchpoints": float(df["Tot. Touchpoints"].mean()),
        "avg_total_time": float(df["Tot. Time"].mean()),
        "by_population": by_pop,
    }
