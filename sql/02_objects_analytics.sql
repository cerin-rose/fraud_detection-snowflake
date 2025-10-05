+---------------------------------------------------+
| GET_DDL('TABLE','FRAUDLAB.ANALYTICS.FRAUD_RULES') |
|---------------------------------------------------|
| create or replace TABLE FRAUD_RULES (             |
| 	RULE_ID NUMBER(38,0),                                                                                                       |
| 	NAME VARCHAR(16777216),                                                                                                       |
| 	SQL_PREDICATE VARCHAR(16777216),                                                                                                       |
| 	SEVERITY VARCHAR(16777216),                                                                                                       |
| 	ACTIVE BOOLEAN                                                                                                       |
| );                                                |
+---------------------------------------------------+
+-------------------------------------------------+
| GET_DDL('TABLE','FRAUDLAB.ANALYTICS.RULE_HITS') |
|-------------------------------------------------|
| create or replace TABLE RULE_HITS (             |
| 	ROW_ID VARCHAR(16777216),                                                                                                   |
| 	TIME_SEC NUMBER(9,0),                                                                                                   |
| 	AMOUNT NUMBER(12,2),                                                                                                   |
| 	RULE_ID NUMBER(38,0),                                                                                                   |
| 	SEVERITY VARCHAR(16777216),                                                                                                   |
| 	HIT_TS TIMESTAMP_NTZ(9)                                                                                                   |
| );                                              |
+-------------------------------------------------+
