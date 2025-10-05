+-------------------------------------------------------------------------------------------------------+
| GET_DDL('PROCEDURE','FRAUDLAB.ANALYTICS.SP_EVAL_RULES()')                                             |
|-------------------------------------------------------------------------------------------------------|
| CREATE OR REPLACE PROCEDURE "SP_EVAL_RULES"()                                                         |
| RETURNS VARCHAR                                                                                       |
| LANGUAGE SQL                                                                                          |
| EXECUTE AS CALLER                                                                                     |
| AS '                                                                                                  |
| DECLARE                                                                                               |
|   v_sql  STRING;                                                                                      |
|   v_stmt STRING;                                                                                      |
| BEGIN                                                                                                 |
|   /* Build UNION ALL across active rules into one statement */                                        |
|   SELECT LISTAGG(                                                                                     |
|            ''SELECT s.METADATA$ROW_ID, s.TIME_SEC, s.AMOUNT, '' || RULE_ID || '', '' ||               |
|            '''''''' || REPLACE(SEVERITY, '''''''', '''''''''''') || '''''', CURRENT_TIMESTAMP() '' || |
|            ''FROM RAW.CREDITCARD_TXNS_STREAM s WHERE '' || SQL_PREDICATE,                             |
|            '' UNION ALL ''                                                                            |
|          ) WITHIN GROUP (ORDER BY RULE_ID)                                                            |
|     INTO :v_sql                                                                                       |
|   FROM ANALYTICS.FRAUD_RULES                                                                          |
|   WHERE ACTIVE = TRUE;                                                                                |
|                                                                                                       |
|   IF (v_sql IS NOT NULL) THEN                                                                         |
|     v_stmt := ''INSERT INTO ANALYTICS.RULE_HITS '' ||                                                 |
|               ''(ROW_ID, TIME_SEC, AMOUNT, RULE_ID, SEVERITY, HIT_TS) '' || v_sql;                    |
|     EXECUTE IMMEDIATE :v_stmt;                                                                        |
|   END IF;                                                                                             |
|                                                                                                       |
|   RETURN ''ok'';                                                                                      |
| END;                                                                                                  |
| ';                                                                                                    |
+-------------------------------------------------------------------------------------------------------+
