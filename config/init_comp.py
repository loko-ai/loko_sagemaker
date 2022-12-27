import json

from loko_extensions.model.components import Component, Input, Output, Arg, save_extensions, AsyncSelect, Dynamic, \
    Events

from doc.sagemaker_doc import sagemaker_doc

### args

algorithm = AsyncSelect('algorithm', url='http://localhost:9999/routes/loko_sagemaker/algorithms', label='Algorithm',
                        required=True, value='xgboost:1.5-1', description='Algorithm type and version',
                        helper='Insert algorithm sagemaker image')

oalgorithm = Dynamic('oalgorithm', label='Other Algorithm', required=True, parent='algorithm',
                     condition="{parent}==='other'")

args = [algorithm, oalgorithm]

fit_group = 'Fit'

model_name_fit = Arg('model_name_fit', label='Model Name',
                     value='sagemaker/DEMO-xgboost',
                     helper='Insert model name', group=fit_group)

instance_type_fit = AsyncSelect('instance_type_fit', label='Instance Type',
                                url='http://localhost:9999/routes/loko_sagemaker/instances',
                                description='The EC2 instance type to deploy this Model to. For example, ‘ml.p2.xlarge’, or ‘local’ for local mode. If not using serverless inference, then it is required to deploy a model.',
                                value='ml.m5.large', group=fit_group)
hp_value = json.dumps(dict(max_depth=5, eta=0.2, gamma=4, min_child_weight=6, subsample=0.8, verbosity=0,
                           objective="multi:softmax", num_round=100))

hp = Arg('hp', label='Hyper-Parameters', type='code', value=hp_value, group=fit_group,
         description='Json format hyperparameters configuration based on the algorithm type.')

predict_group = 'Predict'

model_name_predict = AsyncSelect('model_name_predict', label='Model Name',
                         url='http://localhost:9999/routes/loko_sagemaker/models',
                         helper='Insert model name', group=predict_group)

instance_type_predict = AsyncSelect('instance_type_predict', label='Instance Type',
                                    url='http://localhost:9999/routes/loko_sagemaker/instances',
                                    description='The EC2 instance type to deploy this Model to. For example, ‘ml.p2.xlarge’, or ‘local’ for local mode. If not using serverless inference, then it is required to deploy a model.',
                                    value='ml.m5.large', group=predict_group)

delete_endpoint = Arg('delete_endpoint', 'boolean', 'Delete Endpoint', value=True, group='Delete')
delete_endpoint_config = Arg('delete_endpoint_config', 'boolean', 'Delete Endpoint Config', value=True, group='Delete')
delete_model = Arg('delete_model', 'boolean', 'Delete Model', value=True, group='Delete')

args += [model_name_fit, instance_type_fit, model_name_predict, instance_type_predict, hp, delete_endpoint,
         delete_endpoint_config, delete_model]

### inputs/outputs

fit_input = Input('fit', service='fit', to='fit')
predict_input = Input('predict', service='predict', to='predict')
delete_input = Input('delete', service='delete', to='delete')

fit_output = Output('fit')
predict_output = Output('predict')
delete_output = Output('delete')

sagemaker = Component('Sagemaker',
                      description=sagemaker_doc,
                      args=args,
                      inputs=[fit_input, predict_input, delete_input],
                      outputs=[fit_output, predict_output, delete_output],
                      configured=False,
                      icon='RiTyphoonFill',
                      events=Events(type="sagemaker", field="model_name_fit"))

save_extensions([sagemaker])
