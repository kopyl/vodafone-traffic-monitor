import json
import requests
from request_retrier import retry_request_till_success
import os
import base64


INTERNET_TRAFFIC_API_URL = "https://mw-api.vodafone.ua/prepaybalance/tmf-api/prepayBalanceManagement/v4/bucket"


def decode_base64_header_json(base64_string):
    return base64.decodebytes(bytes(base64_string, encoding='utf-8')).decode()


headers = os.getenv("HEADERS")
if "Authorization" not in headers:
    headers = headers.encode('raw_unicode_escape').decode('unicode_escape')
    headers = decode_base64_header_json(headers)
if headers:
    headers = json.loads(headers)
elif os.path.exists("headers.json"):
    with open('headers.json') as headers_file:
        headers = json.load(headers_file)
else:
    raise FileNotFoundError(
        "You need to set HEADERS as an env variable "
        "or if you're a developer – have 'headers.json' file"
    )


def get_total_available_gb_of_interner_traffic(response):
    buckets = response.json()
    not_available_bucket_types = [
        "REDRoamDPrP2000ROAMQ",
        "REDRoamDPrP1000ROAMQ",
        "VFSuperNetProPlusOver",  # just don't know how is it applied to my available traffic
        "SHAPING"  # it's the speed limitation, not the data size limiation
    ]
    available_buckets = [
        bucket for bucket in buckets
        if bucket['bucketType'] not in not_available_bucket_types
    ]
    available_gb_counts = [
        bucket['remainingValue']['amount'] for bucket in available_buckets
    ]
    total_gb_count = sum(available_gb_counts)
    return available_buckets, available_gb_counts, total_gb_count


def get_total_current_gb_count():
    response = retry_request_till_success(lambda: requests.get(INTERNET_TRAFFIC_API_URL, headers=headers))()
    total_gb_count = get_total_available_gb_of_interner_traffic(response)[-1]
    return total_gb_count