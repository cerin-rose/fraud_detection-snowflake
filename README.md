# Snowflake Fraud Detection (Ingest → Stream → Rules)

- Ingests credit card transactions (Kaggle dataset).
- Uses a Snowflake **STREAM** to process only new rows.
- Dynamic rule engine via stored procedure `SP_EVAL_RULES()` writes to `ANALYTICS.RULE_HITS`.

### Recreate

1. Run `sql/00_context.sql`
2. Run `sql/01_objects_raw.sql`
3. Load data with `PUT` → `COPY` (dataset not committed)
4. Run `sql/02_objects_analytics.sql`
5. Run `sql/03_proc_sp_eval_rules.sql`
6. Run `sql/04_seed_rules.sql`
7. `CALL ANALYTICS.SP_EVAL_RULES();`



## Contribution

Anyone is welcome to contribute to this repo

hi

hi2
