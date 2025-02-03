
-- 01_create_partition.sql 

-- Create a partitioned table to speed up queries by date 

-- Rename the current table to prevent data loss 
ALTER TABLE train_tracking_master RENAME TO train_tracking_master_old;

-- Create a partitioned master table
CREATE TABLE train_tracking_master (
    id SERIAL,
    train_number VARCHAR(10) NOT NULL,
    operator VARCHAR(50) NOT NULL,
    origin VARCHAR(50) NOT NULL,
    destination VARCHAR(50) NOT NULL,
    scheduled_arrival TIME NOT NULL,
    actual_arrival TIME NOT NULL,
    delay_minutes INTEGER,
    date DATE NOT NULL,
	PRIMARY KEY (date, id) -- include a partition key 
) PARTITION BY RANGE (date);

-- Create partitions for January and February 2025
CREATE TABLE train_tracking_2025_01 PARTITION OF train_tracking_master 
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE train_tracking_2025_02 PARTITION OF train_tracking_master 
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');