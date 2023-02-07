<html><p><a href="https://loko-ai.com/" target="_blank" rel="noopener"> <img style="vertical-align: middle;" src="https://user-images.githubusercontent.com/30443495/196493267-c328669c-10af-4670-bbfa-e3029e7fb874.png" width="8%" align="left" /> </a></p>
<h1>Loko Sagemaker Demo</h1><br></html>

A simple example of training/predicting a classification model through the use of the AWS **Sagemaker** service. The use of the Loko Sagemaker extension will enable simple and intuitive integration.

<p align="center"><img src="https://user-images.githubusercontent.com/44770119/217236104-edf15ca6-229a-4924-accc-77620c52a55e.PNG" width="80%" /></p>

**CONFIGURATION**

In order to connect to AWS Sagemaker APIs we need to setup the configuration file "config.json" with an account information as following:

```
{
  "main": {
    "environment": {
        "AWS_ACCESS_KEY_ID": "<insert your key here>",
        "AWS_SECRET_ACCESS_KEY": "<insert your key here>",
        "ROLE": "<insert your key here>",
        "BUCKET": "<insert your key here>",
        "REGION_NAME": "<insert your key here>"
    }
  }
}
```

**TRAIN**

First we choose the reference dataset, which in this case will be iris dataset, very common in Data Science:

<p align="center"><img src="https://user-images.githubusercontent.com/44770119/217234574-2c591a88-77f1-4365-9f18-07a01435a94c.PNG" width="80%" /></p>

In the second step we do a little preprocessing to indicate the target variable to the component that will be in charge of training the Sagemaker model. Next we create batches with the Grouper block.

<p align="center"><img src="https://user-images.githubusercontent.com/44770119/217235225-0ed414c5-83d0-4eab-a770-e8e99a0c405c.PNG" width="80%" /></p>

Finally we use the Loko Sagemaker extension to invoke the AWS Sagemaker Rest API for initializing and training the Machine Learning model.

<p align="center"><img src="https://user-images.githubusercontent.com/44770119/217235440-3a6ec5ff-2d7a-4e51-944f-e46739836ccb.PNG" width="80%" /></p>


**PREDICT**

As for prediction, we select the dataset to be predicted; if the target viariable is present we exclude it via a Selector block and in the end we submit the data to do prediction to the Loko Sagemaker block with the following configuration:

<p align="center"><img src="https://user-images.githubusercontent.com/44770119/217236908-e4ba1a47-0af4-4266-b189-5ea7073972ef.PNG" width="80%" /></p>

<p align="center"><img src="https://user-images.githubusercontent.com/44770119/217236989-6cdfcfcc-4efd-4b36-aadd-a64006a16e45.PNG" width="80%" /></p>

**DELETE**

Once the Sagemaker API operations are finished, if there is no need to keep the objects created in the cloud, they can be deleted via the delete service in the following procedure:

<p align="center"><img src="https://user-images.githubusercontent.com/44770119/217237439-1d9ac6b6-0e4e-422c-a596-60968d77c299.PNG" width="80%" /></p>

