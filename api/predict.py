from fastapi import APIRouter
from pyexpat import features
import joblib
from db.schema import HousePredictSchema


scaler = joblib.load('scaler.pkl')
model = joblib.load('model.pkl')

predict_router = APIRouter(prefix='/predict', tags=['Predict Price'])

nei = ['Blueste', 'BrDale', 'BrkSide', 'ClearCr', 'CollgCr', 'Crawfor', 'Edwards', 'Gilbert', 'IDOTRR', 'MeadowV',
       'Mitchel', 'NAmes', 'NPkVill', 'NWAmes', 'NoRidge', 'NridgHt', 'OldTown', 'SWISU', 'Sawyer', 'SawyerW',
       'Somerst', 'StoneBr', 'Timber', 'Veenker']

@predict_router.post('/')
async def predict_price(house: HousePredictSchema):
    house_dict = dict(house)

    new_neighborhood = house_dict.pop('Neighborhood')
    neighborhood1_0 = [
        1 if new_neighborhood == i else 0 for i in nei
    ]

    features = list(house_dict.values()) + neighborhood1_0
    scaled_data = scaler.transform([features])
    predict = model.predict(scaled_data)[0]
    return {'Price': round(predict, 2)}
