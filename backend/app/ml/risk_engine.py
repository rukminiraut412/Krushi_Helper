import os
import sys
from typing import Dict, Any

# Ensure the root KrushiRakshak directory is in sys.path so 'ml' package can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.prediction.predict import predict_climate_risks, synthesize_risk_explanation


def run_risk_inference(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapter invoking the ML inference pipeline.
    """
    return predict_climate_risks(features)


def get_risk_explanation(predictions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapter synthesizing risk explanation from predictions.
    """
    return synthesize_risk_explanation(predictions)
