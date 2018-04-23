from .cloudwatch import CloudWatch


class PGBouncerInstance:
    def __init__(self, info):
        self.name = info

    def __str__(self):
        return '(PGBouncer Instance) Name: %s' % self.name

    def default_dimension_name(self):
        return 'Workers'

    def default_dimension_value(self):
        return self.name.partition('.')[-1]

    def default_dimensions(self):
        return [dict(Name=self.default_dimension_name(),
                     Value=self.default_dimension_value()),
                dict(Name='PGBouncer',
                     Value=self.name)]

    def dict(self):
        return {'PGBouncerIdentifier': self.default_dimension_value()}


class PGBouncer(CloudWatch, object):

    DEFAULT_NAMESPACE = 'ISC'
    ALARM_NAME_PREFIX = 'PGBOUNCER'

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        super(PGBouncer, self).__init__(aws_access_key_id=aws_access_key_id,
                                        aws_access_secret_key=aws_access_secret_key, # noqa E501
                                        aws_session_token=aws_session_token,
                                        aws_default_region=aws_default_region,
                                        debug=debug)

    def _describe_pgbouncer_instances(self):
        response = self.instance_list()
        return [PGBouncerInstance(i) for i in response]

    def list(self):
        return self._describe_pgbouncer_instances()

    def instance_list(self, namespace=DEFAULT_NAMESPACE,
                      prefix=ALARM_NAME_PREFIX):
        human_alarms, script_alarms = self.remote_alarms(namespace, prefix)
        alarms = human_alarms + script_alarms
        all_hosts = set()
        map(lambda alarm: all_hosts.add(
            PGBouncerInstance(alarm.name.split('/')[1])), alarms)
        return list(all_hosts)

    def remote_alarms(self, namespace=DEFAULT_NAMESPACE,
                      prefix=ALARM_NAME_PREFIX):
        namespace = namespace or PGBouncer.DEFAULT_NAMESPACE
        prefix = prefix or PGBouncer.ALARM_NAME_PREFIX
        return super(PGBouncer, self).remote_alarms(namespace=namespace,
                                                    prefix=prefix)

    def create(self, objects, namespace=DEFAULT_NAMESPACE,
               prefix=ALARM_NAME_PREFIX, default=None, only=None,
               exclude=None, sns={}, simulate=False):
        if exclude is not None and only is not None:
            raise "Exclude and Only option are mutually exclusive."

        instances = self.instance_list()
        super(PGBouncer, self).create(instances=instances,
                                      objects=objects,
                                      namespace=namespace,
                                      prefix=prefix,
                                      default=default,
                                      only=only,
                                      exclude=exclude,
                                      sns=sns,
                                      simulate=simulate)
