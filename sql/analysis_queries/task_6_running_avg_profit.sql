
SELECT 
    y.farm_id,
    y.sowing_date,
    y.profit_loss_inr,
    ROUND(AVG(y.profit_loss_inr) OVER (
        ORDER BY y.sowing_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_avg_profit_loss_inr
FROM fact_crop_yield y
ORDER BY y.sowing_date ASC;
