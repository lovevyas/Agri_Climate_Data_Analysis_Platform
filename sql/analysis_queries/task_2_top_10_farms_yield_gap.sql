
SELECT 
    y.farm_id,
    f.state,
    f.district,
    f.crop,
    y.expected_yield_tonnes,
    y.actual_yield_tonnes,
    y.yield_gap_tonnes
FROM fact_crop_yield y
JOIN dim_farms f ON y.farm_id = f.farm_id
ORDER BY y.yield_gap_tonnes DESC
LIMIT 10;
