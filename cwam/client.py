import boto3


class Client:

    def __init__(self, aws_access_key_id, aws_access_secret_key,
                 aws_default_region, debug=None):
        self.aws_access_key_id = aws_access_key_id
        self.aws_access_secret_key = aws_access_secret_key
        self.aws_default_region = aws_default_region
        self.debug = debug
        self.session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_access_secret_key,
                                     region_name=aws_default_region)
