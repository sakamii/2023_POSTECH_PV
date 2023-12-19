import pandas as pd
import numpy as np
import joblib
import requests_func
import process_func
from tqdm import tqdm

def calc_profit(actual_gens: list[float], forecast_gens: list[float]):
    CAPACITY = 99.0
    facility_utilization_rate = [actual / CAPACITY for actual in actual_gens]

    filter_facility_utilization_rate = [
        utilization >= 0.1 for utilization in facility_utilization_rate
    ]

    errors = [
        abs(forecast - actual) / CAPACITY * 100
        for forecast, actual in zip(forecast_gens, actual_gens)
    ]

    target_errors = [
        error
        for error, is_filtered in zip(errors, filter_facility_utilization_rate)
        if is_filtered
    ]
    target_actual_gens = [
        actual
        for actual, is_filtered in zip(
            actual_gens, filter_facility_utilization_rate
        )
        if is_filtered
    ]

    profits = [0] * len(target_actual_gens)

    for i, error in enumerate(target_errors):
        if error <= 6:
            profits[i] = 1 * 4
        elif 6 < error <= 8:
            profits[i] = 1 * 3

    return profits


def get_incentive(model, start_date, end_date=None):
    incentives = []
    year = "2023-"

    amount_func = predict_amount

    if end_date==None:
        dates = [year+start_date]
    else:
        dates = pd.date_range(year+start_date, year+end_date)

    for date in tqdm(dates):
        forecast_gens = amount_func(model, str(date.month)+'-'+str(date.day))
    
        amounts = pd.read_csv("실측발전량1030이후.csv").iloc[:264]
        amounts.time = pd.to_datetime(amounts.time)
    
        actual_gens = amounts[amounts.time.dt.month == date.month][amounts.time.dt.day == date.day].amount.to_list()
        incentive = sum(calc_profit(actual_gens, forecast_gens))
        
        incentives.append(incentive)
    
    return sum(incentives)


def predict_amount(model, date, time=None):
    models_map = {
        'model1':process_func.model1_processing,
        'model2':process_func.model2_processing, 
        'final':process_func.fin_processing}
    process = models_map[model]
    
    amounts = []
    if time==None:
        time = [10,17]
    else:
        time = [time]
    for t in time:
        weather = requests_func._get_weathers_forecasts(date, t)
        gen = requests_func._get_gen_forecasts(date, t)
        
        df = process(weather, gen)
        loaded_model = joblib.load(model+'.pkl')
        cols_when_model_builds = loaded_model.feature_names_in_ # randomforest 모델의 경우
        # cols_when_model_builds = loaded_model.get_booster().feature_names # xgb 모델의 경우
        result = loaded_model.predict(df[cols_when_model_builds])
    
        amounts.append(result)
    pred = np.array(amounts).mean(axis=0)
        
    return list(pred)