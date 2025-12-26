from pathlib import Path
import mlflow.sklearn
import numpy as np

# -------------------------------------------------
# PATHS
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

WIN_MODEL_DIR = (
        PROJECT_ROOT
        / "ml_scripts"
        / "mlruns"
        / "0"
        / "models"
        / "m-0f55fadd7dfb45b59fc81d8b57492a82"
        / "artifacts"
)

# -------------------------------------------------
# LOAD SKLEARN MODEL (NOT PYFUNC)
# -------------------------------------------------

sk_model = mlflow.sklearn.load_model(str(WIN_MODEL_DIR))

# -------------------------------------------------
# ENCODED INPUT (11 FEATURES)
# -------------------------------------------------
# Board encoding (9 values, left → right, top → bottom):
#   1  = X
#  -1  = O
#   0  = empty cell
#
# Feature layout:
# [ b0 b1 b2
#   b3 b4 b5
#   b6 b7 b8
#   current_player
#   move_number ]
#
# current_player:
#   1  = X to move
#  -1  = O to move
#
# move_number:
#   number of non-empty cells on the board

X = np.array(
    [[
        1,   1,   0,   # row 0: X | X | _
        -1,  -1,  0,   # row 1: O | O | _
        0,   0,  0,   # row 2: _ | _ | _
        1,          # current_player = X
        4           # move_number
    ]],
    dtype=np.float32
)

# -------------------------------------------------
# PREDICT PROBABILITIES
# -------------------------------------------------

probs = sk_model.predict_proba(X)[0]
classes = sk_model.classes_

label_map = {
    0: "WIN_X",
    1: "WIN_O",
    2: "DRAW",
}

print("WIN model probabilities:")
for cls, prob in zip(classes, probs):
    print(f"{label_map[cls]}: {prob:.3f}")
