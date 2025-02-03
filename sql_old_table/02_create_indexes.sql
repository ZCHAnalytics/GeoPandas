-- 02_create_indexes.sql 

-- Add indexes 
CREATE INDEX idx_train_date ON train_tracking_master (date);
CREATE INDEX idx_train_dest ON train_tracking_master (destination);
CREATE INDEX idx_train_date_dest ON train_tracking_master (date, destination);
