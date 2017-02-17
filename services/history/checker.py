import time

from helpers.exthread import ExThread
from models.quotation import Quotation
from services.controller import Controller
from services.analyzer import Analyzer
from models.prediction import Prediction


class Checker:
    def __init__(self, task):
        self.task = task
        self.instrument = task.setting.instrument
        start = self.task.get_param("start")
        end = self.task.get_param("end")
        quotations = Quotation.get_from_interval(start, end, self.instrument.id)
        self.task.update_status("checker_total_quotations", len(quotations))
        last_quotation = None
        if len(quotations) > 0:
            checked_quotations = self.task.get_param("checker_checked_quotations")
            if not checked_quotations:
                checked_quotations = 0

            i = 0
            thread_limit = 10
            total_threads = []
            for row in quotations:
                i += 5  # Так как сбор истории идет мин за 5 сек
                if i >= task.setting.analyzer_collect_interval_sec:
                    print(row.ts)
                    # Проверка на количество работающих тредов и блокировка
                    ExThread.wait_threads(total_threads, thread_limit)

                    analyzer = Analyzer(task)
                    analyzer.quotation = row
                    # analysis_thread = ExThread(target=analyzer.do_analysis)
                    # analysis_thread.task = task
                    # analysis_thread.start()
                    analyzer.do_analysis()
                    # print "Run analysis thread. Total:", len(total_threads)
                    i = 0
                    last_quotation = analyzer.quotation

                    Prediction.calculation_cost_for_topical(task, last_quotation)
                    Controller.update_expired_signals(self.task, last_quotation)

                    checked_quotations += 1
                    if checked_quotations % 10 == 0:
                        # Обновляем параметры стоимости прогнозов
                        self.task.update_status("checker_checked_quotations", checked_quotations)

                    # Запускаем демона для проверки кеша и получения результата торгов
                    if checked_quotations % 100 == 0:
                        self.checker_predictions(last_quotation)

            # Ждем все потоки
            ExThread.wait_threads(total_threads, 0)
            # Обновляем параметры стоимости прогнозов
            if last_quotation:
                self.checker_predictions(last_quotation)

    def checker_predictions(self, last_quotation):
        Controller.check_expired_predictions(self.task, last_quotation)
