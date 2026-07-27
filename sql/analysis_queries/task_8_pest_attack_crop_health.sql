
SELECT 
    y.pest_attack,
    COUNT(*) AS farm_count,
    ROUND(AVG(y.crop_health_score), 2) AS avg_crop_health_score,
    ROUND(AVG(y.sustainability_score), 2) AS avg_sustainability_score
FROM fact_crop_yield y
GROUP BY y.pest_attack;
