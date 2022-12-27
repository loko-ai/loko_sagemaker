sagemaker_doc = '''### Description
The Sagemaker component allows to interact with the AWS APIs in order to train machine learning algorithms. 
Once a model has been trained you can deploy the algorithm and start to make predictions of new data streams. 
Models and datasets will be loaded and stored on a configured S3 bucket in the training phase. 
You can also make inference with already trained models on Sagemaker.
### Configuration
Sagemaker configurations are set in the *config.json* file. 
### Input
**FIT** input accepts a train and an evaluate dataset or only the train one.
In the first case you have to provide a dictionary containing the keys *train_data* and *validation_data*.

Example:
```json
{"train_data": [
        {"target":0,"sepal length":5.1,"sepal width":3.5,"petal length":1.4,"petal width":0.2},
        {"target":0,"sepal length":4.9,"sepal width":3,"petal length":1.4,"petal width":0.2},
        {"target":0,"sepal length":4.7,"sepal width":3.2,"petal length":1.3,"petal width":0.2}
        ],
 "validation_data": [
        {"target":2,"sepal length":6.5,"sepal width":3,"petal length":5.2,"petal width":2},
        {"target":2,"sepal length":6.2,"sepal width":3.4,"petal length":5.4,"petal width":2.3},
        {"target":2,"sepal length":5.9,"sepal width":3,"petal length":5.1,"petal width":1.8}
        ]}
```
Otherwise, you can directly pass your training dataset.

Example:
```json
    [
        {"target":0,"sepal length":5.1,"sepal width":3.5,"petal length":1.4,"petal width":0.2},
        {"target":0,"sepal length":4.9,"sepal width":3,"petal length":1.4,"petal width":0.2},
        {"target":0,"sepal length":4.7,"sepal width":3.2,"petal length":1.3,"petal width":0.2}
    ]
```
The first column of the dataset is used as the model target. 

You have to preprocess your data first.

**PREDICT** input accepts a dataset without target column.

Example:
```json
    [
        {"sepal length":5.1,"sepal width":3.5,"petal length":1.4,"petal width":0.2},
        {"sepal length":4.9,"sepal width":3,"petal length":1.4,"petal width":0.2},
        {"sepal length":4.7,"sepal width":3.2,"petal length":1.3,"petal width":0.2}
    ]
```
'''
