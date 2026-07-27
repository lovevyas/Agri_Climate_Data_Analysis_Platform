
CREATE OR REPLACE VIEW view_rainfall_reporting_gap AS
SELECT 
    f.state,
    ROUND(AVG(y.farm_reported_rainfall_mm), 2) AS avg_farm_reported_rainfall_mm,
    ROUND(AVG(w.rainfall_mm), 2) AS avg_station_reported_rainfall_mm,
    ROUND(AVG(y.farm_reported_rainfall_mm - w.rainfall_mm), 2) AS avg_absolute_gap_mm,
    ROUND(AVG(ABS(y.farm_reported_rainfall_mm - w.rainfall_mm) / NULLIF(w.rainfall_mm, 0) * 100), 2) AS avg_gap_percentage
FROM fact_crop_yield y
JOIN dim_farms f ON y.farm_id = f.farm_id
JOIN fact_weather_observations w ON y.matched_station_code = w.station_code
GROUP BY f.state;
