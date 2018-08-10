from .cloudwatch import CloudWatch


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class ECSInstance:
    def __init__(self, client, info):
        self.client = client
        self.arn = info.get('clusterArn')
        self.name = info.get('clusterName')

    def __str__(self):
        return '(ECSInstance) Name: %s' % self.name

    def default_dimension_name(self):
        return 'ECSCluster'

    def default_dimension_value(self):
        return self.arn.partition('/')[-1]

    def default_dimensions(self):
        return [dict(Name=self.default_dimension_name(),
                     Value=self.default_dimension_value())]

    def dict(self):
        return {'clusterArn': self.arn,
                'clusterName': self.name}


class ECS(CloudWatch, object):

    DEFAULT_NAMESPACE = 'AWS/ECS'
    ALARM_NAME_PREFIX = 'ECS'

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        super(ECS, self).__init__(aws_access_key_id=aws_access_key_id,
                                  aws_access_secret_key=aws_access_secret_key,
                                  aws_session_token=aws_session_token,
                                  aws_default_region=aws_default_region,
                                  debug=debug)
        self.client = self.session.client('ecs')

    def _describe_clusters(self):
        clusters = []
        pager = self.client.get_paginator('list_clusters')
        for page in pager.paginate():
            clusters += page['clusterArns']
        described = []
        for chunk in chunks(clusters, 100):
            resp = self.client.describe_clusters(clusters=chunk)['clusters']
            for cluster in resp:
                described.append(ECSInstance(self.client, cluster))
        return described

    def list(self):
        return self._describe_clusters()

    def remote_alarms(self, namespace=DEFAULT_NAMESPACE,
                      prefix=ALARM_NAME_PREFIX):
        namespace = namespace or ECS.DEFAULT_NAMESPACE
        prefix = prefix or ECS.ALARM_NAME_PREFIX
        return super(ECS, self).remote_alarms(namespace=namespace,
                                              prefix=prefix)

    def create(self, objects, namespace=DEFAULT_NAMESPACE,
               prefix=ALARM_NAME_PREFIX, default=None, only=None,
               exclude=None, sns={}, simulate=False):
        if exclude is not None and only is not None:
            raise "Exclude and Only option are mutually exclusive."

        instances = self._describe_clusters()
        super(ECS, self).create(instances=instances,
                                objects=objects,
                                namespace=namespace,
                                prefix=prefix,
                                default=default,
                                only=only,
                                exclude=exclude,
                                sns=sns,
                                simulate=simulate)
