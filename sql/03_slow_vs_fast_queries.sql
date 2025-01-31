
-- 03_slow_vs_fast_queries.sql 

-- Execution time before partitioning: 4.113 ms 

EXPLAIN ANALYZE
SELECT *FROM train_tracking_master WHERE date = '2025-01-30';

-- Create a partitioned table to speed up queries by date 

-- Execution time after partitioning:  0.034 msec 


-- Execution time before indexing: 0.068 msec
EXPLAIN ANALYZE 
SELECT * FROM train_tracking_master 
WHERE date = '2025-01-30' AND destination = 'KGX';

-- Add indexing
-- Execution time after indexing: 0.028 msec 
