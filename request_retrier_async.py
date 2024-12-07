import os
import sys
import time
import requests
import asyncio


p = print


class CurrentDatetime:

    date = time.strftime('%d %b %Y')
    time = time.strftime('%H:%M:%S')

    def __str__(self):
        return f"{self.date} {self.time}"


def get_caught_error(additional_message=""):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    message = (
        f"Now {CurrentDatetime()}\n"
        f"\"{fname}\" caught an error "
        f"{exc_type.__name__} "
        f"on line {exc_tb.tb_lineno}:\n"
        f"\"{exc_obj}\""
        f"\n\n{additional_message}"
    )
    return message


def define_retry_delay_seconds(
    retry_time_count: int
) -> int:

    retry_in_seconds = 1 * retry_time_count
    if retry_in_seconds > 1800:
        retry_in_seconds = 1800
    return retry_in_seconds


def retry_request_till_success(
    request: requests.models.Request
) -> requests.models.Response:

    async def wrapper(*args, **kwargs):
        retry_time_count = 1
        while True:
            retry_in_seconds = define_retry_delay_seconds(retry_time_count)
            try:
                response = await request(*args, **kwargs)
                if response == None:  # doc.id#13
                    p("There is no request to retry")
                    return

                if response.status_code in [200, 404]:
                    return response
                else:
                    p(
                        f"URL: {response.url} "
                        f"Request in {request.__name__} failed. "
                        f"Status_code – {response.status_code} "
                        f"Will retry again in {retry_in_seconds} seconds"
                    )
                    await asyncio.sleep(retry_in_seconds)
                    retry_time_count += 1

            except (
                requests.ConnectTimeout,
                requests.exceptions.ReadTimeout
            ) as e:
                error = get_caught_error()
                p(
                    f"Request in {request.__name__} failed. "
                    f"Timed out with error {error}"
                    f"Will retry again in {retry_in_seconds} seconds"
                )
                await asyncio.sleep(retry_in_seconds)
                retry_time_count += 1
            except requests.exceptions.ConnectionError as e:
                sleep_time = 10
                p(
                    f"Request in {request.__name__} failed @"
                    f"{CurrentDatetime()}. "
                    "No connection to internet... "
                    f"Will retry again in {sleep_time} seconds"
                )
                await asyncio.sleep(sleep_time)
    return wrapper