"""
model.py — YOUR MODEL. Edit this file and parameters.csv.
DO NOT edit evaluate.py or specs.json.

run_model(params) -> dict of metrics matching keys in specs.json
Every key used in params must have a row in parameters.csv.
"""
import numpy as np


def run_model(params: dict) -> dict:
    """
    Starter model: simple exponential response.
    Replace this with your actual model.

    params keys must match parameters.csv names.
    Return dict keys must match specs.json keys.
    """
    A = params["A"]
    B = params["B"]
    C = params["C"]

    # Example: y(x) = A * exp(-B * x) + C
    x = np.linspace(0, 10, 200)
    y = A * np.exp(-B * x) + C

    return {
        "y_peak":  float(y.max()),
        "y_final": float(y[-1]),
        "decay":   float(B),
    }
