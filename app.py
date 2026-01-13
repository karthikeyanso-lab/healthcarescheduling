from __future__ import annotations

import io
import json
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session

from simulation import DEFAULT_CONFIG, simulate, summarize

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"  # change for deployment


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

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        session["latest_csv"] = csv_bytes.decode("latin1")

        return render_template(
            "results.html",
            summary=summ,
            preview=df.head(25).to_dict(orient="records"),
            columns=list(df.columns),
        )

    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("index"))


@app.get("/download")
def download_csv():
    if "latest_csv" not in session:
        flash("No results to download yet. Run the simulation first.", "warning")
        return redirect(url_for("index"))

    csv_bytes = session["latest_csv"].encode("latin1")
    return send_file(
        io.BytesIO(csv_bytes),
        mimetype="text/csv",
        as_attachment=True,
        download_name="appt_sim_results.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)
