-- *** DOWN ***
-- file: 1/20170205222041_create_functions
-- comment: create_functions

DROP FUNCTION IF EXISTS "public"."make_candles"(int4, _int4, int4);
DROP FUNCTION IF EXISTS "public"."get_till_ts_from_last_candle_on_ts"(int4, int4);
DROP FUNCTION IF EXISTS "public"."get_last_candles_on_till_ts"(int4, int4, _int4);
DROP FUNCTION IF EXISTS "public"."get_last_candles_with_nesting"(int4, int4, int4, varchar, _int4);
