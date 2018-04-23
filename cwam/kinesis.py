from .cloudwatch import CloudWatch


class KinesisInstance:
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def __str__(self):
        return '(KinesisInstance) Name: %s' % self.name

    def default_dimension_name(self):
        return 'StreamName'

    def default_dimension_value(self):
        return self.name

    def default_dimensions(self):
        return [dict(Name=self.default_dimension_name(),
                     Value=self.default_dimension_value())]

    def dict(self):
        return {'StreamName': self.name}


class Kinesis(CloudWatch, object):

    DEFAULT_NAMESPACE = 'AWS/Kinesis'
    ALARM_NAME_PREFIX = 'Kinesis'

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        super(Kinesis, self).__init__(aws_access_key_id=aws_access_key_id,
                                      aws_access_secret_key=aws_access_secret_key,  # noqa E501
                                      aws_session_token=aws_session_token,
                                      aws_default_region=aws_default_region,
                                      debug=debug)
        self.client = self.session.client('kinesis')

    def _list_streams(self):
        response = self.client.list_streams(Limit=1000)
        return [KinesisInstance(self.client, name) for name in response['StreamNames']]  # noqa E501

    def list(self):
        return self._list_streams()

    def remote_alarms(self, namespace=DEFAULT_NAMESPACE,
                      prefix=ALARM_NAME_PREFIX):
        namespace = namespace or Kinesis.DEFAULT_NAMESPACE
        prefix = prefix or Kinesis.ALARM_NAME_PREFIX
        return super(Kinesis, self).remote_alarms(namespace=namespace,
                                                  prefix=prefix)

    def create(self, objects, namespace=DEFAULT_NAMESPACE,
               prefix=ALARM_NAME_PREFIX, default=None, only=None,
               exclude=None, sns={}, simulate=False):

        instances = self._list_streams()
        super(Kinesis, self).create(instances=instances,
                                    objects=objects,
                                    namespace=namespace,
                                    prefix=prefix,
                                    default=default,
                                    only=only,
                                    exclude=exclude,
                                    sns=sns,
                                    simulate=simulate)
