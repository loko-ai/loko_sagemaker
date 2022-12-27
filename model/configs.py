from config.app_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME, ROLE, BUCKET


class Configs:
    def __init__(self, model_name=None, algorithm=None, oalgorithm=None, **kwargs):
        self.aws_access_key_id = AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        self.region_name = REGION_NAME
        self.role = ROLE
        self.bucket = BUCKET
        self.model_name = model_name
        self.algorithm = algorithm if algorithm!='other' else oalgorithm