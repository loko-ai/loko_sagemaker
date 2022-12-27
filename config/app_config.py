import os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
ROLE = os.environ.get('ROLE')
BUCKET = os.environ.get('BUCKET')
REGION_NAME = os.environ.get('REGION_NAME')

GATEWAY = os.environ.get('GATEWAY', 'http://localhost:9999/')

SM_INSTANCES = ['ml.trn1.32xlarge', 'ml.p2.xlarge', 'ml.m5.4xlarge', 'ml.m4.16xlarge', 'ml.p4d.24xlarge',
                'ml.g5.2xlarge', 'ml.c5n.xlarge', 'ml.p3.16xlarge', 'ml.m5.large', 'ml.p2.16xlarge', 'ml.g5.4xlarge',
                'ml.c4.2xlarge', 'ml.c5.2xlarge', 'ml.c4.4xlarge', 'ml.g5.8xlarge', 'ml.c5.4xlarge', 'ml.c5n.18xlarge',
                'ml.g4dn.xlarge', 'ml.g4dn.12xlarge', 'ml.c4.8xlarge', 'ml.g4dn.2xlarge', 'ml.c5.9xlarge',
                'ml.g4dn.4xlarge', 'ml.c5.xlarge', 'ml.g4dn.16xlarge', 'ml.c4.xlarge', 'ml.g4dn.8xlarge',
                'ml.g5.xlarge', 'ml.c5n.2xlarge', 'ml.g5.12xlarge', 'ml.g5.24xlarge', 'ml.c5n.4xlarge',
                'ml.trn1.2xlarge', 'ml.c5.18xlarge', 'ml.p3dn.24xlarge', 'ml.g5.48xlarge', 'ml.g5.16xlarge',
                'ml.p3.2xlarge', 'ml.m5.xlarge', 'ml.m4.10xlarge', 'ml.c5n.9xlarge', 'ml.m5.12xlarge', 'ml.m4.xlarge',
                'ml.m5.24xlarge', 'ml.m4.2xlarge', 'ml.p2.8xlarge', 'ml.m5.2xlarge', 'ml.p4de.24xlarge',
                'ml.p3.8xlarge', 'ml.m4.4xlarge']