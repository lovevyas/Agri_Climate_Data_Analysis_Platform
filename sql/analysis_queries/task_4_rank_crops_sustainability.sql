
WITH crop_sustainability AS (
    SELECT 
        f.state,
        f.crop,
        ROUND(AVG(y.sustainability_score), 2) AS avg_sustainability_score
    FROM fact_crop_yield y
    JOIN dim_farms f ON y.farm_id = f.farm_id
    GROUP BY f.state, f.crop
)
SELECT 
    state,
    crop,
    avg_sustainability_score,
    RANK() OVER (PARTITION BY state ORDER BY avg_sustainability_score DESC) AS sustainability_rank
FROM crop_sustainability;
