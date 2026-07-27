
WITH crop_yields AS (
    SELECT 
        f.state,
        f.crop,
        ROUND(AVG(y.actual_yield_tonnes), 2) AS avg_actual_yield_tonnes
    FROM fact_crop_yield y
    JOIN dim_farms f ON y.farm_id = f.farm_id
    GROUP BY f.state, f.crop
),
ranked_yields AS (
    SELECT 
        state,
        crop,
        avg_actual_yield_tonnes,
        DENSE_RANK() OVER (PARTITION BY state ORDER BY avg_actual_yield_tonnes DESC) as yield_rank
    FROM crop_yields
)
SELECT 
    state,
    crop,
    avg_actual_yield_tonnes
FROM ranked_yields
WHERE yield_rank = 1
ORDER BY state ASC;
