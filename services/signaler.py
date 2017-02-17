from models.signal import Signal
from providers.providers import Providers


class Signaler:
    @staticmethod
    def check(task, pattern):
        result = None
        if pattern.delay == 0:
            all_amounts = pattern.calls_count + pattern.puts_count
            all_condition = all_amounts / 100
            if pattern.calls_count < pattern.puts_count:
                if pattern.trend <= -task.setting.signaler_min_repeats:
                    if pattern.puts_count / all_condition >= task.setting.signaler_min_chance:
                        result = 'put'
            else:
                if pattern.calls_count > pattern.puts_count:
                    if pattern.trend >= task.setting.signaler_min_repeats:
                        if pattern.calls_count / all_condition >= task.setting.signaler_min_chance:
                            result = 'call'

            call_change = task.setting.signaler_call_max_change_cost
            put_change = task.setting.signaler_put_max_change_cost

            if call_change > 0:
                if call_change <= pattern.call_max_change_cost:
                    result = None
            if put_change > 0:
                if put_change >= pattern.put_max_change_cost:
                    result = None

            # Проверка на количество тиков
            if result and task.setting.signaler_min_ticks_count > 0:
                change = 0
                if result == 'call':
                    change = pattern.call_max_avg_change_cost
                if result == 'put':
                    change = pattern.put_max_avg_change_cost

                one_tick = task.setting.instrument.pip
                ticks_count = int(change / one_tick)
                if int(ticks_count) < task.setting.signaler_min_ticks_count:
                    result = None

            if result and task.setting.signaler_trend_chance > 0:
                all_trends = pattern.trend_max_call_count + pattern.trend_max_put_count
                trend_condition = all_trends / 100
                if result == 'call':
                    if pattern.trend_max_call_count / trend_condition <= task.setting.signaler_trend_chance:
                        result = None
                if result == 'put':
                    if pattern.trend_max_put_count / trend_condition <= task.setting.signaler_trend_chance:
                        result = None

        return result

    @staticmethod
    def make_and_save(task, direction, pattern, prediction):
        signal = Signal()
        signal.sequence_id = prediction.sequence_id
        signal.expiration_at = prediction.created_at + prediction.time_bid
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
        signal.call_max_change_cost = pattern.call_max_change_cost
        signal.put_max_change_cost = pattern.put_max_change_cost

        task.storage.signals.append(signal)
        if task.get_param("history_num") == 0:
            Providers.telebot().send_signal(task.setting.instrument.instrument + ": "
                                            + "Новый сигнал: " + str(direction) + ". Время:" + str(prediction.time_bid)
                                            + ". Цена " + str(round(prediction.created_cost, 5)) + " изменится на "
                                            + str(round(expiration_cost - prediction.created_cost, 5))
                                            + " и станет " + str(round(expiration_cost, 5)))

        return signal.save()
