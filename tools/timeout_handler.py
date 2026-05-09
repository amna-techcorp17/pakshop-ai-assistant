import threading

class Result:
    def __init__(self):
        self.data = None
        self.error = None

def run_with_timeout(func, timeout=7):

    result = Result()

    def target():
        try:
            result.data = func()
        except Exception as e:
            result.error = str(e)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return {"timeout": True}

    if result.error:
        return {"error": result.error}

    return {"data": result.data}