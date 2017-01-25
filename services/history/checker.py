import time

from helpers.exthread import ExThread
from models.quotation import Quotation
from services.controller import Controller
from services.analyzer import Analyzer


class Checker:

    def __init__(self, task):
        self.task = task
        self.instrument = task.setting.instrument
        start = self.task.get_param("start")
        end = self.task.get_param("end")
        quotations = Quotation.get_from_interval(start, end, self.instrument.id)
        self.task.update_status("checker_total_quotations", len(quotations))
        if len(quotations) > 0:
            # Запускаем демона для проверки кеша и получения результата торгов
            check_thread = ExThread(target=self.checker_daemon)
            check_thread.task = self.task
            check_thread.start()

            checked_quotations = self.task.get_param("checker_checked_quotations")
            if not checked_quotations:
                checked_quotations = 0

            i = 0
            thread_limit = 10
            total_threads = []
            for row in quotations:
                i += 5  # Так как сбор истории идет мин за 5 сек
                if i >= task.setting.analyzer_collect_interval_sec:
                    # Проверка на количество работающих тредов и блокировка
                    ExThread.wait_threads(total_threads, thread_limit)

                    analyzer = Analyzer(task)
                    analyzer.quotation = row
                    analysis_thread = ExThread(target=analyzer.do_analysis)
                    analysis_thread.task = task
                    analysis_thread.start()

                    total_threads.append(analysis_thread)
                    # print "Run analysis thread. Total:", len(total_threads)
                    i = 0

                    checked_quotations += 1
                    self.task.update_status("checker_checked_quotations", checked_quotations)

            # Ждем все потоки
            ExThread.wait_threads(total_threads, 0)

        print("All threads closed")

    def checker_daemon(self):
        signals_count = self.task.get_param("checker_signals_count")
        if not signals_count:
            signals_count = 0
        while True:
            check_result = Controller.check_expired_predictions(self.task)
            if check_result and len(check_result) > 0:
                for check in check_result:
                    print(check)
                    signals_count += 1
                    self.task.update_status("checker_signals_count", signals_count)
            time.sleep(1)

