/*
 Navicat Premium Data Transfer

 Source Server         : Localhost
 Source Server Type    : PostgreSQL
 Source Server Version : 90504
 Source Host           : localhost
 Source Database       : iqfx
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 90504
 File Encoding         : utf-8

 Date: 01/27/2017 14:20:14 PM
*/

-- ----------------------------
--  Sequence structure for actives_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."actives_id_seq";
CREATE SEQUENCE "public"."actives_id_seq" INCREMENT 1 START 2890 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."actives_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for orders_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."orders_id_seq";
CREATE SEQUENCE "public"."orders_id_seq" INCREMENT 1 START 902 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."orders_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for patterns_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."patterns_id_seq";
CREATE SEQUENCE "public"."patterns_id_seq" INCREMENT 1 START 79221 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."patterns_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for predictions_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."predictions_id_seq";
CREATE SEQUENCE "public"."predictions_id_seq" INCREMENT 1 START 298743 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."predictions_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for sequences_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sequences_id_seq";
CREATE SEQUENCE "public"."sequences_id_seq" INCREMENT 1 START 79270 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."sequences_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for settings_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."settings_id_seq";
CREATE SEQUENCE "public"."settings_id_seq" INCREMENT 1 START 13 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."settings_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for signals_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."signals_id_seq";
CREATE SEQUENCE "public"."signals_id_seq" INCREMENT 1 START 62 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."signals_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for tasks_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."tasks_id_seq";
CREATE SEQUENCE "public"."tasks_id_seq" INCREMENT 1 START 545 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."tasks_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for workers_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."workers_id_seq";
CREATE SEQUENCE "public"."workers_id_seq" INCREMENT 1 START 658 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."workers_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Function structure for public.make_candles(int4, _int4, int4)
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."make_candles"(int4, _int4, int4);
CREATE FUNCTION "public"."make_candles"(IN input_ts int4, IN input_durations _int4, IN input_instrument_id int4) RETURNS "void" 
	AS $BODY$
DECLARE
  duration_key     INT;
  high_var         REAL = 0;
  low_var          REAL = 0;
  open_var         REAL = 0;
  close_var        REAL = 0;
  average_var      REAL = 0;
  range_var        REAL = 0;
  change_var       REAL = 0;
  last_change_var  REAL = 0;
  change_power_var REAL = 0;
BEGIN
  FOREACH duration_key IN ARRAY input_durations
  LOOP
    RAISE INFO '%', duration_key;
    SELECT
      MAX(value)
      OVER w AS high,
      MIN(value)
      OVER w AS low,
      first_value(value)
      OVER w AS open,
      last_value(value)
      OVER w AS close,
      AVG(value)
      OVER w AS average
    INTO high_var, low_var, open_var, close_var, average_var
    FROM quotations
    WHERE ts >= (input_ts - duration_key) AND instrument_id = input_instrument_id AND ts <= input_ts
    WINDOW w AS ()
    ORDER BY ts DESC
    LIMIT 1;

    IF high_var IS NOT NULL AND low_var IS NOT NULL
    THEN
      range_var = high_var - low_var;
    END IF;

    IF open_var IS NOT NULL AND close_var IS NOT NULL
    THEN
      change_var = open_var - close_var;
    END IF;

    SELECT change
    INTO last_change_var
    FROM candles
    WHERE
      instrument_id = input_instrument_id AND duration = duration_key AND till_ts <= input_ts
    ORDER BY till_ts DESC
    LIMIT 1;

    IF last_change_var IS NOT NULL AND last_change_var > 0
    THEN
      change_power_var = change_var / (last_change_var / 100);
    END IF;

    INSERT INTO candles (instrument_id, from_ts, till_ts, duration, high, low, open, close, range, change, average,
                         average_power, range_power, change_power, high_power, low_power)
    VALUES (input_instrument_id, input_ts - duration_key, input_ts, duration_key, high_var, low_var, open_var,
                                 close_var, range_var, change_var, average_var, 0, 0, change_power_var, 0, 0)
    ON CONFLICT (instrument_id, from_ts, till_ts)
      DO NOTHING;

  END LOOP;
  RETURN;
END
$BODY$
	LANGUAGE plpgsql
	COST 100
	CALLED ON NULL INPUT
	SECURITY INVOKER
	VOLATILE;
ALTER FUNCTION "public"."make_candles"(IN input_ts int4, IN input_durations _int4, IN input_instrument_id int4) OWNER TO "postgres";

-- ----------------------------
--  Table structure for tasks
-- ----------------------------
DROP TABLE IF EXISTS "public"."tasks";
CREATE TABLE "public"."tasks" (
	"id" int4 NOT NULL DEFAULT nextval('tasks_id_seq'::regclass),
	"user_id" int4,
	"setting_id" int4,
	"worker_id" int4,
	"is_enabled" bool,
	"service_name" varchar COLLATE "default",
	"params" json,
	"status" json,
	"thread" varchar COLLATE "default",
	"start_at" int4,
	"launched_at" int4,
	"stop_at" int4,
	"terminated_at" int4,
	"handled_exceptions" json
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."tasks" OWNER TO "postgres";

-- ----------------------------
--  Table structure for predictions
-- ----------------------------
DROP TABLE IF EXISTS "public"."predictions";
CREATE TABLE "public"."predictions" (
	"id" int8 NOT NULL DEFAULT nextval('predictions_id_seq'::regclass),
	"sequence_id" int8,
	"setting_id" int4,
	"task_id" int4,
	"time_bid" int4,
	"pattern_id" int4,
	"created_cost" float4,
	"expiration_cost" float4,
	"last_cost" float4,
	"range_max_change_cost" float4,
	"range_max_avg_change_cost" float4,
	"call_max_change_cost" float4,
	"put_max_change_cost" float4,
	"call_max_avg_change_cost" float4,
	"put_max_avg_change_cost" float4,
	"range_sum_max_change_cost" float4,
	"call_sum_max_change_cost" float4,
	"put_sum_max_change_cost" float4,
	"count_change_cost" int4,
	"created_at" int4,
	"expiration_at" int4,
	"history_num" int4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."predictions" OWNER TO "postgres";

-- ----------------------------
--  Table structure for workers
-- ----------------------------
DROP TABLE IF EXISTS "public"."workers";
CREATE TABLE "public"."workers" (
	"id" int4 NOT NULL DEFAULT nextval('workers_id_seq'::regclass),
	"host_name" varchar COLLATE "default",
	"pid" int4,
	"launched_at" int4,
	"terminated_at" int4,
	"terminated_code" varchar COLLATE "default",
	"terminated_traceback" json,
	"terminated_description" text COLLATE "default"
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."workers" OWNER TO "postgres";

-- ----------------------------
--  Table structure for sequences
-- ----------------------------
DROP TABLE IF EXISTS "public"."sequences";
CREATE TABLE "public"."sequences" (
	"id" int8 NOT NULL DEFAULT nextval('sequences_id_seq'::regclass),
	"json" json,
	"hash" varchar COLLATE "default",
	"duration" int4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."sequences" OWNER TO "postgres";

-- ----------------------------
--  Table structure for candles
-- ----------------------------
DROP TABLE IF EXISTS "public"."candles";
CREATE TABLE "public"."candles" (
	"instrument_id" int2 NOT NULL,
	"from_ts" int4 NOT NULL,
	"till_ts" int4 NOT NULL,
	"duration" int4,
	"high" float4,
	"low" float4,
	"open" float4,
	"close" float4,
	"range" float4,
	"change" float4,
	"average" float4,
	"average_power" float4 DEFAULT 0,
	"range_power" float4,
	"change_power" float4,
	"high_power" float4,
	"low_power" float4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."candles" OWNER TO "postgres";

COMMENT ON COLUMN "public"."candles"."instrument_id" IS 'ИД актива';
COMMENT ON COLUMN "public"."candles"."from_ts" IS 'От';
COMMENT ON COLUMN "public"."candles"."till_ts" IS 'До';
COMMENT ON COLUMN "public"."candles"."duration" IS 'Длительность';
COMMENT ON COLUMN "public"."candles"."high" IS 'Высшее значение свечи за сек';
COMMENT ON COLUMN "public"."candles"."low" IS 'Низшее значение свечи за сек';
COMMENT ON COLUMN "public"."candles"."open" IS 'Значение открытия свечи за сек';
COMMENT ON COLUMN "public"."candles"."close" IS 'Значение закрытия свечи за сек';
COMMENT ON COLUMN "public"."candles"."range" IS 'Значение изменения за сек';
COMMENT ON COLUMN "public"."candles"."average" IS 'Среднее значение за сек';
COMMENT ON COLUMN "public"."candles"."average_power" IS 'Относительная сила к прошлому изменению в процентах';

-- ----------------------------
--  Table structure for quotations
-- ----------------------------
DROP TABLE IF EXISTS "public"."quotations";
CREATE TABLE "public"."quotations" (
	"ts" int4 NOT NULL,
	"instrument_id" int2 NOT NULL,
	"ask" float4,
	"bid" float4,
	"value" float4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."quotations" OWNER TO "postgres";

COMMENT ON COLUMN "public"."quotations"."ts" IS 'Временная метка';
COMMENT ON COLUMN "public"."quotations"."instrument_id" IS 'ИД актива';

-- ----------------------------
--  Table structure for instruments
-- ----------------------------
DROP TABLE IF EXISTS "public"."instruments";
CREATE TABLE "public"."instruments" (
	"id" int4 NOT NULL DEFAULT nextval('actives_id_seq'::regclass),
	"instrument" varchar NOT NULL COLLATE "default",
	"pip" float4,
	"name" varchar COLLATE "default"
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."instruments" OWNER TO "postgres";

COMMENT ON COLUMN "public"."instruments"."instrument" IS 'Название актива';

-- ----------------------------
--  Table structure for orders
-- ----------------------------
DROP TABLE IF EXISTS "public"."orders";
CREATE TABLE "public"."orders" (
	"id" int8 NOT NULL DEFAULT nextval('orders_id_seq'::regclass),
	"instrument_id" int4,
	"prediction_id" int8,
	"created_at" int4,
	"expiration_at" int4,
	"direction" int2,
	"created_cost" float4,
	"expiration_cost" float4,
	"change" float4,
	"closed_at" int4,
	"bid_cost" float4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."orders" OWNER TO "postgres";

-- ----------------------------
--  Table structure for signals
-- ----------------------------
DROP TABLE IF EXISTS "public"."signals";
CREATE TABLE "public"."signals" (
	"id" int8 NOT NULL DEFAULT nextval('signals_id_seq'::regclass),
	"instrument_id" int4,
	"sequence_id" int8,
	"setting_id" int4,
	"task_id" int4,
	"prediction_id" int8,
	"pattern_id" int8,
	"created_at" int4,
	"expiration_at" int4,
	"direction" int2,
	"created_cost" float4,
	"expiration_cost" float4,
	"max_cost" float4,
	"min_cost" float4,
	"max_change_cost" float4,
	"min_change_cost" float4,
	"time_bid" int4,
	"history_num" int4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."signals" OWNER TO "postgres";

-- ----------------------------
--  Table structure for patterns
-- ----------------------------
DROP TABLE IF EXISTS "public"."patterns";
CREATE TABLE "public"."patterns" (
	"id" int8 NOT NULL DEFAULT nextval('patterns_id_seq'::regclass),
	"sequence_id" int8,
	"setting_id" int4,
	"task_id" int4,
	"time_bid" int4,
	"used_count" int4,
	"calls_count" int4,
	"puts_count" int4,
	"same_count" int4,
	"last_call" int2,
	"range_max_change_cost" float4,
	"range_max_avg_change_cost" float4,
	"call_max_change_cost" float4,
	"put_max_change_cost" float4,
	"call_max_avg_change_cost" float4,
	"put_max_avg_change_cost" float4,
	"range_sum_max_change_cost" float4,
	"call_sum_max_change_cost" float4,
	"put_sum_max_change_cost" float4,
	"count_change_cost" int4,
	"delay" int4,
	"expires" int4,
	"history_num" int4,
	"created_at" int4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."patterns" OWNER TO "postgres";

-- ----------------------------
--  Table structure for settings
-- ----------------------------
DROP TABLE IF EXISTS "public"."settings";
CREATE TABLE "public"."settings" (
	"id" int4 NOT NULL DEFAULT nextval('settings_id_seq'::regclass),
	"user_id" int4,
	"name" varchar(255) NOT NULL COLLATE "default",
	"is_default" bool,
	"created_at" int4,
	"updated_at" int4,
	"instrument_id" int4,
	"candles_durations" json,
	"analyzer_working_interval_sec" int4,
	"analyzer_collect_interval_sec" int4,
	"analyzer_bid_times" json,
	"analyzer_deep" int4,
	"analyzer_min_deep" int4,
	"analyzer_prediction_expire" json,
	"analyzer_save_prediction_if_exists" bool,
	"analyzer_candles_parent_relation" varchar COLLATE "default",
	"signaler_min_chance" float4,
	"signaler_min_repeats" int4,
	"signaler_delay_on_trend" int4,
	"signaler_min_change_cost" float4,
	"signaler_max_change_cost" float4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."settings" OWNER TO "postgres";


-- ----------------------------
--  Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."actives_id_seq" RESTART 2891 OWNED BY "instruments"."id";
ALTER SEQUENCE "public"."orders_id_seq" RESTART 903 OWNED BY "orders"."id";
ALTER SEQUENCE "public"."patterns_id_seq" RESTART 79222 OWNED BY "patterns"."id";
ALTER SEQUENCE "public"."predictions_id_seq" RESTART 298744 OWNED BY "predictions"."id";
ALTER SEQUENCE "public"."sequences_id_seq" RESTART 79271 OWNED BY "sequences"."id";
ALTER SEQUENCE "public"."settings_id_seq" RESTART 14 OWNED BY "settings"."id";
ALTER SEQUENCE "public"."signals_id_seq" RESTART 63 OWNED BY "signals"."id";
ALTER SEQUENCE "public"."tasks_id_seq" RESTART 546 OWNED BY "tasks"."id";
ALTER SEQUENCE "public"."workers_id_seq" RESTART 659 OWNED BY "workers"."id";
-- ----------------------------
--  Primary key structure for table tasks
-- ----------------------------
ALTER TABLE "public"."tasks" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table predictions
-- ----------------------------
ALTER TABLE "public"."predictions" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table workers
-- ----------------------------
ALTER TABLE "public"."workers" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table sequences
-- ----------------------------
ALTER TABLE "public"."sequences" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Uniques structure for table sequences
-- ----------------------------
ALTER TABLE "public"."sequences" ADD CONSTRAINT "hash_uniq" UNIQUE ("hash") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table candles
-- ----------------------------
ALTER TABLE "public"."candles" ADD PRIMARY KEY ("instrument_id", "from_ts", "till_ts") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table quotations
-- ----------------------------
ALTER TABLE "public"."quotations" ADD PRIMARY KEY ("ts", "instrument_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table instruments
-- ----------------------------
ALTER TABLE "public"."instruments" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Uniques structure for table instruments
-- ----------------------------
ALTER TABLE "public"."instruments" ADD CONSTRAINT "instrument_uniq" UNIQUE ("instrument") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table orders
-- ----------------------------
ALTER TABLE "public"."orders" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table signals
-- ----------------------------
ALTER TABLE "public"."signals" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table patterns
-- ----------------------------
ALTER TABLE "public"."patterns" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Uniques structure for table patterns
-- ----------------------------
ALTER TABLE "public"."patterns" ADD CONSTRAINT "uniq_key" UNIQUE ("sequence_id","setting_id","time_bid","expires","history_num") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table settings
-- ----------------------------
ALTER TABLE "public"."settings" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

