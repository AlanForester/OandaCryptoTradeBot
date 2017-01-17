from models.signal import Signal


class Signaler:
    @staticmethod
    def check(task, pattern):
        result = None
        if pattern.delay == 0:
            all_amounts = pattern.calls_count + pattern.puts_count
            all_condition = all_amounts / 100
            if pattern.calls_count < pattern.puts_count:
                if pattern.last_call <= -task.setting.signaler_min_repeats:
                    if pattern.puts_count / all_condition > task.setting.signaler_min_chance:
                        result = 'put'
            else:
                if pattern.calls_count > pattern.puts_count:
                    if pattern.last_call >= task.setting.trader_min_repeats:
                        if pattern.calls_count / all_condition > task.setting.signaler_min_chance:
                            result = 'call'

            max_change = task.setting.signaler_max_change_cost
            min_change = task.setting.signaler_min_change_cost

            if 0 < max_change < pattern.max_change:
                result = None
            if 0 < min_change > pattern.min_change:
                result = None

        return result

    @staticmethod
    def make_and_save(task, sequence, quotation, direction, time_bid, pattern, prediction):
        signal = Signal()
        signal.sequence_id = sequence.id
        signal.expiration_at = quotation.ts + time_bid
        signal.prediction_id = prediction.id
        signal.setting_id = task.setting_id
        signal.time_bid = time_bid
        signal.task_id = task.id
        signal.history_num = task.get_param("history_num")
        signal.pattern_id = pattern.id
        signal.created_cost = quotation.value
        signal.direction = direction
        signal.instrument_id = task.setting.instrument_id
        signal.created_at = quotation.ts

        if direction == 'call':
            expiration_cost = quotation.value + pattern.max_avg_change
        else:
            expiration_cost = quotation.value - pattern.min_avg_change
        signal.expiration_cost = expiration_cost

        signal.max_cost = quotation.value + pattern.max_change
        signal.min_cost = quotation.value - pattern.min_change
        signal.max_change_cost = pattern.max_change
        signal.min_change_cost = pattern.min_change
        return signal.save()
