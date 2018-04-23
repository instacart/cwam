from .cloudwatch import CloudWatch


class ALBInstance:
    def __init__(self, client, info):
        self.client = client
        self.arn = info.get('LoadBalancerArn')
        self.name = info.get('LoadBalancerName')

    def __str__(self):
        return '(ALBInstance) Name: %s' % self.name

    def default_dimension_name(self):
        return 'LoadBalancer'

    def default_dimension_value(self):
        return self.arn.partition('/')[-1]

    def default_dimensions(self):
        return [dict(Name=self.default_dimension_name(),
                     Value=self.default_dimension_value())]

    def dict(self):
        return {'LoadBalancerArn': self.arn,
                'LoadBalancerName': self.name}


class ALB(CloudWatch, object):

    DEFAULT_NAMESPACE = 'AWS/ApplicationELB'
    ALARM_NAME_PREFIX = 'ALB'

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        super(ALB, self).__init__(aws_access_key_id=aws_access_key_id,
                                  aws_access_secret_key=aws_access_secret_key,
                                  aws_session_token=aws_session_token,
                                  aws_default_region=aws_default_region,
                                  debug=debug)
        self.client = self.session.client('elbv2')

    def _describe_load_balancers(self):
        albs = []
        pager = self.client.get_paginator('describe_load_balancers')
        for page in pager.paginate():
            for i in page['LoadBalancers']:
                albs.append(ALBInstance(self.client, i))
        return albs

    def list(self):
        return self._describe_load_balancers()

    def remote_alarms(self, namespace=DEFAULT_NAMESPACE,
                      prefix=ALARM_NAME_PREFIX):
        namespace = namespace or ALB.DEFAULT_NAMESPACE
        prefix = prefix or ALB.ALARM_NAME_PREFIX
        return super(ALB, self).remote_alarms(namespace=namespace,
                                              prefix=prefix)

    def create(self, objects, namespace=DEFAULT_NAMESPACE,
               prefix=ALARM_NAME_PREFIX, default=None, only=None,
               exclude=None, sns={}, simulate=False):
        if exclude is not None and only is not None:
            raise "Exclude and Only option are mutually exclusive."

        instances = self._describe_load_balancers()
        super(ALB, self).create(instances=instances,
                                objects=objects,
                                namespace=namespace,
                                prefix=prefix,
                                default=default,
                                only=only,
                                exclude=exclude,
                                sns=sns,
                                simulate=simulate)
