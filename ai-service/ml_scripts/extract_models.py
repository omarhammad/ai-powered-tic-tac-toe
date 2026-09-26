from pathlib import Path
import mlflow.sklearn

# -------------------------------------------------
# PATHS
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MLRUNS_DIR = PROJECT_ROOT / "ml_scripts" / "mlruns"
OUTPUT_DIR = PROJECT_ROOT / "src" / "main" / "resources" / "models"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

POLICY_MODEL_DIR = (
        MLRUNS_DIR
        / "2"
        / "models"
        / "m-6c82d29dcf064b2c83f741191cb1b7cd"
        / "artifacts"
)

print("\n Extracting POLICY model only...\n")

# -------------------------------------------------
# POLICY MODEL (XGBoost via MLflow)
# -------------------------------------------------

print("Loading POLICY model via MLflow...")
policy_model = mlflow.sklearn.load_model(str(POLICY_MODEL_DIR))

policy_out = OUTPUT_DIR / "policy_model.json"
policy_model.save_model(policy_out)

print(f" Saved XGBoost policy model → {policy_out}")
print("\n Policy model extraction complete.")
