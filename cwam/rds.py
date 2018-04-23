from .cloudwatch import CloudWatch


class RDSInstance:
    def __init__(self, client, info):
        self.client = client
        self.arn = info.get('DBInstanceArn')
        self.name = info.get('DBInstanceIdentifier')

    def __str__(self):
        return '(RDSInstance) Name: %s' % self.name

    def default_dimension_name(self):
        return 'DBInstanceIdentifier'

    def default_dimension_value(self):
        return self.name

    def default_dimensions(self):
        return [dict(Name=self.default_dimension_name(),
                     Value=self.default_dimension_value())]

    def dict(self):
        return {'DBInstanceArn': self.arn,
                'DBInstanceIdentifier': self.name}


class RDS(CloudWatch, object):

    DEFAULT_NAMESPACE = 'AWS/RDS'
    ALARM_NAME_PREFIX = 'RDS'

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        super(RDS, self).__init__(aws_access_key_id=aws_access_key_id,
                                  aws_access_secret_key=aws_access_secret_key,
                                  aws_session_token=aws_session_token,
                                  aws_default_region=aws_default_region,
                                  debug=debug)
        self.client = self.session.client('rds')

    def _describe_db_instances(self):
        response = self.client.describe_db_instances()
        return [RDSInstance(self.client, i) for i in response['DBInstances']]

    def list(self):
        return self._describe_db_instances()

    def remote_alarms(self, namespace=DEFAULT_NAMESPACE,
                      prefix=ALARM_NAME_PREFIX):
        namespace = namespace or RDS.DEFAULT_NAMESPACE
        prefix = prefix or RDS.ALARM_NAME_PREFIX
        return super(RDS, self).remote_alarms(namespace=namespace,
                                              prefix=prefix)

    def create(self, objects, namespace=DEFAULT_NAMESPACE,
               prefix=ALARM_NAME_PREFIX, default=None, only=None,
               exclude=None, sns={}, simulate=False):
        if exclude is not None and only is not None:
            raise "Exlude and Only option are mutually exclusive."

        instances = self._describe_db_instances()
        super(RDS, self).create(instances=instances,
                                objects=objects,
                                namespace=namespace,
                                prefix=prefix,
                                default=default,
                                only=only,
                                exclude=exclude,
                                sns=sns,
                                simulate=simulate)
