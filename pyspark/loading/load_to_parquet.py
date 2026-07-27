

import os
import shutil

def load_all(dim_farms, dim_weather_stations, fact_crop_yield, fact_weather_observations, fact_global_climate_environment, curated_dir='datasets/curated'):

    print("--- Phase 6: LOADING ---")

    if not os.path.exists(curated_dir):
        os.makedirs(curated_dir)

    tables = {
        "dim_farms": (dim_farms, None),
        "dim_weather_stations": (dim_weather_stations, None),
        "fact_crop_yield": (fact_crop_yield, ['season']),
        "fact_weather_observations": (fact_weather_observations, ['season']),
        "fact_global_climate_environment": (fact_global_climate_environment, ['country'])
    }

    for table_name, (df, partition_cols) in tables.items():
        table_path = os.path.join(curated_dir, table_name)

        if os.path.exists(table_path):
            if os.path.isdir(table_path):
                shutil.rmtree(table_path)
            else:
                os.remove(table_path)

        pdf = df.toPandas()

        pdf.to_parquet(table_path, index=False, partition_cols=partition_cols)
        print(f"Successfully loaded {table_name} into {table_path}")

    print("Loading complete.\n")
