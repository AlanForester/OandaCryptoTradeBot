-- *** UP ***
-- file: 1/20170205222036_create_tables
-- comment: create_tables

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

 Date: 02/05/2017 21:08:26 PM
*/

-- ----------------------------
--  Sequence structure for actives_id_seq
-- ----------------------------
CREATE SEQUENCE "public"."actives_id_seq" INCREMENT 1 START 1 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."actives_id_seq" OWNER TO "iqfx";

-- ----------------------------
--  Sequence structure for orders_id_seq
-- ----------------------------
CREATE SEQUENCE "public"."orders_id_seq" INCREMENT 1 START 1 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."orders_id_seq" OWNER TO "iqfx";

-- ----------------------------
--  Sequence structure for patterns_id_seq
-- ----------------------------
CREATE SEQUENCE "public"."patterns_id_seq" INCREMENT 1 START 1 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."patterns_id_seq" OWNER TO "iqfx";

-- ----------------------------
--  Sequence structure for predictions_id_seq
-- ----------------------------
CREATE SEQUENCE "public"."predictions_id_seq" INCREMENT 1 START 1 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."predictions_id_seq" OWNER TO "iqfx";

-- ----------------------------
--  Sequence structure for settings_id_seq
-- ----------------------------
CREATE SEQUENCE "public"."settings_id_seq" INCREMENT 1 START 1 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."settings_id_seq" OWNER TO "iqfx";

-- ----------------------------
--  Sequence structure for signals_id_seq
-- ----------------------------
CREATE SEQUENCE "public"."signals_id_seq" INCREMENT 1 START 1 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."signals_id_seq" OWNER TO "iqfx";

-- ----------------------------
--  Sequence structure for tasks_id_seq
-- ----------------------------
CREATE SEQUENCE "public"."tasks_id_seq" INCREMENT 1 START 1 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."tasks_id_seq" OWNER TO "iqfx";

-- ----------------------------
--  Sequence structure for workers_id_seq
-- ----------------------------
CREATE SEQUENCE "public"."workers_id_seq" INCREMENT 1 START 1 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."workers_id_seq" OWNER TO "iqfx";


-- ----------------------------
--  Table structure for tasks
-- ----------------------------
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
ALTER TABLE "public"."tasks" OWNER TO "iqfx";

-- ----------------------------
--  Table structure for workers
-- ----------------------------
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
ALTER TABLE "public"."workers" OWNER TO "iqfx";

-- ----------------------------
--  Table structure for candles
-- ----------------------------
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
ALTER TABLE "public"."candles" OWNER TO "iqfx";

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
CREATE TABLE "public"."quotations" (
	"ts" int4 NOT NULL,
	"instrument_id" int2 NOT NULL,
	"ask" float4,
	"bid" float4,
	"value" float4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."quotations" OWNER TO "iqfx";

COMMENT ON COLUMN "public"."quotations"."ts" IS 'Временная метка';
COMMENT ON COLUMN "public"."quotations"."instrument_id" IS 'ИД актива';

-- ----------------------------
--  Table structure for instruments
-- ----------------------------
CREATE TABLE "public"."instruments" (
	"id" int4 NOT NULL DEFAULT nextval('actives_id_seq'::regclass),
	"instrument" varchar COLLATE "default" NOT NULL,
	"pip" float4,
	"name" varchar COLLATE "default",
	"not_working_time" json
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."instruments" OWNER TO "iqfx";

COMMENT ON COLUMN "public"."instruments"."instrument" IS 'Название актива';

-- ----------------------------
--  Table structure for orders
-- ----------------------------
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
ALTER TABLE "public"."orders" OWNER TO "iqfx";

-- ----------------------------
--  Table structure for signals
-- ----------------------------
CREATE TABLE "public"."signals" (
	"id" int8 NOT NULL DEFAULT nextval('signals_id_seq'::regclass),
	"instrument_id" int4,
	"setting_id" int4,
	"task_id" int4,
	"pattern_id" int8,
	"created_at" int4,
	"expiration_at" int4,
	"direction" int2,
	"created_cost" float4,
	"expiration_cost" float4,
	"closed_cost" float4,
	"closed_discrepancy_cost" float4,
	"closed_change_cost" float4,
	"max_cost" float4,
	"min_cost" float4,
	"call_max_change_cost" float4,
	"put_max_change_cost" float4,
	"time_bid" int4,
	"history_num" int4,
	"is_read" bool
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."signals" OWNER TO "iqfx";

-- ----------------------------
--  Table structure for patterns
-- ----------------------------
CREATE TABLE "public"."patterns" (
	"id" int8 NOT NULL DEFAULT nextval('patterns_id_seq'::regclass),
	"setting_id" int4,
	"task_id" int4,
	"time_bid" int4,
	"sequence" text,
	"sequence_duration" int4,
	"used_count" int4,
	"calls_count" int4,
	"puts_count" int4,
	"same_count" int4,
	"trend" int2,
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
	"created_at" int4,
	"trend_max_call_count" int2,
	"trend_max_put_count" int2
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."patterns" OWNER TO "iqfx";

-- ----------------------------
--  Table structure for predictions
-- ----------------------------
CREATE TABLE "public"."predictions" (
	"id" int8 NOT NULL DEFAULT nextval('predictions_id_seq'::regclass),
	"setting_id" int4,
	"task_id" int4,
	"time_bid" int4,
	"pattern_id" int4,
	"created_cost" float4,
	"created_ask" float4,
	"created_bid" float4,
	"expiration_cost" float4,
	"expiration_ask" float4,
	"expiration_bid" float4,
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
	"history_num" int4,
	"time_to_expiration" int4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."predictions" OWNER TO "iqfx";

-- ----------------------------
--  Table structure for settings
-- ----------------------------
CREATE TABLE "public"."settings" (
	"id" int4 NOT NULL DEFAULT nextval('settings_id_seq'::regclass),
	"user_id" varchar COLLATE "default",
	"name" varchar(255) COLLATE "default" NOT NULL,
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
	"analyzer_patterns_control" json,
	"analyzer_candles_parent_relation" varchar COLLATE "default",
	"analyzer_expiry_time_bid_divider" int4,
	"analyzer_capacity_granularity" float4,
	"analyzer_capacity_type" varchar COLLATE "default",
	"signaler_min_chance" float4,
	"signaler_min_repeats" int4,
	"signaler_delay_on_trend" int4,
	"signaler_call_max_change_cost" float4,
	"signaler_put_max_change_cost" float4,
	"signaler_min_ticks_count" float4,
	"signaler_trend_chance" int4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."settings" OWNER TO "iqfx";


-- ----------------------------
--  Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."actives_id_seq" RESTART 4016 OWNED BY "instruments"."id";
ALTER SEQUENCE "public"."orders_id_seq" RESTART 904 OWNED BY "orders"."id";
ALTER SEQUENCE "public"."patterns_id_seq" RESTART 800726 OWNED BY "patterns"."id";
ALTER SEQUENCE "public"."predictions_id_seq" RESTART 995795 OWNED BY "predictions"."id";
ALTER SEQUENCE "public"."settings_id_seq" RESTART 22 OWNED BY "settings"."id";
ALTER SEQUENCE "public"."signals_id_seq" RESTART 105323 OWNED BY "signals"."id";
ALTER SEQUENCE "public"."tasks_id_seq" RESTART 672 OWNED BY "tasks"."id";
ALTER SEQUENCE "public"."workers_id_seq" RESTART 785 OWNED BY "workers"."id";
-- ----------------------------
--  Primary key structure for table tasks
-- ----------------------------
ALTER TABLE "public"."tasks" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table workers
-- ----------------------------
ALTER TABLE "public"."workers" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;


-- ----------------------------
--  Primary key structure for table candles
-- ----------------------------
ALTER TABLE "public"."candles" ADD PRIMARY KEY ("instrument_id", "from_ts", "till_ts") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Indexes structure for table candles
-- ----------------------------
CREATE INDEX  "instr_dur_till" ON "public"."candles" USING btree(instrument_id ASC NULLS LAST, duration ASC NULLS LAST, till_ts ASC NULLS LAST);
CREATE INDEX  "till_instr" ON "public"."candles" USING btree(till_ts ASC NULLS LAST, instrument_id ASC NULLS LAST);

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
ALTER TABLE "public"."patterns" ADD CONSTRAINT "uniq_key" UNIQUE ("sequence","setting_id","time_bid","expires","history_num") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Indexes structure for table patterns
-- ----------------------------
CREATE INDEX  "seq_set_tb_his" ON "public"."patterns" USING btree(sequence ASC NULLS LAST, setting_id ASC NULLS LAST, time_bid ASC NULLS LAST, history_num ASC NULLS LAST);

-- ----------------------------
--  Primary key structure for table predictions
-- ----------------------------
ALTER TABLE "public"."predictions" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Uniques structure for table predictions
-- ----------------------------
ALTER TABLE "public"."predictions" ADD CONSTRAINT "uniq" UNIQUE ("setting_id","time_bid","pattern_id","expiration_at","time_to_expiration","history_num") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Indexes structure for table predictions
-- ----------------------------
CREATE INDEX  "created_cost" ON "public"."predictions" USING btree(expiration_cost ASC NULLS LAST, setting_id ASC NULLS LAST, expiration_at ASC NULLS LAST);
CREATE INDEX  "ex_set_his" ON "public"."predictions" USING btree(setting_id ASC NULLS LAST, expiration_cost ASC NULLS LAST, history_num ASC NULLS LAST);

-- ----------------------------
--  Primary key structure for table settings
-- ----------------------------
ALTER TABLE "public"."settings" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

