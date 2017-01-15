class Trader:
    @staticmethod
    def check(task, prediction):
        # setting pattern
        result = None
        if delay == 0:
            call_amount = 0.0
            put_amount = 0.0
            if call_count:
                call_amount = call_count
            if put_count:
                put_amount = put_count

            all_amounts = call_amount + put_amount
            all_condition = float(all_amounts) / 100
            if call_amount < put_amount:
                # print "Amounts put: ", float(put_amount)/all_condition, all_condition
                if last_call <= -self.settings.trader_min_repeats:
                    if float(put_amount) / all_condition > float(self.settings.trader_min_chance):
                        # if not self.is_test:
                        # print "Amounts:", used_count, call_amount, put_amount, last_call
                        # print "Put:", float(put_amount) / all_condition, float(self.settings.trader_min_chance)
                        result = 'put'
            else:
                if call_amount > put_amount:
                    # print "Amounts call: ", float(call_amount)/all_condition, all_condition
                    if last_call >= self.settings.trader_min_repeats:
                        if float(call_amount) / all_condition > float(self.settings.trader_min_chance):
                            # if not self.is_test:
                            # print "Amounts:", used_count, call_amount, put_amount, last_call
                            # print "Call: ", float(call_amount) / all_condition, float(
                            #     self.settings.trader_min_chance)
                            result = 'call'
        return result