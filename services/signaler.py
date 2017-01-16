class Signaler:
    @staticmethod
    def check(task, pattern):
        result = None
        if pattern.delay == 0:
            all_amounts = pattern.call_amount + pattern.put_amount
            all_condition = all_amounts / 100
            if pattern.call_amount < pattern.put_amount:
                if pattern.last_call <= -task.settings.signaler_min_repeats:
                    if pattern.puts_count / all_condition > task.settings.signaler_min_chance:
                        result = 'put'
            else:
                if pattern.call_amount > pattern.put_amount:
                    if pattern.last_call >= task.settings.trader_min_repeats:
                        if pattern.call_amount / all_condition > task.settings.signaler_min_chance:
                            result = 'call'
            # TODO: Добавить параметры максимальной цены ограничителя
            # TODO: Добавить параметры минимальной цены ограничителя

        return result
