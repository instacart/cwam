from .cloudwatch import CloudWatch


class EC2Instance:

    TYPE_TO_CORES = {
        "t1.micro": 1,
        "t2.micro": 1,
        "t2.small": 1,
        "t2.medium": 2,
        "t2.large": 2,
        "t2.xlarge": 4,
        "t2.2xlarge": 8,
        "m1.small": 1,
        "m1.medium": 1,
        "m1.large": 2,
        "m1.xlarge": 4,
        "m2.xlarge": 2,
        "m2.2xlarge": 4,
        "m2.4xlarge": 8,
        "m3.medium": 1,
        "m3.large": 1,
        "m3.xlarge": 2,
        "m3.2xlarge": 4,
        "m4.large": 1,
        "m4.xlarge": 2,
        "m4.2xlarge": 4,
        "m4.4xlarge": 8,
        "m4.10xlarge": 20,
        "m4.16xlarge": 32,
        "c1.medium": 2,
        "c1.xlarge": 8,
        "cc2.8xlarge": 16,
        "cg1.4xlarge": 8,
        "cr1.8xlarge": 16,
        "c3.large": 1,
        "c3.xlarge": 2,
        "c3.2xlarge": 4,
        "c3.4xlarge": 8,
        "c3.8xlarge": 16,
        "c4.large": 1,
        "c4.xlarge": 2,
        "c4.2xlarge": 4,
        "c4.4xlarge": 8,
        "c4.8xlarge": 18,
        "hi1.4xlarge": 8,
        "hs1.8xlarge": 8,
        "g2.2xlarge": 16,
        "x1.16xlarge": 32,
        "x1.32xlarge": 64,
        "r4.large": 1,
        "r4.xlarge": 2,
        "r4.2xlarge": 4,
        "r4.4xlarge": 8,
        "r4.8xlarge": 16,
        "r4.16xlarge": 32,
        "r3.large": 1,
        "r3.xlarge": 2,
        "r3.2xlarge": 4,
        "r3.4xlarge": 8,
        "r3.8xlarge": 16,
        "p2.xlarge": 2,
        "p2.8xlarge": 16,
        "p2.16xlarge": 32,
        "i3.large": 1,
        "i3.xlarge": 2,
        "i3.2xlarge": 4,
        "i3.4xlarge": 8,
        "i3.8xlarge": 16,
        "i3.16xlarge": 32,
        "i2.xlarge": 2,
        "i2.2xlarge": 4,
        "i2.4xlarge": 8,
        "i2.8xlarge": 16,
        "d2.xlarge": 2,
        "d2.2xlarge": 4,
        "d2.4xlarge": 8,
        "d2.8xlarge": 18
    }

    def __init__(self, client, info):
        self.client = client
        find_name_in_tags = filter(lambda tag: tag['Key'] == 'Name', info.get('Tags')) # noqa E501
        self.instance_id = info.get('InstanceId')
        self.type = info.get('InstanceType')
        if find_name_in_tags and len(find_name_in_tags) > 0:
            self.name = find_name_in_tags[0]['Value']
        else:
            self.name = self.instance_id

    def __str__(self):
        return '(EC2Instance) Name: %s | Type: %s' % (self.name, self.type)

    def default_dimension_name(self):
        return 'InstanceId'

    def default_dimension_value(self):
        return self.instance_id

    def default_dimensions(self):
        return [dict(Name=self.default_dimension_name(),
                     Value=self.default_dimension_value())]

    def cpu_utilization_threshold_modifier(self, threshold):
        if self.type not in self.TYPE_TO_CORES:
            raise Exception('Unknown instance type %s.' % self.type)
        cores = self.TYPE_TO_CORES[self.type]
        return threshold / cores

    def dict(self):
        return {'InstanceId': self.instance_id,
                'Type': self.type}


class EC2(CloudWatch, object):

    DEFAULT_NAMESPACE = 'AWS/EC2'
    ALARM_NAME_PREFIX = 'EC2'

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        super(EC2, self).__init__(aws_access_key_id=aws_access_key_id,
                                  aws_access_secret_key=aws_access_secret_key,
                                  aws_session_token=aws_session_token,
                                  aws_default_region=aws_default_region,
                                  debug=debug)
        self.client = self.session.client('ec2')

    def _describe_instances(self):
        ec2s = []
        pager = self.client.get_paginator('describe_instances')
        for page in pager.paginate():
            for r in page['Reservations']:
                for i in r['Instances']:
                    ec2s.append(EC2Instance(self.client, i))
        return ec2s

    def list(self):
        return self._describe_instances()

    def remote_alarms(self, namespace=DEFAULT_NAMESPACE,
                      prefix=ALARM_NAME_PREFIX):
        namespace = namespace or EC2.DEFAULT_NAMESPACE
        prefix = prefix or EC2.ALARM_NAME_PREFIX
        return super(EC2, self).remote_alarms(namespace=namespace,
                                              prefix=prefix)

    def create(self, objects, namespace=DEFAULT_NAMESPACE,
               prefix=ALARM_NAME_PREFIX, default=None, only=None,
               exclude=None, sns={}, simulate=False):
        if exclude is not None and only is not None:
            raise "Exlude and Only option are mutually exclusive."

        instances = self._describe_instances()
        super(EC2, self).create(instances=instances,
                                objects=objects,
                                namespace=namespace,
                                prefix=prefix,
                                default=default,
                                only=only,
                                exclude=exclude,
                                sns=sns,
                                simulate=simulate)
