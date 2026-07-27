
CREATE OR REPLACE VIEW view_noaa_disaster_risk_distribution AS
WITH country_totals AS (
    SELECT 
        country,
        COUNT(*) AS total_observations
    FROM fact_global_climate_environment
    GROUP BY country
)
SELECT 
    g.country,
    g.disaster_risk,
    COUNT(*) AS risk_occurrence_count,
    ROUND(COUNT(*)::NUMERIC / ct.total_observations * 100, 2) AS risk_percentage
FROM fact_global_climate_environment g
JOIN country_totals ct ON g.country = ct.country
GROUP BY g.country, g.disaster_risk, ct.total_observations
ORDER BY g.country, risk_percentage DESC;
