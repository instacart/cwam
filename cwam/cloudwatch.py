import time

from dictdiffer import diff

from .client import Client
from .alarm import Alarm
from .utils import filter_only, filter_exclude, resolved_dict


class CloudWatch(Client, object):

    def __init__(self, aws_access_key_id, aws_access_secret_key,
                 aws_default_region, debug=None):
        super(CloudWatch, self).__init__(aws_access_key_id,
                                         aws_access_secret_key,
                                         aws_default_region,
                                         debug)
        self.cloudwatch_client = self.session.client('cloudwatch')

    def remote_alarms(self, namespace, prefix):
        script_alarms = []
        human_alarms = []
        pager = self.cloudwatch_client.get_paginator('describe_alarms')
        for page in pager.paginate(AlarmNamePrefix=prefix):
            for alarm in page['MetricAlarms']:
                alarm = Alarm(name=alarm.get('AlarmName'), info=alarm)
                if alarm.namespace != namespace:
                    continue
                if alarm.is_created_by_script():
                    alarm = script_alarms.append(alarm)
                else:
                    human_alarms.append(alarm)
        return human_alarms, script_alarms

    def create_alarm(self, **kwargs):
        for _ in range(3):
            try:
                time.sleep(0.5)
                self.cloudwatch_client.put_metric_alarm(**kwargs)
            except Exception as e:
                print e
                continue
            break
        else:
            print 'Exception when doing put_metric_alarm.'

    def create(self, instances, objects, namespace, prefix, default=None,
               only=None, exclude=None, sns={}, simulate=False):
        remote_alarms = self.remote_alarms(namespace=namespace, prefix=prefix)
        human_alarms, scripts_alarms = remote_alarms

        if only and len(only) > 0:
            instances = filter_only(instances, only)

        if exclude and len(exclude) > 0:
            instances = filter_exclude(instances, exclude)

        to_create_total = []
        to_update_total = []
        to_ignore_cause_up_to_date_total = []
        to_ignore_cause_humans_total = []

        for instance in instances:
            to_create = []
            to_update = []
            to_ignore_cause_up_to_date = []
            to_ignore_cause_humans = []
            all_alarms = objects.get('all') or []
            alarms = objects.get(instance.name) or []
            alarms_names = [a.name for a in alarms]
            all_alarms = [obj for obj in all_alarms if obj.name not in alarms_names]
            alarms = alarms + all_alarms
            if len(alarms) > 0:
                for alarm in alarms:

                    new_params = resolved_dict(name=alarm.name,
                                               instance=instance,
                                               namespace=namespace,
                                               original=alarm.dict(),
                                               default=default,
                                               prefix=prefix,
                                               sns=sns)

                    alarm = Alarm(name=alarm.name, info=new_params)

                    print '  - Checking alarm: {0}'.format(alarm.name)

                    found1 = [a for a in human_alarms if a.name == alarm.name]
                    found2 = [a for a in scripts_alarms if a.name == alarm.name]

                    if found1 and len(found1) > 0:
                        found1 = found1[0]
                    if found2 and len(found2) > 0:
                        found2 = found2[0]

                    if all([found1, not found2]):
                        to_ignore_cause_humans.append(alarm)
                        if self.debug:
                            print '    - Not creating %s because human know better.' % alarm.name
                            differences = list(diff(found1.dict(), alarm.dict()))
                            for changes in differences:
                                keys = changes[1]
                                values = changes[2]
                                print '      - %s | %s | %s' % (changes[0], keys, values)
                        continue

                    if alarm.is_valid():
                        if found2:
                            dict1 = found2.dict()
                            dict2 = alarm.dict()
                            differences = list(diff(dict1, dict2))
                            if len(differences) > 0:
                                to_update.append(alarm)
                                if self.debug:
                                    print '    - Update action.'
                                    print '      - Diff:'
                                    for changes in differences:
                                        keys = changes[1]
                                        values = changes[2]
                                        print '        - %s | %s | %s' % (changes[0], keys, values)
                            else:
                                if self.debug:
                                    print '      - Already up to date.'
                                to_ignore_cause_up_to_date.append(alarm)
                                continue
                        else:
                            to_create.append(alarm)
                            if self.debug:
                                print '    - Create action.'
                                print '      - Params: {0}'.format(alarm.dict())
                    else:
                        print '  - Invalid parameters.'
                        print '    - Params: {0}'.format(alarm.dict())

                    if self.debug:
                        print # New line

                    if not simulate:
                        self.create_alarm(**alarm.dict())

                print '\n  - Create total: {0}'.format(len(to_create))
                print '  - Update total: {0}'.format(len(to_update))
                print '  - Ignore total: (Up to date: {0} | Humans: {1})'.format(len(to_ignore_cause_up_to_date),
                                                                                 len(to_ignore_cause_humans))

                to_update_total.append(to_update)
                to_create_total.append(to_create)
                to_ignore_cause_up_to_date_total.append(to_ignore_cause_up_to_date)
                to_ignore_cause_humans_total.append(to_ignore_cause_humans)

                print # New line
            else:
                print '  - None'

        print '\nCreate total: {0}'.format(sum([len(a) for a in to_create_total]))
        print 'Update total: {0}'.format(sum([len(a) for a in to_update_total]))
        print 'Ignore total: (Up to date: {0} | Humans: {1})'.format(sum([len(a) for a in to_ignore_cause_up_to_date_total]),
                                                                     sum([len(a) for a in to_ignore_cause_humans_total]))
