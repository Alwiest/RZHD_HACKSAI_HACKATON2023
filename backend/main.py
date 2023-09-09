import pickle

from fastapi import FastAPI
from pydantic import BaseModel
from scipy.sparse import load_npz, csr_matrix

from middleware import logging_middleware

app = FastAPI()

app.middleware("http")(logging_middleware)


class TrainIDInput(BaseModel):
    train_id: int


def get_recommendations_for_train(train_id: int):
    sparse_interaction_matrix = load_npz(r"sparse_interaction_matrix.npz")
    with open("/Users/dromanov/PycharmProjects/RZHD_HACK/ml/model_weights.pkl", "rb") as f:
        loaded_model = pickle.load(f)

    user_items = csr_matrix(sparse_interaction_matrix[train_id])

    recommended_stations, _ = loaded_model.recommend(0, user_items)

    return recommended_stations


@app.post("/get_recommendations/")
async def get_recommendations(train_id_input: TrainIDInput):
    train_id = train_id_input.train_id

    recommendations = get_recommendations_for_train(train_id)
    recommendations_list = recommendations.tolist()
    message = f"Для поезда {train_id} подходит следующий маршрут"
    return {
        "message": f"{message}",
        "recommended_stations": recommendations_list
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
