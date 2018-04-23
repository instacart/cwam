import time

from dictdiffer import diff

from .client import Client
from .alarm import Alarm
from .utils import filter_only, filter_exclude, resolved_dict


class CloudWatch(Client, object):

    def __init__(self, aws_access_key_id=None, aws_access_secret_key=None,
                 aws_session_token=None, aws_default_region=None, debug=None):
        super(CloudWatch, self).__init__(aws_access_key_id,
                                         aws_access_secret_key,
                                         aws_session_token,
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
                print(e)
                continue
            break
        else:
            print('Exception when doing put_metric_alarm.')

    def create(self, instances, objects, namespace, prefix, default=None,
               only=None, exclude=None, sns={}, simulate=False):
        remote_alarms = self.remote_alarms(namespace=namespace, prefix=prefix)
        human_alarms, scripts_alarms = remote_alarms

        if only and len(only) > 0:
            instances = filter_only(instances, only)

        if exclude and len(exclude) > 0:
            instances = filter_exclude(instances, exclude)

        to_create_total = []
        to_update_scripted_total = []
        to_update_humans_total = []
        to_ignore_scripted_total = []
        to_ignore_humans_total = []

        for instance in instances:
            to_create = []
            to_update_scripted = []
            to_update_humans = []
            to_ignore_scripted = []
            to_ignore_humans = []
            all_alarms = objects.get('all') or []
            instance_name = instance.name
            filtered_instance = list(filter(lambda i: i in instance.name, objects.keys())) # noqa E501
            if len(filtered_instance) > 0:
                instance_name = max(filtered_instance, key=len)
            alarms = objects.get(instance_name) or []
            alarms_names = [a.name for a in alarms]
            all_alarms = [obj for obj in all_alarms if obj.name not in alarms_names] # noqa E501
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

                    print('  - Checking alarm: {}'.format(alarm.name))

                    found1 = [a for a in human_alarms if a.name == alarm.name]
                    found2 = [a for a in scripts_alarms if a.name == alarm.name] # noqa E501

                    if found1 and len(found1) > 0:
                        found1 = found1[0]
                    if found2 and len(found2) > 0:
                        found2 = found2[0]

                    is_human = all([found1, not found2])

                    if "MaximumUsedTransactionIDs" in alarm.metric_name:
                        alarm.ok_actions = [sns['default']]
                        alarm.alarm_actions = [sns['default']]
                        alarm.threshold = 1000000000

                    if "HTTPCode_ELB_5XX_Count" in alarm.metric_name:
                        alarm.ok_actions = [sns['default']]
                        alarm.alarm_actions = [sns['default']]

                    if "5XX" in alarm.metric_name:
                        alarm.treat_missing_data = 'notBreaching'

                    if is_human:
                        alarm.threshold = found1.threshold
                        alarm.description = found1.description
                        alarm.evaluation_periods = found1.evaluation_periods
                        alarm.period = found1.period

                    if alarm.is_valid():
                        if is_human:
                            alarm.is_human = True
                            found1.is_human = True
                            dict1 = found1.dict()
                        else:
                            dict1 = found2.dict() if type(found2).__name__ == 'Alarm' else {}  # noqa E501

                        dict2 = alarm.dict()

                        if dict1 and dict2:
                            differences = list(diff(dict1, dict2))
                            if len(differences) > 0:
                                if is_human:
                                    to_update_humans.append(alarm)
                                else:
                                    to_update_scripted.append(alarm)
                                if self.debug:
                                    print('    - Update action. (Human alarm: %s)') % is_human  # noqa E501
                                    print('      - Diff:')
                                    for changes in differences:
                                        keys = changes[1]
                                        values = changes[2]
                                        print('        - %s | %s | %s') % (changes[0], keys, values)  # noqa E501
                            else:
                                if is_human:
                                    if self.debug:
                                        print('      - Already up to date.')
                                    to_ignore_humans.append(alarm)
                                    continue
                                else:
                                    if self.debug:
                                        print('      - Already up to date.')
                                    to_ignore_scripted.append(alarm)
                                    continue
                        else:
                            to_create.append(alarm)
                            if self.debug:
                                print('    - Create action.')
                                print('      - Params: {}'.format(alarm.dict()))  # noqa E501
                    else:
                        print('  - Invalid parameters.')
                        print('    - Params: {}'.format(alarm.dict()))

                    if self.debug:
                        print  # New line

                    if not simulate:
                        self.create_alarm(**alarm.dict())

                print('\n  - Create total: {}'.format(len(to_create)))
                print('  - Update total: (Scripted: {} | Humans: {})'.format(len(to_update_scripted),  # noqa E501
                                                                             len(to_update_humans)))  # noqa E501
                print('  - Ignore total: (Scripted: {} | Humans: {})'.format(len(to_ignore_scripted),  # noqa E501
                                                                             len(to_ignore_humans)))  # noqa E501

                to_create_total.append(to_create)
                to_update_scripted_total.append(to_update_scripted)
                to_update_humans_total.append(to_update_humans)
                to_ignore_scripted_total.append(to_ignore_scripted)
                to_ignore_humans_total.append(to_ignore_humans)

                print  # New line
            else:
                print('  - None')

        print('\nCreate total: {}'.format(sum([len(a) for a in to_create_total])))  # noqa E501
        print('Update total: (Scripted: {} | Humans: {})'.format(sum([len(a) for a in to_update_scripted_total]),  # noqa E501
                                                                 sum([len(a) for a in to_update_humans_total])))  # noqa E501
        print('Ignore total: (Scripted: {} | Humans: {})'.format(sum([len(a) for a in to_ignore_scripted_total]),  # noqa E501
                                                                 sum([len(a) for a in to_ignore_humans_total])))  # noqa E501
