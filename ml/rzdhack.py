# -*- coding: utf-8 -*-
import json
import pickle
from typing import List, Dict

import implicit
import pandas as pd
from scipy.sparse import csr_matrix


def convert_duration_to_seconds(duration_str: str) -> int:
    parts = duration_str.split(':')
    hours, minutes, seconds = map(int, parts)
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds


def load_data(dataset_path: str) -> List[Dict]:
    with open(dataset_path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def create_stations_df(data: List[Dict]) -> pd.DataFrame:
    stations_data = [item['stations'] for item in data]
    combined_data = {}

    for item in stations_data:
        combined_data.update(item)

    stations_df = pd.DataFrame.from_dict(
        combined_data, orient='index',
        columns=[f'station_{i}' for i in range(1, 8)],
        dtype="float64"
    )
    stations_df.index.name = 'station_id'
    stations_df.reset_index(inplace=True)

    stations_df['station_number'] = stations_df['station_id'].apply(extract_station_number)
    stations_df.drop(columns=['station_id'], inplace=True)

    return stations_df


def extract_station_number(station_str: str) -> int:
    parts = station_str.split('(')
    if len(parts) == 2:
        number = parts[1].strip(')')
        return int(number)
    else:
        return -1  # Можно использовать None, если хотите


def create_full_timetable_df(data: List[Dict]) -> pd.DataFrame:
    full_timetable_data = [item['full_timetable'] for item in data]

    combined_schedule_data = {}
    for timetable in full_timetable_data:
        combined_schedule_data.update(timetable)

    full_timetable_df = pd.DataFrame.from_dict(combined_schedule_data, orient='index')
    full_timetable_df.index.name = 'train_id'
    full_timetable_df.reset_index(inplace=True)

    full_timetable_df = full_timetable_df.explode('timetable')

    full_timetable_df[['start_time', 'end_time']] = full_timetable_df['timetable'].str.split(' - ', expand=True)

    full_timetable_df.drop(columns=['timetable'], inplace=True)

    full_timetable_df['start_time'] = pd.to_datetime(full_timetable_df['start_time'], format='%H:%M')
    full_timetable_df['end_time'] = pd.to_datetime(full_timetable_df['end_time'], format='%H:%M')

    full_timetable_df['duration'] = full_timetable_df['end_time'] - full_timetable_df['start_time']
    full_timetable_df['duration'] = full_timetable_df['duration'].astype(str).str.split().str[-1]

    full_timetable_df.drop(columns=['start_time', 'end_time'], inplace=True)

    full_timetable_df['duration'] = full_timetable_df['duration'].apply(convert_duration_to_seconds)

    full_timetable_df['train_id'] = full_timetable_df['train_id'].astype('category')

    full_timetable_df['route'] = full_timetable_df['route'].apply(lambda x: x[0])
    full_timetable_df['free_carriage'] = full_timetable_df['free_carriage'].apply(lambda x: x[0])

    return full_timetable_df


def build_interaction_matrix(full_timetable_df: pd.DataFrame) -> csr_matrix:
    interaction_matrix = pd.pivot_table(
        full_timetable_df,
        values='duration',
        index='train_id',
        columns='route',
        aggfunc='sum',
        fill_value=0
    )

    sparse_interaction_matrix = csr_matrix(interaction_matrix.values)

    return sparse_interaction_matrix


def train_recommendation_model(sparse_interaction_matrix: csr_matrix) -> None:
    model = implicit.als.AlternatingLeastSquares(factors=200, regularization=0.01, iterations=50)
    model.fit(sparse_interaction_matrix)

    with open("../backend/model_weights.pkl", "wb") as f:
        pickle.dump(model, f)


def load_recommendation_model() -> implicit.als.AlternatingLeastSquares:
    with open("../backend/model_weights.pkl", "rb") as f:
        loaded_model = pickle.load(f)

    return loaded_model


def recommend_stations(
        user_id: int,
        user_items: csr_matrix,
        loaded_model: implicit.als.AlternatingLeastSquares
) -> List[int]:
    recommended_stations, _ = loaded_model.recommend(user_id, user_items)
    return recommended_stations


if __name__ == "__main__":
    dataset_path = "/Users/dromanov/PycharmProjects/RZHD_HACK/ml/dataset.json"

    data = load_data(dataset_path)
    stations_df = create_stations_df(data)
    full_timetable_df = create_full_timetable_df(data)
    sparse_interaction_matrix = build_interaction_matrix(full_timetable_df)

    train_recommendation_model(sparse_interaction_matrix)

    loaded_model = load_recommendation_model()
    user_items = csr_matrix(sparse_interaction_matrix[853])
    recommended_stations = recommend_stations(0, user_items, loaded_model)
