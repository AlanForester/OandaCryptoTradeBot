class Signaler:
    @staticmethod
    def check(task, pattern):
        result = None
        if pattern.delay == 0:
            all_amounts = pattern.calls_count + pattern.puts_count
            all_condition = all_amounts / 100
            if pattern.calls_count < pattern.puts_count:
                if pattern.last_call <= -task.settings.signaler_min_repeats:
                    if pattern.puts_count / all_condition > task.settings.signaler_min_chance:
                        result = 'put'
            else:
                if pattern.calls_count > pattern.puts_count:
                    if pattern.last_call >= task.settings.trader_min_repeats:
                        if pattern.calls_count / all_condition > task.settings.signaler_min_chance:
                            result = 'call'
            # TODO: Добавить параметры максимальной цены ограничителя
            # TODO: Добавить параметры минимальной цены ограничителя

        return result
