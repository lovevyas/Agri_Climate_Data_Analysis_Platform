
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS dim_farms (
    farm_id            VARCHAR(20) PRIMARY KEY,
    state              VARCHAR(60) NOT NULL,
    district           VARCHAR(60) NOT NULL,
    village            VARCHAR(60) NOT NULL,
    crop               VARCHAR(40) NOT NULL,
    crop_variety       VARCHAR(40) NOT NULL,
    soil_type          VARCHAR(30) NOT NULL,
    soil_ph            DECIMAL(3,1) NOT NULL,
    land_area_acres    DECIMAL(6,2) NOT NULL,
    irrigation_method  VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_weather_stations (
    station_code       VARCHAR(20) PRIMARY KEY,
    station_name       VARCHAR(80) NOT NULL,
    state              VARCHAR(60) NOT NULL,
    district           VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_crop_yield (
    farm_id                     VARCHAR(20) PRIMARY KEY REFERENCES dim_farms(farm_id),
    sowing_date                 DATE NOT NULL,
    harvesting_date             DATE NOT NULL,
    season                      VARCHAR(10) NOT NULL,
    nitrogen_kg_ha              INT NOT NULL,
    phosphorus_kg_ha            INT NOT NULL,
    potassium_kg_ha             INT NOT NULL,
    fertilizer_used             VARCHAR(30) NOT NULL,
    farm_reported_rainfall_mm   DECIMAL(6,2) NOT NULL,
    farm_reported_avg_temp_c    DECIMAL(5,2) NOT NULL,
    farm_reported_humidity_pct  INT NOT NULL,
    pest_attack                 VARCHAR(3) NOT NULL,
    disease_name                VARCHAR(40),       
    pesticide_used              VARCHAR(30) NOT NULL,
    expected_yield_tonnes       DECIMAL(8,2) NOT NULL,
    actual_yield_tonnes         DECIMAL(8,2) NOT NULL,
    yield_gap_tonnes            DECIMAL(8,2) NOT NULL,
    water_consumption_litres    DECIMAL(12,2) NOT NULL,
    production_cost_inr         DECIMAL(12,2) NOT NULL,
    market_price_inr            DECIMAL(12,2) NOT NULL,
    profit_loss_inr             DECIMAL(12,2) NOT NULL,
    crop_health_score           DECIMAL(5,2) NOT NULL,
    sustainability_score        DECIMAL(5,2) NOT NULL,
    matched_station_code        VARCHAR(20) REFERENCES dim_weather_stations(station_code),
    match_type                  VARCHAR(25) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_weather_observations (
    station_code               VARCHAR(20) PRIMARY KEY REFERENCES dim_weather_stations(station_code),
    observation_date           DATE NOT NULL,
    season                     VARCHAR(15) NOT NULL,
    max_temp_c                 DECIMAL(5,2) NOT NULL,
    min_temp_c                 DECIMAL(5,2) NOT NULL,
    avg_temp_c                 DECIMAL(5,2) NOT NULL,
    rainfall_mm                DECIMAL(6,2) NOT NULL,
    relative_humidity_percent  INT NOT NULL,
    wind_speed_kmh             DECIMAL(5,2) NOT NULL,
    wind_direction             VARCHAR(5) NOT NULL,
    visibility_km              DECIMAL(5,2) NOT NULL,
    cloud_cover_percent        INT NOT NULL,
    sunshine_hours             DECIMAL(4,2) NOT NULL,
    atmospheric_pressure_hpa   DECIMAL(6,2) NOT NULL,
    soil_temperature_c         DECIMAL(5,2) NOT NULL,
    heat_index_c               DECIMAL(5,2) NOT NULL,
    dew_point_c                DECIMAL(5,2) NOT NULL,
    flood_warning              VARCHAR(3) NOT NULL,
    cyclone_alert              VARCHAR(3) NOT NULL,
    rainfall_category          VARCHAR(15) NOT NULL,
    weather_condition          VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_global_climate_environment (
    observation_id             BIGINT PRIMARY KEY,
    date                       DATE NOT NULL,
    station_id                 VARCHAR(20) NOT NULL,
    country                    VARCHAR(20) NOT NULL,
    latitude                   DECIMAL(9,6) NOT NULL,
    longitude                  DECIMAL(9,6) NOT NULL,
    elevation_m                DECIMAL(7,2) NOT NULL,
    avg_temperature_c          DECIMAL(5,2) NOT NULL,
    max_temperature_c          DECIMAL(5,2) NOT NULL,
    min_temperature_c          DECIMAL(5,2) NOT NULL,
    precipitation_mm           DECIMAL(6,2) NOT NULL,
    snowfall_cm                DECIMAL(6,2) NOT NULL,
    humidity_percent           INT NOT NULL,
    wind_speed_kmh             DECIMAL(5,2) NOT NULL,
    wind_direction             VARCHAR(5) NOT NULL,
    solar_radiation_wm2        DECIMAL(6,2) NOT NULL,
    atmospheric_pressure_hpa   DECIMAL(6,2) NOT NULL,
    cloud_cover_percent        INT NOT NULL,
    uv_index                   INT NOT NULL,
    soil_moisture_percent      DECIMAL(5,2) NOT NULL,
    drought_index              VARCHAR(10) NOT NULL,
    evapotranspiration_mm      DECIMAL(5,2) NOT NULL,
    air_quality_index          INT NOT NULL,
    pm25                       DECIMAL(5,2) NOT NULL,
    pm10                       DECIMAL(5,2) NOT NULL,
    co2_ppm                    DECIMAL(6,2) NOT NULL,
    methane_ppb                DECIMAL(7,2) NOT NULL,
    ozone_ppb                  DECIMAL(5,2) NOT NULL,
    climate_zone               VARCHAR(15) NOT NULL,
    weather_event              VARCHAR(15),        
    disaster_risk              VARCHAR(10) NOT NULL 
);

CREATE TABLE IF NOT EXISTS analytics.yield_weather_correlation (
    correlation_id             SERIAL PRIMARY KEY,
    state                      VARCHAR(60) NOT NULL,
    crop                       VARCHAR(40) NOT NULL,
    rainfall_reporting_gap_pct DECIMAL(6,2) NOT NULL,
    avg_profit_loss_inr        DECIMAL(12,2) NOT NULL,
    avg_yield_gap_tonnes       DECIMAL(8,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.climate_risk_farms (
    risk_id                    SERIAL PRIMARY KEY,
    state                      VARCHAR(60) NOT NULL,
    crop                       VARCHAR(40) NOT NULL,
    exposure_flag              VARCHAR(20) NOT NULL,
    pest_attack_rate_pct       DECIMAL(5,2) NOT NULL,
    avg_crop_health_score      DECIMAL(5,2) NOT NULL,
    avg_sustainability_score   DECIMAL(5,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.global_environment_summary (
    summary_id                 SERIAL PRIMARY KEY,
    country                    VARCHAR(20) NOT NULL,
    climate_zone               VARCHAR(15) NOT NULL,
    avg_air_quality_index      DECIMAL(6,2) NOT NULL,
    avg_co2_ppm                DECIMAL(6,2) NOT NULL,
    avg_methane_ppb            DECIMAL(7,2) NOT NULL,
    high_disaster_risk_pct     DECIMAL(5,2) NOT NULL
);
