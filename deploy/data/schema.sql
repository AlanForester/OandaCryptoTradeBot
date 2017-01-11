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

 Date: 01/12/2017 01:26:31 AM
*/

-- ----------------------------
--  Sequence structure for actives_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."actives_id_seq";
CREATE SEQUENCE "public"."actives_id_seq" INCREMENT 1 START 1291 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."actives_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for orders_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."orders_id_seq";
CREATE SEQUENCE "public"."orders_id_seq" INCREMENT 1 START 894 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."orders_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for predictions_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."predictions_id_seq";
CREATE SEQUENCE "public"."predictions_id_seq" INCREMENT 1 START 219656 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."predictions_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for settings_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."settings_id_seq";
CREATE SEQUENCE "public"."settings_id_seq" INCREMENT 1 START 33 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."settings_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for tasks_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."tasks_id_seq";
CREATE SEQUENCE "public"."tasks_id_seq" INCREMENT 1 START 246 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."tasks_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Sequence structure for workers_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."workers_id_seq";
CREATE SEQUENCE "public"."workers_id_seq" INCREMENT 1 START 359 MAXVALUE 9223372036854775807 MINVALUE 1 CACHE 1;
ALTER TABLE "public"."workers_id_seq" OWNER TO "postgres";

-- ----------------------------
--  Table structure for predictions
-- ----------------------------
DROP TABLE IF EXISTS "public"."predictions";
CREATE TABLE "public"."predictions" (
	"id" int8 NOT NULL DEFAULT nextval('predictions_id_seq'::regclass),
	"setting_id" int4,
	"instrument_id" int4,
	"time_bid" int4,
	"sequence" json,
	"sequence_hash" int4,
	"created_cost" float4,
	"expiration_cost" float4,
	"admission" float4,
	"change" float4,
	"expires" int4,
	"delay" int4,
	"created_at" int4,
	"expiration_at" int4,
	"task_id" int4
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
	"working_interval_sec" int4,
	"analyzer_bid_times" json,
	"analyzer_deep" int4,
	"analyzer_min_deep" int4,
	"analyzer_prediction_expire" json,
	"analyzer_save_prediction_if_exists" bool,
	"trader_min_chance" float4,
	"trader_min_repeats" int4,
	"trader_delay_on_trend" int4,
	"trader_max_count_orders_for_expiration_time" int4
)
WITH (OIDS=FALSE);
ALTER TABLE "public"."settings" OWNER TO "postgres";

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
--  Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."actives_id_seq" RESTART 1292 OWNED BY "instruments"."id";
ALTER SEQUENCE "public"."orders_id_seq" RESTART 895 OWNED BY "orders"."id";
ALTER SEQUENCE "public"."predictions_id_seq" RESTART 219657 OWNED BY "predictions"."id";
ALTER SEQUENCE "public"."settings_id_seq" RESTART 34 OWNED BY "settings"."id";
ALTER SEQUENCE "public"."tasks_id_seq" RESTART 247 OWNED BY "tasks"."id";
ALTER SEQUENCE "public"."workers_id_seq" RESTART 360 OWNED BY "workers"."id";
-- ----------------------------
--  Primary key structure for table predictions
-- ----------------------------
ALTER TABLE "public"."predictions" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table workers
-- ----------------------------
ALTER TABLE "public"."workers" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table candles
-- ----------------------------
ALTER TABLE "public"."candles" ADD PRIMARY KEY ("instrument_id", "from_ts", "till_ts") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table quotations
-- ----------------------------
ALTER TABLE "public"."quotations" ADD PRIMARY KEY ("ts", "instrument_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table tasks
-- ----------------------------
ALTER TABLE "public"."tasks" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table instruments
-- ----------------------------
ALTER TABLE "public"."instruments" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Uniques structure for table instruments
-- ----------------------------
ALTER TABLE "public"."instruments" ADD CONSTRAINT "instrument_uniq" UNIQUE ("instrument") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table settings
-- ----------------------------
ALTER TABLE "public"."settings" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table orders
-- ----------------------------
ALTER TABLE "public"."orders" ADD PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

