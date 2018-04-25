from .cloudwatch import CloudWatch


class ElastiCacheInstance:

    TYPE_TO_CORES = {
        "cache.t2.micro": 1,
        "cache.t2.small": 1,
        "cache.t2.medium": 2,
        "cache.m3.medium": 1,
        "cache.m3.large": 2,
        "cache.m3.xlarge": 4,
        "cache.m3.2xlarge": 8,
        "cache.m4.large": 2,
        "cache.m4.xlarge": 4,
        "cache.m4.2xlarge": 8,
        "cache.m4.4xlarge": 16,
        "cache.m4.10xlarge": 40,
        "cache.r3.large": 2,
        "cache.r3.xlarge": 4,
        "cache.r3.2xlarge": 8,
        "cache.r3.4xlarge": 16,
        "cache.r3.8xlarge": 32,
        "cache.r4.large": 2,
        "cache.r4.xlarge": 4,
        "cache.r4.2xlarge": 8,
        "cache.r4.4xlarge": 16,
        "cache.r4.8xlarge": 32,
        "cache.r4.16xlarge": 64,
    }

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

    def cpu_utilization_threshold_modifier(self, threshold):
        if self.engine == 'redis':
            if self.type not in self.TYPE_TO_CORES:
                raise Exception('Unknown instance type %s.' % self.type)
            cores = self.TYPE_TO_CORES[self.type]
            return threshold / cores
        return threshold

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

    def _describe_elastic_caches(self):
        caches = []
        pager = self.client.get_paginator('describe_cache_clusters')
        for page in pager.paginate():
            for i in page['CacheClusters']:
                caches.append(ElastiCacheInstance(self.client, i))
        return caches

    def list(self):
        return self._describe_elastic_caches()

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

        instances = self._describe_elastic_caches()

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
