class Checker:
    def __init__(self, task):
        print("Checker")
        cursor = starter.db.cursor()
        cursor.execute(
            "SELECT * FROM quotations WHERE ts>=%s AND ts<=%s AND active_id=%s ORDER BY ts;",
            (begin, end, starter.settings.active["db_id"]))
        rows = cursor.fetchall()
        if len(rows) > 0:
            """Запускаем демона для проверки кеша и получения результата торгов"""
            check_thread = threading.Thread(target=checker_daemon, args=(predictor,))
            check_thread.setDaemon(True)
            check_thread.start()

            i = 0
            thread_limit = 10
            threads_count = 0
            total_threads = []
            for row in rows:
                i += 1
                if i >= starter.settings.collector_working_interval_sec:
                    # response_threads.append(pool.apply_async(run_analysis, (row, predictor)))
                    """Проверка на количество работающих тредов и блокировка"""
                    while threads_count >= thread_limit:
                        threads_count = len(get_alive_threads(total_threads))

                    analysis_thread = threading.Thread(target=run_analysis, args=(row, predictor))
                    analysis_thread.setDaemon(True)
                    analysis_thread.start()

                    total_threads.append(analysis_thread)
                    threads_count += 1
                    # print "Run analysis thread. Total:", len(total_threads)
                    i = 0

            for th in total_threads:
                th.join()

            print("All threads closed")

    def get_alive_threads(threads):
        result_threads = []
        if len(threads) > 0:
            for thread in threads:
                if thread.isAlive():
                    result_threads.append(thread)
        return result_threads

    def checker_daemon(predictor):
        result = {
            "put_bids": 0,
            "call_bids": 0,
            "total_success": 0,
            "total_fails": 0,
            "no_trade": 0,
            "total_check": 0
        }
        while True:
            check_result = predictor.check_predictions(None)
            if check_result and len(check_result) > 0:
                for check in check_result:
                    result["total_check"] += 1
                    if check == "Put":
                        result["put_bids"] += 1
                        result["total_success"] += 1
                    if check == "Call":
                        result["call_bids"] += 1
                        result["total_success"] += 1
                    if check == "No":
                        result["no_trade"] += 1
                    if check == "Fail":
                        result["total_fails"] += 1
                print(result)
            time.sleep(1)

    def run_analysis(row, predictor):
        quotation = Quotation([row[0], row[4]])
        """Формируем кеши прошнозов для проверки"""
        predictor.do_analysis(quotation)
