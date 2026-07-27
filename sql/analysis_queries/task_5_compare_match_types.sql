
SELECT 
    y.match_type,
    COUNT(*) AS farm_count,
    ROUND(AVG(y.profit_loss_inr), 2) AS avg_profit_loss_inr,
    ROUND(AVG(y.expected_yield_tonnes - y.actual_yield_tonnes), 2) AS avg_yield_gap_tonnes
FROM fact_crop_yield y
GROUP BY y.match_type;
