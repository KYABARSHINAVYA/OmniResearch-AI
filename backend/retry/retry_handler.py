import time


def retry_function(
        func,
        *args,
        retries=3
):

    for i in range(retries):

        try:

            return func(*args)

        except Exception as e:

            print(
                f"Retry {i+1} failed:",
                e
            )

            time.sleep(2)

    return None