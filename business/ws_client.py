from loko_client.utils.requests_utils import URLRequest

from config.app_config import GATEWAY


class WSClient:

    def __init__(self, type: str, gateway=GATEWAY):
        self.type = type
        self.u = URLRequest(gateway)

    def emit(self, name: str, msg: str):
        data = dict(event_name='event_ds4biz',
                    content=dict(msg=msg,
                                 type=self.type,
                                 name=name))
        r = self.u.emit.post(json=data)
        return r.text

if __name__ == '__main__':
    wsclient = WSClient(type='sagemaker')
    print(wsclient.emit('sagemaker/DEMO-xgboost', 'hello'))