BEGIN READ ONLY;
SELECT json_build_object(
 'database', current_database(),
 'read_only', current_setting('transaction_read_only'),
 'records', (SELECT json_agg(t ORDER BY id) FROM
   (SELECT id,name,state,quantity,unit_price,amount FROM lab_qualification ORDER BY id) t),
 'module', (SELECT json_agg(t) FROM
   (SELECT id,name,state,latest_version FROM ir_module_module WHERE name='lab_qualification') t),
 'constraints', (SELECT json_agg(t ORDER BY conname) FROM
   (SELECT conname,pg_get_constraintdef(oid) AS definition,convalidated
    FROM pg_constraint WHERE conrelid='lab_qualification'::regclass) t),
 'invalid_confirmed_count', (SELECT count(*) FROM lab_qualification WHERE state='confirmed' AND COALESCE(quantity,0)<=0)
);
ROLLBACK;
