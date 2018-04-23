from .cloudwatch import CloudWatch


class ELBInstance:
    def __init__(self, client, info):
        self.client = client
        self.arn = info.get('LoadBalancerArn')
        self.name = info.get('LoadBalancerName')

    def __str__(self):
        return '(ELBInstance) Name: %s' % self.name

    def default_dimension_name(self):
        return 'LoadBalancerName'

    def default_dimension_value(self):
        return self.name

    def default_dimensions(self):
        return [dict(Name=self.default_dimension_name(),
                     Value=self.default_dimension_value())]

    def dict(self):
        return {'LoadBalancerArn': self.arn,
                'LoadBalancerName': self.name}


class ELB(CloudWatch, object):

    DEFAULT_NAMESPACE = 'AWS/ELB'
    ALARM_NAME_PREFIX = 'ELB'

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        super(ELB, self).__init__(aws_access_key_id=aws_access_key_id,
                                  aws_access_secret_key=aws_access_secret_key,
                                  aws_session_token=aws_session_token,
                                  aws_default_region=aws_default_region,
                                  debug=debug)
        self.client = self.session.client('elbv2')

    def _describe_load_balancers(self):
        elbs = []
        pager = self.client.get_paginator('describe_load_balancers')
        for page in pager.paginate():
            for i in page['LoadBalancers']:
                elbs.append(ELBInstance(self.client, i))
        return elbs

    def list(self):
        return self._describe_load_balancers()

    def remote_alarms(self, namespace=DEFAULT_NAMESPACE,
                      prefix=ALARM_NAME_PREFIX):
        namespace = namespace or ELB.DEFAULT_NAMESPACE
        prefix = prefix or ELB.ALARM_NAME_PREFIX
        return super(ELB, self).remote_alarms(namespace=namespace,
                                              prefix=prefix)

    def create(self, objects, namespace=DEFAULT_NAMESPACE,
               prefix=ALARM_NAME_PREFIX, default=None, only=None,
               exclude=None, sns={}, simulate=False):
        if exclude is not None and only is not None:
            raise "Exlude and Only option are mutually exclusive."

        instances = self._describe_load_balancers()
        super(ELB, self).create(instances=instances,
                                objects=objects,
                                namespace=namespace,
                                prefix=prefix,
                                default=default,
                                only=only,
                                exclude=exclude,
                                sns=sns,
                                simulate=simulate)
