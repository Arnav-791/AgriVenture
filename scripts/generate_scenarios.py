import os
import shutil
import pandas as pd
from datetime import timedelta

# ------------------------------------------------------
# Import algorithms & evaluation
# ------------------------------------------------------
from Algorithms.greedy_allocation import greedy_allocate
from Algorithms.maxflow_allocation import run_maxflow
from Algorithms.mincost_maxflow_allocation import run_mincost_maxflow
from Algorithms.fair_mincost_maxflow_allocation import run_fair_mincost_maxflow
from Algorithms.hungarian_allocation import run_hungarian
from Algorithms.fair_hungarian_allocation import run_fair_hungarian
from .evaluate_allocation import evaluate_algorithm


# ------------------------------------------------------
# Scenario Definitions (ONLY 3)
# ------------------------------------------------------
SCENARIOS = {
    "base": "Normal baseline case",
    "high_demand": "Companies demand more quantity",
    "low_demand": "Farmers produce more quantity"
}

DATA_DIR = "data"
SCENARIOS_DIR = "scenarios"


# ------------------------------------------------------
# Utility
# ------------------------------------------------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def modify_data_for_scenario(scenario):
    """Modify farmers.csv & companies.csv for scenario, save to temp folder."""
    farmers = pd.read_csv(f"{DATA_DIR}/farmers.csv")
    companies = pd.read_csv(f"{DATA_DIR}/companies.csv")

    # Convert date columns
    farmers["Availability_Date"] = pd.to_datetime(farmers["Availability_Date"], errors="coerce")
    companies["Delivery_Deadline"] = pd.to_datetime(companies["Delivery_Deadline"], errors="coerce")

    # Scenario-specific changes
    if scenario == "high_demand":
        companies["Required_Quantity_kg"] = (companies["Required_Quantity_kg"] * 1.5).astype(int)

    elif scenario == "low_demand":
        farmers["Quantity_kg"] = (farmers["Quantity_kg"] * 1.5).astype(int)

    # Save modified files to /data/temp
    temp_path = f"{DATA_DIR}/temp"
    ensure_dir(temp_path)
    farmers.to_csv(f"{temp_path}/farmers.csv", index=False)
    companies.to_csv(f"{temp_path}/companies.csv", index=False)
    shutil.copy(f"{DATA_DIR}/edges.csv", f"{temp_path}/edges.csv")

    return temp_path


# ------------------------------------------------------
# Run all algorithms for a scenario
# ------------------------------------------------------
def run_algorithms_for_scenario(scenario, temp_dir):
    print(f"\n🔹 Running algorithms for scenario: {scenario}")

    scenario_path = f"{SCENARIOS_DIR}/{scenario}"
    ensure_dir(scenario_path)

    # Replace main data with scenario-modified data
    shutil.copy(f"{temp_dir}/farmers.csv", f"{DATA_DIR}/farmers.csv")
    shutil.copy(f"{temp_dir}/companies.csv", f"{DATA_DIR}/companies.csv")
    shutil.copy(f"{temp_dir}/edges.csv", f"{DATA_DIR}/edges.csv")

    farmers_file = f"{DATA_DIR}/farmers.csv"
    companies_file = f"{DATA_DIR}/companies.csv"
    edges_file = f"{DATA_DIR}/edges.csv"

    # Algorithm methods
    ALGO_FUNCS = {
        "greedy": greedy_allocate,
        "maxflow": run_maxflow,
        "mincostmaxflow": run_mincost_maxflow,
        "fair_mincostmaxflow": run_fair_mincost_maxflow,
        "hungarian": run_hungarian,
        "fair_hungarian": run_fair_hungarian
    }

    for key, func in ALGO_FUNCS.items():
        print(f"  ▶ Running {key}...")
        try:
            output = func(farmers_file, companies_file, edges_file)

            # allocation file path
            alloc_path = f"{scenario_path}/{key}_allocation.csv"

            # save allocation result
            if isinstance(output, pd.DataFrame):
                output.to_csv(alloc_path, index=False)
            elif os.path.exists("results/allocation_temp.csv"):
                shutil.move("results/allocation_temp.csv", alloc_path)

            # evaluate and save results
            eval_path = f"{scenario_path}/evaluation_{key}.csv"
            evaluate_algorithm(key, alloc_path, output_file=eval_path)

            print(f"  ✔ Completed {key}")

        except Exception as e:
            print(f"  ❌ {key} failed: {e}")

    print(f"✅ Scenario '{scenario}' fully processed.\n")


# ------------------------------------------------------
# Main Controller
# ------------------------------------------------------
def main():
    ensure_dir(SCENARIOS_DIR)

    print("\n===== 🌾 Generating SCENARIO SIMULATIONS for AGRIVENTURE =====")

    for scenario in SCENARIOS.keys():
        print(f"\n🧩 Preparing scenario: {scenario}")
        temp_dir = modify_data_for_scenario(scenario)
        run_algorithms_for_scenario(scenario, temp_dir)

    print("\n🎉 ALL SCENARIOS COMPLETED SUCCESSFULLY!")
    print("📁 Check output inside: /scenarios/")


if __name__ == "__main__":
    main()
