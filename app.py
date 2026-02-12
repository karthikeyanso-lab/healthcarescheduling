from __future__ import annotations

import io
import json
import pandas as pd
from flask import Flask, render_template, request, send_file, flash, redirect, url_for

from simulation import DEFAULT_CONFIG, simulate, summarize
from db import init_db, save_run, list_runs, get_run

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"  # change for deployment

init_db()


def _safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return float(default)


def _safe_int(x, default=0):
    try:
        return int(float(x))
    except Exception:
        return int(default)


def build_config_from_form(form) -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy

    cfg["n_patients"] = _safe_int(form.get("n_patients"), cfg["n_patients"])
    cfg["seed"] = _safe_int(form.get("seed"), cfg["seed"])
    cfg["max_attempts"] = _safe_int(form.get("max_attempts"), cfg["max_attempts"])
    cfg["lambda_per_week"] = _safe_float(form.get("lambda_per_week"), cfg["lambda_per_week"])

    for pop in cfg["populations"].keys():
        key = f"pop_weight__{pop}"
        if key in form:
            cfg["populations"][pop]["weight"] = _safe_float(form.get(key), cfg["populations"][pop]["weight"])

    advanced_on = form.get("advanced_on") == "1"
    if advanced_on:
        pop_params_json = (form.get("population_params_json") or "").strip()
        tp_json = (form.get("avg_touchpoints_json") or "").strip()
        alloc_json = (form.get("allocated_minutes_json") or "").strip()

        if pop_params_json:
            cfg["population_params"] = json.loads(pop_params_json)
        if tp_json:
            cfg["avg_touchpoints_by_method"] = json.loads(tp_json)
        if alloc_json:
            cfg["allocated_minutes_by_visit_category"] = json.loads(alloc_json)

    return cfg


@app.get("/")
def index():
    return render_template("index.html", default_cfg=DEFAULT_CONFIG)


@app.post("/run")
def run_sim():
    try:
        cfg = build_config_from_form(request.form)

        df = simulate(cfg)
        summ = summarize(df)

        csv_text = df.to_csv(index=False)
        run_id = save_run(cfg, summ, csv_text)

        # results page shows current run
        return render_template(
            "results.html",
            run_id=run_id,
            summary=summ,
            preview=df.head(25).to_dict(orient="records"),
            columns=list(df.columns),
        )

    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("index"))


@app.get("/archive")
def archive():
    runs = list_runs(limit=100)
    return render_template("archive.html", runs=runs)


@app.get("/archive/<int:run_id>")
def archive_run(run_id: int):
    run = get_run(run_id)
    if not run:
        flash("Run not found.", "warning")
        return redirect(url_for("archive"))

    # For preview, read a small chunk of the CSV into a DF
    df = pd.read_csv(io.StringIO(run["csv_text"]))
    return render_template(
        "results.html",
        run_id=run_id,
        summary=run["summary"],
        preview=df.head(25).to_dict(orient="records"),
        columns=list(df.columns),
        archived=True,
        created_at=run["created_at"],
    )


@app.get("/archive/<int:run_id>/download")
def archive_download(run_id: int):
    run = get_run(run_id)
    if not run:
        flash("Run not found.", "warning")
        return redirect(url_for("archive"))

    csv_bytes = run["csv_text"].encode("utf-8")
    return send_file(
        io.BytesIO(csv_bytes),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"appt_sim_run_{run_id}.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)
