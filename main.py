from typing import Union
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import joblib
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
df_raw = pd.read_csv("classes_prod.csv")
df = pd.read_csv("classesNum_prod.csv")
loaded_model = joblib.load("nearest_neighbors_model_v5.pkl")

def recommend_class(class_id, df, model):
    indexByClassId = df_raw[df_raw["classId"] == int(class_id)].index[0]

    user_classes = df.iloc[[indexByClassId]]
    neighbors = model.kneighbors(user_classes.iloc[0, :].values.reshape(1, -1))

    distances = neighbors[0][0]
    index_recommends = neighbors[1][0]

    recommend_class_list = []

    for (index,val) in enumerate(index_recommends.tolist()):
        distance = distances[index]
        data = df_raw.iloc[[val]]
        
        classId = data["classId"].values[0]
        nameTh = data["nameTh"].values[0]
        nameEn = data["nameEn"].values[0]
        # hours = data["hours"].values[0]

        recommend_class_list.append({
            "classId": classId,
            "nameTh": nameTh,
            "nameEn": nameEn,
            # "hours": hours,
            "distance": distance
        })

    return recommend_class_list


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

@app.get("/{classId}")
def read_root(classId: str):
    recommended_classes = recommend_class(classId, df, loaded_model)
    return JSONResponse(content=json.loads(json.dumps(recommended_classes, cls=NpEncoder)))


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}