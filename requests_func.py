import requests
import json
import pandas as pd

_API_URL = "https://research-api.solarkim.com"
_API_KEY = "api키"  # https://o.solarkim.com/cmpt2023/result에서 확인할 수 있다.
_AUTH_PARAM = {"headers": {"Authorization": f"Bearer {_API_KEY}"}}


def _get(url: str):
    """
    주어진 url의 리소스를 조회한다.

    Args:
        url (str): API url
    """
    response = requests.get(url, **_AUTH_PARAM)
    return response.json()


def _post(url: str, data):
    """
    리소스 생성 데이터를 이용해서 주어진 url의 리소스를 생성한다.

    Args:
        url (str): API url
        data (dict): 리소스 생성용 데이터
    """
    response = requests.post(url, data=json.dumps(data), **_AUTH_PARAM)
    return response.json()


def _get_weathers_forecasts(date: str, time: int):
    """
    기상데이터 일단위 기상예측 데이터 조회 (https://research-api.solarkim.com/docs#tag/Competition-2023/operation/get_weathers_forecasts_date_bid_round_cmpt_2023_weathers_forecasts__date___bid_round__get 참고)
    """
    date = "2023-" + date
  
    if time==10:
        weather_fcst = _get(
            f"{_API_URL}/cmpt-2023/weathers-forecasts/{date}/1"
        )
    elif time==17:
        weather_fcst = _get(
            f"{_API_URL}/cmpt-2023/weathers-forecasts/{date}/2"
        )
    weather_fcst = pd.DataFrame(weather_fcst)
    weather_fcst['time'] = pd.to_datetime(weather_fcst['time'])
    return weather_fcst

def _get_gen_forecasts(date: str, time: int):
    """
    더쉐어 예측 모델의 예측 발전량 조회, 입찰대상일의 5가지 예측 모델의 예측 발전량 값을 취득한다 (https://research-api.solarkim.com/docs#tag/Competition-2023/operation/get_gen_forecasts_date_cmpt_2023_gen_forecasts__date___bid_round__get 참고)
    """
    date = "2023-" + date
  
    if time==10:
        gen_fcst = _get(
            f"{_API_URL}/cmpt-2023/gen-forecasts/{date}/1"
        )
    elif time==17:
        gen_fcst = _get(
            f"{_API_URL}/cmpt-2023/gen-forecasts/{date}/2"
        )
    gen_fcst = pd.DataFrame(gen_fcst)
    gen_fcst['time'] = pd.to_datetime(gen_fcst['time'])
    return gen_fcst



def _get_weathers_observeds(date):
    """
    기상데이터 일단위 기상관측데이터 조회, 당일에 대해 조회하면 현재시간 기준 24시간치 조회 (https://research-api.solarkim.com/docs#tag/Competition-2023/operation/get_weathers_observeds_date_cmpt_2023_weathers_observeds__date__get 참고)
    """
    date = "2023-" + date
    weather_obsv = _get(f"{_API_URL}/cmpt-2023/weathers-observeds/{date}")
    return weather_obsv


def _get_bids_result(date: str):
    """
    더쉐어 예측 모델의 예측 결과 조회 (https://research-api.solarkim.com/docs#tag/Competition-2023/operation/get_bids_result_date_cmpt_2023_bid_results__date__get 참고)
    """
    date = "2023-" + date

    bid_results = _get(f"{_API_URL}/cmpt-2023/bid-results/{date}")
    return bid_results


def _post_bids(amounts):
    """
    일단위 태양광 발전량 입찰. 시간별 24개의 발전량을 입찰하며 API가 호출된 시간에 따라 입찰 대상일이 결정된다. (https://research-api.solarkim.com/docs#tag/Competition-2023/operation/post_bids_cmpt_2023_bids_post 참고)
    """

    success = _post(f"{_API_URL}/cmpt-2023/bids", amounts)
    print(success)
