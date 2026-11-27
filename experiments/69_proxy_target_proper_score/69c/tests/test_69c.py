import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "69b/scripts"))
from common import SPLIT  # noqa: E402
from eval_69c import run, wins  # noqa: E402


def _items(n_per=2):
    items = []
    k = 0
    for task, split in SPLIT.items():
        for j in range(n_per):
            k += 1
            # Test tasks are all 1s. Train and val are all 5s, so a train-only selector
            # that likes a point mass at 5 is wrong on the test tasks.
            rating = 1 if split == "test" else 5
            items.append({
                "item_id": f"i{k}", "task": task, "split": split,
                "ratings": [rating, rating],
            })
    return items


def test_formulation_3_prefers_the_test_matching_forecast():
    items = _items()
    rows = []
    for it in items:
        rows.append({"judge": "good", "source": "measured", "item_id": it["item_id"], "probs": [0, 1, 0, 0, 0, 0]})
        rows.append({"judge": "bad", "source": "measured", "item_id": it["item_id"], "probs": [0, 0, 0, 0, 0, 1]})
    # One judge whose native forecast is the train mode (5). Val is also 5, so both
    # formulations see the same native vector. The contrast is inside one judge that
    # is perfect: native mass on 1, which matches the test and loses on train.
    out = run(rows, items)
    good = out["arms"]["good"]
    bad = out["arms"]["bad"]
    assert good["status"] == "MEASURED"
    assert good["rps3_minus_rps4"]["test_rps_a"] < bad["rps3_minus_rps4"]["test_rps_a"]
    assert wins({"diff": -0.02, "hi": -0.01}) is True
    assert wins({"diff": -0.02, "hi": 0.01}) is False
    assert np.isfinite(good["rps3_minus_pearson3"]["diff"])
