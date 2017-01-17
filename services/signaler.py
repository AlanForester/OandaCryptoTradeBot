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
            if pattern.max_change > max_change or pattern.min_change < min_change:
                result = None

        return result
