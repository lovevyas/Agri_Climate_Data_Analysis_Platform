
SELECT 
    f.state,
    f.crop,
    ROUND(AVG(y.profit_loss_inr), 2) AS avg_profit_loss_inr,
    COUNT(*) AS total_farms
FROM fact_crop_yield y
JOIN dim_farms f ON y.farm_id = f.farm_id
GROUP BY f.state, f.crop
ORDER BY avg_profit_loss_inr ASC;
