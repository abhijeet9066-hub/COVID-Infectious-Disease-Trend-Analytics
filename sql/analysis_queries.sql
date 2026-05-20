-- Core analytical queries
SELECT COUNT(*) AS total_records FROM fact_main;

-- Replace date_column with actual date field
-- SELECT strftime('%Y-%m', date_column) AS month, COUNT(*) AS records
-- FROM fact_main
-- GROUP BY 1
-- ORDER BY 1;

-- Replace target with actual target field
-- SELECT target, COUNT(*) AS records
-- FROM fact_main
-- GROUP BY target;
