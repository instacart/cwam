from .cloudwatch import CloudWatch


class ElastiCacheInstance:

    def __init__(self, client, info):
        self.client = client
        self.arn = info.get('CacheClusterArn')
        self.name = info.get('CacheClusterId')
        self.engine = info.get('Engine')
        self.type = info.get('CacheNodeType')

    def __str__(self):
        return '(ElastiCacheInstance) Name: %s, Engine: %s, Type: %s' % (self.name, self.engine, self.type) # noqa E501

    def default_dimension_name(self):
        return 'CacheClusterId'

    def default_dimension_value(self):
        return self.name

    def default_dimensions(self):
        return [dict(Name=self.default_dimension_name(),
                     Value=self.default_dimension_value())]

    def dict(self):
        return {'CacheClusterArn': self.arn,
                'CacheClusterId': self.name}


class ElastiCache(CloudWatch, object):

    DEFAULT_NAMESPACE = 'AWS/ElastiCache'
    ALARM_NAME_PREFIX = 'Cache'

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        super(ElastiCache, self).__init__(aws_access_key_id=aws_access_key_id,
                                          aws_access_secret_key=aws_access_secret_key, # noqa E501
                                          aws_session_token=aws_session_token,
                                          aws_default_region=aws_default_region, # noqa E501
                                          debug=debug)
        self.client = self.session.client('elasticache')

    def _describe_elasticaches(self):
        caches = []
        pager = self.client.get_paginator('describe_cache_clusters')
        for page in pager.paginate():
            for i in page['CacheClusters']:
                caches.append(ElastiCacheInstance(self.client, i))
        return caches

    def list(self):
        return self._describe_elasticaches()

    def remote_alarms(self, namespace=DEFAULT_NAMESPACE,
                      prefix=ALARM_NAME_PREFIX):
        namespace = namespace or ElastiCache.DEFAULT_NAMESPACE
        prefix = prefix or ElastiCache.ALARM_NAME_PREFIX
        return super(ElastiCache, self).remote_alarms(namespace=namespace,
                                                      prefix=prefix)

    def create(self, objects, namespace=DEFAULT_NAMESPACE,
               prefix=ALARM_NAME_PREFIX, default=None, only=None,
               exclude=None, sns={}, simulate=False, engine=None):
        if exclude is not None and only is not None:
            raise "Exlude and Only option are mutually exclusive."

        instances = self._describe_elasticaches()

        redis_instances = [i for i in instances if i.engine == 'redis']
        memcached_instances = [i for i in instances if i not in redis_instances] # noqa E501

        if engine is None or engine == 'redis':
            super(ElastiCache, self).create(instances=redis_instances,
                                            objects=objects,
                                            namespace=namespace,
                                            prefix='%s/redis' % prefix,
                                            default=default,
                                            only=only,
                                            exclude=exclude,
                                            sns=sns,
                                            simulate=simulate)

        if engine is None or engine == 'memcached':
            super(ElastiCache, self).create(instances=memcached_instances,
                                            objects=objects,
                                            namespace=namespace,
                                            prefix='%s/memcached' % prefix,
                                            default=default,
                                            only=only,
                                            exclude=exclude,
                                            sns=sns,
                                            simulate=simulate)
