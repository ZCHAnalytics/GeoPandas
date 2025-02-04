04_results.md 

🚄 Train Tracking Database Optimization

1️⃣ Query Performance Before Optimization

❌ Before Partitioning
Query:
```sql
EXPLAIN ANALYZE
SELECT * FROM train_tracking_master WHERE date = '2025-01-30';
```
⏳ Execution Time: 4.113 ms  

![Before Partition](docs/images/03_before_partition.png)


2️⃣ After Partitioning (Faster Reads!)
Query: 
```sql 
EXPLAIN ANALYZE
SELECT * FROM train_tracking_master WHERE date = '2025-01-30';
```
⚡ Execution Time: 0.034 ms  

![After Partition](docs/images/03_after_partition.png)

🚀 Performance Boost: ~99% Faster!

3️⃣ Indexing for Even Faster Queries
🔍 Before Indexing:
⏳ Execution Time: 0.068 ms

![Before Indexing](docs/images/03_before_indexing.png)

✅ After Indexing:
⏳ Execution Time: 0.028 ms

![After Indexing](docs/images/03_after_indexing.png)