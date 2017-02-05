-- *** DOWN ***
-- file: 1/20170205222036_create_tables
-- comment: create_tables

DROP TABLE IF EXISTS "public"."tasks";
DROP TABLE IF EXISTS "public"."workers";
DROP TABLE IF EXISTS "public"."sequences";
DROP TABLE IF EXISTS "public"."candles";
DROP TABLE IF EXISTS "public"."quotations";
DROP TABLE IF EXISTS "public"."instruments";
DROP TABLE IF EXISTS "public"."orders";
DROP TABLE IF EXISTS "public"."signals";
DROP TABLE IF EXISTS "public"."patterns";
DROP TABLE IF EXISTS "public"."predictions";
DROP TABLE IF EXISTS "public"."settings";

DROP SEQUENCE IF EXISTS "public"."actives_id_seq";
DROP SEQUENCE IF EXISTS "public"."orders_id_seq";
DROP SEQUENCE IF EXISTS "public"."patterns_id_seq";
DROP SEQUENCE IF EXISTS "public"."predictions_id_seq";
DROP SEQUENCE IF EXISTS "public"."sequences_id_seq";
DROP SEQUENCE IF EXISTS "public"."settings_id_seq";
DROP SEQUENCE IF EXISTS "public"."signals_id_seq";
DROP SEQUENCE IF EXISTS "public"."tasks_id_seq";
DROP SEQUENCE IF EXISTS "public"."workers_id_seq";
