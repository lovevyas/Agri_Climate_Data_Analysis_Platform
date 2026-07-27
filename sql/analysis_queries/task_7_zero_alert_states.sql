
SELECT DISTINCT f_all.state
FROM dim_farms f_all
WHERE f_all.state NOT IN (
    SELECT DISTINCT f.state
    FROM fact_crop_yield y
    JOIN dim_farms f ON y.farm_id = f.farm_id
    JOIN fact_weather_observations w ON y.matched_station_code = w.station_code
    WHERE w.flood_warning = 'Yes' OR w.cyclone_alert = 'Yes'
);
