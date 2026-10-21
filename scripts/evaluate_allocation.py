import pandas as pd
import os

# ------------------------------------------------------
# Allocation Evaluator Class
# ------------------------------------------------------

class AllocationEvaluator:
    def __init__(self, allocation_path, farmers_path="data/farmers.csv", companies_path="data/companies.csv"):
        self.alloc_df = pd.read_csv(allocation_path)
        self.farmers_df = pd.read_csv(farmers_path)
        self.companies_df = pd.read_csv(companies_path)

        # Merge farmer size only if missing
        if "Farmer_Size" not in self.alloc_df.columns:
            self.alloc_df = self.alloc_df.merge(
                self.farmers_df[["Farmer_ID", "Farmer_Size"]],
                on="Farmer_ID", how="left"
            )

        # Merge company demand only if missing
        if "Required_Quantity_kg" not in self.alloc_df.columns:
            self.alloc_df = self.alloc_df.merge(
                self.companies_df[["Company_ID", "Required_Quantity_kg"]],
                on="Company_ID", how="left"
            )

        # Cleanup accidental duplicates (_x, _y)
        for col in list(self.alloc_df.columns):
            if col.endswith("_x") or col.endswith("_y"):
                base = col.rsplit("_", 1)[0]
                if base not in self.alloc_df.columns:
                    self.alloc_df[base] = self.alloc_df[col]

        self.alloc_df = self.alloc_df.loc[:, ~self.alloc_df.columns.duplicated()]

    # ------------------------------------------------------
    # Efficiency metrics
    # ------------------------------------------------------
    def calculate_efficiency(self):
        total_alloc = self.alloc_df["Quantity_Allocated"].sum()
        total_demand = self.companies_df["Required_Quantity_kg"].sum()
        total_supply = self.farmers_df["Quantity_kg"].sum()

        return {
            "Total_Allocated": total_alloc,
            "Demand_Satisfied_%": round((total_alloc / total_demand) * 100, 2) if total_demand else 0,
            "Supply_Utilized_%": round((total_alloc / total_supply) * 100, 2) if total_supply else 0
        }

    # ------------------------------------------------------
    # Fairness metrics
    # ------------------------------------------------------
    def calculate_fairness(self):
        farmer_alloc = self.alloc_df.groupby("Farmer_ID")["Quantity_Allocated"].sum()
        variance = (farmer_alloc.std() / farmer_alloc.mean()) if farmer_alloc.mean() > 0 else 0

        small_alloc = self.alloc_df[self.alloc_df["Farmer_Size"] == "Small"]["Quantity_Allocated"].sum()
        total_alloc = self.alloc_df["Quantity_Allocated"].sum()

        fairness_ratio = (small_alloc / total_alloc * 100) if total_alloc > 0 else 0

        return {
            "Allocation_Variance": round(variance, 3),
            "Fairness_Small_Farmers_%": round(fairness_ratio, 2)
        }

    # ------------------------------------------------------
    # Cost metrics
    # ------------------------------------------------------
    def calculate_cost(self):
        if "Distance_km" in self.alloc_df.columns:
            avg_distance = self.alloc_df["Distance_km"].mean()
            return {"Average_Distance_km": round(avg_distance, 2)}
        return {"Average_Distance_km": "N/A"}

    # ------------------------------------------------------
    # Final evaluator
    # ------------------------------------------------------
    def evaluate(self):
        metrics = {}
        metrics.update(self.calculate_efficiency())
        metrics.update(self.calculate_fairness())
        metrics.update(self.calculate_cost())
        metrics["Total_Allocations"] = len(self.alloc_df)

        return pd.DataFrame([metrics])


# ------------------------------------------------------
# Public API: called from generate_scenarios.py
# ------------------------------------------------------
def evaluate_algorithm(name, allocation_file, output_file=None):
    try:
        evaluator = AllocationEvaluator(allocation_file)
        result = evaluator.evaluate()
        result["Algorithm"] = name

        # Decide where to save
        if output_file is None:
            os.makedirs("results", exist_ok=True)
            output_file = f"results/evaluation_{name.lower()}.csv"

        result.to_csv(output_file, index=False)
        print(f"  ✔ Evaluation saved → {output_file}")

        return result

    except Exception as e:
        print(f"  ❌ Evaluation failed for {name}: {e}")
        return None


if __name__ == "__main__":
    evaluate_algorithm("Greedy", "results/greedy_allocation.csv")
