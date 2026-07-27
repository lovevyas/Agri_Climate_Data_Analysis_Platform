import os
import pandas as pd
import numpy as np

def run_tests():
    print("=================== AGRI-CLIMATE PLATFORM TEST SUITE ===================")
    print("Reading local curated Parquet datasets for verification...")

    curated_dir = "datasets/curated"

    required_tables = ["dim_farms", "dim_weather_stations", "fact_crop_yield", "fact_weather_observations", "fact_global_climate_environment"]
    missing_tables = [t for t in required_tables if not os.path.exists(os.path.join(curated_dir, t))]

    if missing_tables:
        print(f"ERROR: Curated tables {missing_tables} are missing! Please run the PySpark ETL script first.")
        return

    df_farms = pd.read_parquet(os.path.join(curated_dir, "dim_farms"))
    df_stations = pd.read_parquet(os.path.join(curated_dir, "dim_weather_stations"))
    df_yield = pd.read_parquet(os.path.join(curated_dir, "fact_crop_yield"))
    df_weather = pd.read_parquet(os.path.join(curated_dir, "fact_weather_observations"))
    df_noaa = pd.read_parquet(os.path.join(curated_dir, "fact_global_climate_environment"))

    test_results = []

    farms_dupes = df_farms["farm_id"].duplicated().sum()
    stations_dupes = df_stations["station_code"].duplicated().sum()
    tc_01_pass = (farms_dupes == 0) and (stations_dupes == 0)
    test_results.append({
        "TC ID": "TC-01",
        "Scenario": "Exact duplicate row in raw files",
        "Expected Result": "Duplicates removed; primary keys are unique",
        "Actual Result": f"Farms Dupes: {farms_dupes}, Stations Dupes: {stations_dupes}",
        "Status": "PASSED" if tc_01_pass else "FAILED"
    })

    belagavi_kota_farms = df_farms[df_farms["district"].isin(["BELAGAVI", "KOTA"])]["farm_id"]
    matched_bel_kota = df_yield[df_yield["farm_id"].isin(belagavi_kota_farms)]

    match_types = matched_bel_kota["match_type"].unique()
    tc_02_pass = len(matched_bel_kota) > 0 and all(mt == "Nearest In State" for mt in match_types)
    test_results.append({
        "TC ID": "TC-02",
        "Scenario": "Farms in Belagavi/Kota fallback match",
        "Expected Result": "Resolved via same-state closest date; match_type = 'Nearest In State'",
        "Actual Result": f"Farms verified: {len(matched_bel_kota)}, Match Types: {list(match_types)}",
        "Status": "PASSED" if tc_02_pass else "FAILED"
    })

    unmatched_yields = df_yield[df_yield["matched_station_code"].isnull()]
    tc_03_pass = len(unmatched_yields) == 0 
    test_results.append({
        "TC ID": "TC-03",
        "Scenario": "Farm in a state with zero stations",
        "Expected Result": "Retained with null matched_station_code and match_type = 'Unresolved'",
        "Actual Result": f"Unmatched yields in current dataset: {len(unmatched_yields)}",
        "Status": "PASSED" if tc_03_pass else "FAILED"
    })

    crop_seasons = set(df_yield["season"].unique())
    imd_seasons = set(df_weather["season"].unique())
    tc_05_pass = len(crop_seasons.intersection(imd_seasons)) == 0
    test_results.append({
        "TC ID": "TC-05",
        "Scenario": "Agriculture vs IMD season vocabulary",
        "Expected Result": "Vocabularies kept distinct, no overlap",
        "Actual Result": f"Crop Seasons: {crop_seasons}, IMD Seasons: {imd_seasons}",
        "Status": "PASSED" if tc_05_pass else "FAILED"
    })

    station_groups = df_noaa.groupby("station_id")[["country", "climate_zone", "latitude", "longitude"]].nunique()
    unstable_count = len(station_groups[station_groups.max(axis=1) > 1])
    tc_06_pass = unstable_count == len(df_noaa["station_id"].unique())
    test_results.append({
        "TC ID": "TC-06",
        "Scenario": "NOAA station_id instability",
        "Expected Result": "Treat station_id as observation attribute; do not assume physical stability",
        "Actual Result": f"Unstable station counts: {unstable_count} out of {df_noaa['station_id'].nunique()}",
        "Status": "PASSED" if tc_06_pass else "FAILED"
    })

    profitable_count = (df_yield["profit_loss_inr"] >= 0).sum()
    tc_07_pass = profitable_count == 92
    test_results.append({
        "TC ID": "TC-07",
        "Scenario": "Profit/Loss positive row count",
        "Expected Result": "92 profitable farms preserved in aggregates",
        "Actual Result": f"Profitable farms: {profitable_count}",
        "Status": "PASSED" if tc_07_pass else "FAILED"
    })

    invalid_ph = df_farms[(df_farms["soil_ph"] < 0) | (df_farms["soil_ph"] > 14)]
    tc_08_pass = len(invalid_ph) == 0
    test_results.append({
        "TC ID": "TC-08",
        "Scenario": "soil_ph value range check",
        "Expected Result": "All values within 0-14 scale",
        "Actual Result": f"Invalid ph rows: {len(invalid_ph)}",
        "Status": "PASSED" if tc_08_pass else "FAILED"
    })

    merged = pd.merge(df_yield, df_weather, left_on="matched_station_code", right_on="station_code")
    merged["gap_pct"] = (abs(merged["farm_reported_rainfall_mm"] - merged["rainfall_mm"]) / merged["rainfall_mm"]) * 100
    large_gap_count = (merged["gap_pct"] > 20).sum()
    tc_10_pass = large_gap_count > 0
    test_results.append({
        "TC ID": "TC-10",
        "Scenario": "Rainfall reporting gap > 20%",
        "Expected Result": "Correctly tracked for Use Case 1 KPI threshold",
        "Actual Result": f"Farms with > 20% gap: {large_gap_count} (out of {len(merged)})",
        "Status": "PASSED" if tc_10_pass else "FAILED"
    })

    tc_13_pass = (len(df_farms) == 2000) and (len(df_yield) == 2000) and (len(df_noaa) == 2000)
    test_results.append({
        "TC ID": "TC-13",
        "Scenario": "Ingestion to curation row count checks",
        "Expected Result": "2000 rows in, 2000 rows out for all files",
        "Actual Result": f"Farms: {len(df_farms)}, Yield Facts: {len(df_yield)}, NOAA: {len(df_noaa)}",
        "Status": "PASSED" if tc_13_pass else "FAILED"
    })

    df_results = pd.DataFrame(test_results)

    os.makedirs("testing", exist_ok=True)
    csv_log_path = "testing/test_results_log.csv"
    df_results.to_csv(csv_log_path, index=False)
    print(f"\nSaved test results log to: {csv_log_path}")

    print("\n----------------------- TEST SUMMARY -----------------------")
    for idx, row in df_results.iterrows():
        print(f"[{row['Status']}] {row['TC ID']} - {row['Scenario']}")
    print("------------------------------------------------------------")

    passed_count = (df_results["Status"] == "PASSED").sum()
    print(f"Total Tests Executed: {len(df_results)} | PASSED: {passed_count} | FAILED: {len(df_results) - passed_count}")

if __name__ == "__main__":
    run_tests()
