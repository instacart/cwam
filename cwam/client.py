import boto3


class Client:

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        self.aws_access_key_id = aws_access_key_id
        self.aws_access_secret_key = aws_access_secret_key
        self.aws_session_token = aws_session_token
        self.aws_default_region = aws_default_region
        self.debug = debug
        self.session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_access_secret_key,  # noqa E501
                                     aws_session_token=aws_session_token,
                                     region_name=aws_default_region)
