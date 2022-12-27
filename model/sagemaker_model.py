from io import BytesIO
from pprint import pprint

import boto3
import pandas as pd
import sagemaker
from sagemaker import Session, TrainingInput
from sagemaker.predictor import RealTimePredictor, csv_serializer, csv_deserializer
from sagemaker.serializers import CSVSerializer
from utils.logger_utils import stream_logger
from utils.ws_utils import logs_for_job

logger = stream_logger(__name__)


class SagemakerPredictor:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, role, bucket, model_name, algorithm,
                 ws=None):
        self.boto_session = boto3.session.Session(aws_access_key_id=aws_access_key_id,
                                                  aws_secret_access_key=aws_secret_access_key,
                                                  region_name=region_name)
        self.sagemaker_session = Session(boto_session=self.boto_session)
        self.s3 = self.boto_session.client("s3")
        self.role = role
        self.bucket = bucket
        self.container = self._get_image_uri(algorithm) if algorithm else None
        self.model_name = model_name
        self._predictor = None
        self.instance_type = None
        self.ws = ws

    def _get_image_uri(self, algorithm):
        model, version = algorithm.split(':')
        container = sagemaker.image_uris.retrieve(model, self.sagemaker_session.boto_region_name, version)
        return container

    def fit(self, train_data, validation_data=None, instance_type=None, hp=None):

        self.ws.emit(self.model_name, 'Saving train dataset on S3')
        self._save_dataset(train_data, 'train/train.csv')
        s3_input_train = TrainingInput(s3_data=f"s3://{self.bucket}/{self.model_name}/train", content_type="csv")
        if validation_data:
            self.ws.emit(self.model_name, 'Saving train dataset on S3')
            self._save_dataset(validation_data, 'validation/validation.csv')
            s3_input_validation = TrainingInput(s3_data=f"s3://{self.bucket}/{self.model_name}/validation/",
                                                content_type="csv")
        self.ws.emit(self.model_name, 'Init model')
        model = sagemaker.estimator.Estimator(self.container,
                                                   self.role,
                                                   instance_count=1,
                                                   instance_type=instance_type,
                                                   output_path=f"s3://{self.bucket}/{self.model_name}",
                                                   sagemaker_session=self.sagemaker_session)
        if hp:
            if hp.get('objective', '')=='multi:softmax':
                if not 'num_class' in hp:
                    data = pd.DataFrame(train_data)
                    hp['num_class'] = len(data[data.columns[-1]].unique())
            model.set_hyperparameters(**hp)
        data = dict(train=s3_input_train)
        if validation_data:
            data['validation'] = s3_input_validation
        # self.ws.emit(self.model_name, 'Start fitting')
        model.fit(data, wait=False)
        job_name = model.latest_training_job.name
        logs_for_job(job_name, model.sagemaker_session, wait=True, poll=3, log_type="All", ws=self.ws,
                     model_name=self.model_name)
        # self.ws.emit(self.model_name, 'End fitting')

    def _get_last_model(self):
        path = f'{self.model_name}'
        content = self.s3.list_objects(Bucket=self.bucket, Prefix=path)
        models = sorted([p['Key'] for p in content['Contents'] if p['Key'].endswith('.tar.gz')])
        return f's3://{self.bucket}/{models[-1]}'

    def get_models(self):
        content = self.s3.list_objects(Bucket=self.bucket)
        if not 'Contents' in content:
            return []
        models = [p['Key'] for p in content['Contents'] if p['Key'].endswith('.tar.gz')]
        models = sorted(set(['/'.join(model.split('/')[:-3]).strip('/') for model in models]))
        return models

    def _save_dataset(self, dataset, fname):
        buff = BytesIO()
        pd.DataFrame(dataset).to_csv(buff, header=False, index=False)
        buff.seek(0)
        self.s3.upload_fileobj(buff, self.bucket, f'{self.model_name}/{fname}')


    @property
    def predictor(self):
        if not self._predictor:
            logger.debug('GET MODEL')
            class Predictor(RealTimePredictor):
                def __init__(self, endpoint_name, sagemaker_session=None):
                    super(Predictor, self).__init__(endpoint_name, sagemaker_session, csv_serializer, csv_deserializer)

            model_data = self._get_last_model()

            logger.debug(model_data)
            self.ws.emit(self.model_name, 'Init model')
            model = sagemaker.model.Model(model_data=model_data,
                                          image_uri=self.container,
                                          role=self.role,
                                          sagemaker_session=self.sagemaker_session,
                                          predictor_cls=Predictor)
            self.ws.emit(self.model_name, 'Start deploy')
            self._predictor = model.deploy(initial_instance_count=1, instance_type=self.instance_type,
                                          serializer=CSVSerializer())
            self.ws.emit(self.model_name, ' ')
        return self._predictor

    def predict(self, test_data, instance_type="ml.m5.large"):
        logger.debug('START PREDICTION')
        self.instance_type = instance_type
        test_data = pd.DataFrame(test_data)
        return self.predictor.predict(test_data.values)

    def delete_endpoint(self, delete_endpoint_config=True):
        if self._predictor:
            self.predictor.delete_endpoint(delete_endpoint_config=delete_endpoint_config)
        logger.debug('ENDPOINT DELETED')

    def delete_model(self):
        if self._predictor:
            self.predictor.delete_model()
        logger.debug('MODEL DELETED')



if __name__ == '__main__':
    from config.app_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME, ROLE, BUCKET

    sm = SagemakerPredictor(aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                            region_name=REGION_NAME,
                            role=ROLE,
                            bucket=BUCKET,
                            model_name='',
                            algorithm=None)

    # pprint(sm.get_models())
    # print(sm._get_last_model())
    pprint(sm.sagemaker_session.sagemaker_client.list_models())

    # df = pd.read_csv('../resources/datasets_test/iris_test.csv').to_dict(orient='records')
    # print(df)
    #
    # sm._save_dataset(df, 'iris/iris_test.csv')
