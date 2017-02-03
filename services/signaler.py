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
                    if pattern.last_call >= task.setting.signaler_min_repeats:
                        if pattern.calls_count / all_condition > task.setting.signaler_min_chance:
                            result = 'call'

            min_call_change = task.setting.signaler_max_change_cost
            min_put_change = task.setting.signaler_min_change_cost

            if min_call_change > 0:
                if min_call_change >= pattern.call_max_change_cost:
                    result = None
            if min_put_change > 0:
                if min_put_change >= pattern.put_max_change_cost:
                    result = None

            # Проверка на количество тиков
            if result:
                change = 0
                if result == 'call':
                    change = pattern.call_max_change_cost
                if result == 'put':
                    change = pattern.put_max_change_cost

                one_tick = task.setting.instrument.pip
                ticks_count = int(change / one_tick)
                if ticks_count < task.setting.signaler_min_ticks_count:
                    result = None

        return result

    @staticmethod
    def make_and_save(task, direction, pattern, prediction):
        signal = Signal()
        signal.sequence_id = prediction.sequence_id
        signal.expiration_at = prediction.created_at + prediction.time_bid
        signal.prediction_id = prediction.id
        signal.setting_id = prediction.setting_id
        signal.time_bid = prediction.time_bid
        signal.task_id = task.id
        signal.history_num = task.get_param("history_num")
        signal.pattern_id = prediction.pattern_id
        signal.created_cost = prediction.created_cost
        direction_status = 0
        if direction == 'call':
            direction_status = 1
        if direction == 'put':
            direction_status = -1
        signal.direction = direction_status
        signal.instrument_id = task.setting.instrument_id
        signal.created_at = prediction.created_at

        if direction == 'call':
            expiration_cost = prediction.created_cost + pattern.call_max_avg_change_cost
        else:
            expiration_cost = prediction.created_cost - pattern.put_max_avg_change_cost
        signal.expiration_cost = expiration_cost

        signal.max_cost = prediction.created_cost + pattern.call_max_change_cost
        signal.min_cost = prediction.created_cost - pattern.put_max_change_cost
        signal.max_change_cost = pattern.call_max_change_cost
        signal.min_change_cost = pattern.put_max_change_cost
        return signal.save()
