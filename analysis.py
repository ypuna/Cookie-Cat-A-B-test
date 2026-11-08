"""Mobile game A/B test: moving the first progression gate from level 30 to level 40.

Data: cookie_cats.csv (one row per player; version = gate_30 or gate_40;
retention_1 / retention_7 = returned 1 / 7 days after install).
Run:  python analysis.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "cookie_cats.csv"
OUT = ROOT / "results"


def two_prop_test(success_a, n_a, success_b, n_b):
    """Two-sided z-test and 95% CI for (B - A) difference in proportions."""
    p_a, p_b = success_a / n_a, success_b / n_b
    pooled = (success_a + success_b) / (n_a + n_b)
    se_pooled = np.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z = (p_b - p_a) / se_pooled
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    se = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    diff = p_b - p_a
    return {
        "rate_a": p_a,
        "rate_b": p_b,
        "diff": diff,
        "ci_low": diff - 1.96 * se,
        "ci_high": diff + 1.96 * se,
        "z": z,
        "p_value": p_value,
    }


def main():
    df = pd.read_csv(DATA)
    OUT.mkdir(exist_ok=True)

    # Data quality checks
    dup_users = int(df["userid"].duplicated().sum())
    nulls = int(df.isna().sum().sum())

    a = df[df["version"] == "gate_30"]
    b = df[df["version"] == "gate_40"]
    n_a, n_b = len(a), len(b)

    # Sample ratio mismatch: a 50/50 split should give roughly equal counts
    srm = stats.chisquare([n_a, n_b])

    results = {
        "players_total": len(df),
        "players_gate_30": n_a,
        "players_gate_40": n_b,
        "duplicate_users": dup_users,
        "null_values": nulls,
        "sample_ratio_mismatch_p": float(srm.pvalue),
        "retention_1": two_prop_test(a["retention_1"].sum(), n_a, b["retention_1"].sum(), n_b),
        "retention_7": two_prop_test(a["retention_7"].sum(), n_a, b["retention_7"].sum(), n_b),
        "avg_game_rounds": {
            "gate_30": float(a["sum_gamerounds"].mean()),
            "gate_40": float(b["sum_gamerounds"].mean()),
        },
    }
    # Retained players lost per 1M installs from the change
    results["retained_players_lost_per_1m_installs"] = round(
        -results["retention_7"]["diff"] * 1_000_000
    )

    (OUT / "results.json").write_text(json.dumps(results, indent=2, default=float))

    r7, r1 = results["retention_7"], results["retention_1"]
    lines = [
        "# Mobile Game A/B Test: First Progression Gate Placement",
        "",
        f"- Players: {results['players_total']:,} (gate_30: {n_a:,}, gate_40: {n_b:,})",
        f"- Sample ratio mismatch check: p = {results['sample_ratio_mismatch_p']:.3f}",
        f"- Duplicate users: {dup_users}; null values: {nulls}",
        "",
        "## 7-day retention",
        f"- Gate 30: {r7['rate_a']:.2%}",
        f"- Gate 40: {r7['rate_b']:.2%}",
        f"- Difference: {r7['diff'] * 100:+.2f} pts "
        f"(95% CI {r7['ci_low'] * 100:+.2f} to {r7['ci_high'] * 100:+.2f}), p = {r7['p_value']:.4f}",
        f"- Retained players lost per 1M installs: "
        f"{results['retained_players_lost_per_1m_installs']:,}",
        "",
        "## 1-day retention",
        f"- Gate 30: {r1['rate_a']:.2%}",
        f"- Gate 40: {r1['rate_b']:.2%}",
        f"- Difference: {r1['diff'] * 100:+.2f} pts "
        f"(95% CI {r1['ci_low'] * 100:+.2f} to {r1['ci_high'] * 100:+.2f}), p = {r1['p_value']:.4f}",
        "",
        "## Average game rounds played",
        f"- Gate 30: {results['avg_game_rounds']['gate_30']:.1f}",
        f"- Gate 40: {results['avg_game_rounds']['gate_40']:.1f}",
    ]
    (OUT / "results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
