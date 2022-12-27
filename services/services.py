import json
import sys
import traceback
from pathlib import Path

import sanic
from loko_extensions.business.decorators import extract_value_args

from business.ws_client import WSClient
from config.app_config import SM_INSTANCES
from model.configs import Configs
from model.sagemaker_model import SagemakerPredictor
from sanic import Sanic, Blueprint
from sanic.exceptions import NotFound, SanicException
from sanic_openapi import swagger_blueprint

from utils.logger_utils import stream_logger

logger = stream_logger(__name__)

SERVICES_PORT = 8080


in_memory_models = {}
wsclient = WSClient(type='sagemaker')

def get_app(name):
    app = Sanic(name)
    swagger_blueprint.url_prefix = "/api"
    app.blueprint(swagger_blueprint)
    return app


name = "sagemaker"
app = get_app(name)
bp = Blueprint("default", url_prefix="")
app.config.API_DESCRIPTION = "Sagemaker Swagger"
app.config["API_TITLE"] = name
app.config["REQUEST_MAX_SIZE"] = 20000000000
app.config["REQUEST_TIMEOUT"] = 172800


@app.exception(Exception)
async def manage_exception(request, exception):
    if isinstance(exception, SanicException):
        return sanic.json(dict(error=str(exception)), status=exception.status_code)

    e = dict(error=f'{exception.__class__.__name__}: {exception}')
    if isinstance(exception, NotFound):
        return sanic.json(e, status=404)

    logger.error('TracebackERROR: \n' + traceback.format_exc() + '\n\n', exc_info=True)

    if type(exception) == Exception:
        return sanic.json(dict(error=str(exception)), status=500)

    return sanic.json(e, status=500)

@bp.get('/algorithms')
async def algorithms(request):
    venv_path = sys.prefix
    images_path = Path(venv_path)/'lib/python3.10/site-packages/sagemaker/image_uri_config'
    images = images_path.glob('*')
    algo = sorted([(el.name).replace('.json', '')+':*' if el.name!='xgboost.json' else 'xgboost:1.5-1' for el in images])
    return sanic.json(algo)
@bp.get('/instances')
async def instances(request):
    return sanic.json(sorted(SM_INSTANCES))

@bp.get('/models')
async def models(request):
    configs = Configs().__dict__
    predictor = get_sagemaker_model(configs)
    return sanic.json(predictor.get_models())

def get_sagemaker_model(configs):
    ks = tuple(configs.values())
    if not ks in in_memory_models:
        in_memory_models[ks] = SagemakerPredictor(**configs, ws=wsclient)
    return in_memory_models[ks]

@bp.post('/fit')
@extract_value_args()
async def fit(value, args):
    args['model_name'] = args['model_name_fit']
    if not args['model_name']:
        raise SanicException('no model name specified', status_code=400)
    configs = Configs(**args).__dict__
    predictor = get_sagemaker_model(configs)
    instance_type = args.get('instance_type_fit')
    hp = json.loads(args.get('hp', '{}'))
    if 'train_data' in value:
        train_data = value.get('train_data')
        validation_data = value.get('validation_data')
    else:
        train_data = value
        validation_data = None
    predictor.fit(train_data=train_data, validation_data=validation_data, instance_type=instance_type, hp=hp)
    return sanic.json('fitted')


@bp.post('/predict')
@extract_value_args()
async def predict(value, args):
    args['model_name'] = args['model_name_predict']
    if not args['model_name']:
        raise SanicException('no model name specified', status_code=400)
    configs = Configs(**args).__dict__
    predictor = get_sagemaker_model(configs)
    instance_type = args.get('instance_type_predict')
    preds = predictor.predict(value, instance_type)
    return sanic.json(preds)

@bp.post('delete')
@extract_value_args()
async def delete(value, args):
    configs = Configs(**args).__dict__
    predictor = get_sagemaker_model(configs)
    delete_endpoint = args.get('delete_endpoint')
    delete_endpoint_config = args.get('delete_endpoint_config')
    delete_model = args.get('delete_model')

    if delete_model:
        predictor.delete_model()
    if delete_endpoint:
        predictor.delete_endpoint(delete_endpoint_config=delete_endpoint_config)
    return sanic.json('OK')



app.blueprint(bp)

app.run("0.0.0.0", port=8080, auto_reload=True)