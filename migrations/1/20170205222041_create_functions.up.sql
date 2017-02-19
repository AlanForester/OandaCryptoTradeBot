-- *** UP ***
-- file: 1/20170205222041_create_functions
-- comment: create_functions

-- *** UP ***
-- file: 1/20170205221826_create_functions
-- comment: create_functions

----------------------------
--  Function structure for public.make_candles(int4, _int4, int4)
-- ----------------------------
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
ALTER FUNCTION "public"."make_candles"(IN input_ts int4, IN input_durations _int4, IN input_instrument_id int4) OWNER TO "iqfx";

-- ----------------------------
--  Function structure for public.get_till_ts_from_last_candle_on_ts(int4, int4)
-- ----------------------------
CREATE FUNCTION "public"."get_till_ts_from_last_candle_on_ts"(IN input_instrument_id int4, IN input_till_ts int4) RETURNS "int4"
	AS $BODY$
DECLARE
  ret INT;
BEGIN
  SELECT till_ts
  INTO ret
  FROM candles
  WHERE till_ts <= input_till_ts AND instrument_id = input_instrument_id
  ORDER BY till_ts DESC
  LIMIT 1;
  RETURN ret;
END
$BODY$
	LANGUAGE plpgsql
	COST 100
	CALLED ON NULL INPUT
	SECURITY INVOKER
	VOLATILE;
ALTER FUNCTION "public"."get_till_ts_from_last_candle_on_ts"(IN input_instrument_id int4, IN input_till_ts int4) OWNER TO "iqfx";

-- ----------------------------
--  Function structure for public.get_last_candles_on_till_ts(int4, int4, _int4)
-- ----------------------------
CREATE FUNCTION "public"."get_last_candles_on_till_ts"(IN input_instrument_id int4, IN input_till_ts int4, IN input_durations _int4) RETURNS SETOF "public"."candles"
	AS $BODY$
DECLARE
BEGIN
  RETURN QUERY
  SELECT *
  FROM candles
  WHERE till_ts = (SELECT get_till_ts_from_last_candle_on_ts(input_instrument_id, input_till_ts)) AND
        instrument_id = input_instrument_id AND duration = ANY(input_durations);
END
$BODY$
	LANGUAGE plpgsql
	COST 100
	ROWS 1000
	CALLED ON NULL INPUT
	SECURITY INVOKER
	VOLATILE;
ALTER FUNCTION "public"."get_last_candles_on_till_ts"(IN input_instrument_id int4, IN input_till_ts int4, IN input_durations _int4) OWNER TO "iqfx";

-- ----------------------------
--  Function structure for public.get_last_candles_with_nesting(int4, int4, int4, varchar, _int4)
-- ----------------------------
CREATE FUNCTION "public"."get_last_candles_with_nesting"(IN input_instrument_id int4, IN input_till_ts int4, IN input_deep int4, IN input_relation varchar, IN input_durations _int4) RETURNS SETOF "public"."candles"
	AS $BODY$
DECLARE
  deep_var INT = input_deep;
  r        candles%ROWTYPE;
BEGIN
  FOR r IN SELECT *
           FROM get_last_candles_on_till_ts(input_instrument_id, input_till_ts, input_durations)
  LOOP
    deep_var = input_deep - 1;
    IF deep_var > 0
    THEN
      IF input_relation = 'parent'
      THEN
        RETURN QUERY SELECT *
                     FROM get_last_candles_with_nesting(input_instrument_id, r.from_ts, deep_var, input_relation, input_durations);
      END IF;
      IF input_relation = 'related'
      THEN
        RETURN QUERY SELECT *
                     FROM get_last_candles_with_nesting(input_instrument_id, r.till_ts, deep_var, input_relation, input_durations);
      END IF;
    END IF;
    RETURN NEXT r;
  END LOOP;
END;
$BODY$
	LANGUAGE plpgsql
	COST 100
	ROWS 1000
	CALLED ON NULL INPUT
	SECURITY INVOKER
	VOLATILE;
ALTER FUNCTION "public"."get_last_candles_with_nesting"(IN input_instrument_id int4, IN input_till_ts int4, IN input_deep int4, IN input_relation varchar, IN input_durations _int4) OWNER TO "iqfx";
