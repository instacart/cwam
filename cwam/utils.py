def to_underscore(name):
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def json_serializer(obj):
    """Default JSON serializer."""
    import calendar
    import datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 +
            obj.microsecond / 1000
        )
        return millis

    if isinstance(obj, set):
        return list(obj)

    raise TypeError('Not sure how to serialize %s' % (obj,))


def filter_only(iterable, only):
    out = []
    for info in only:
        for i in iterable:
            if info['regexp'].search(i.dict().get(info['key'])):
                out.append(i)
    return out


def filter_exclude(iterable, only):
    out = []
    for info in only:
        for i in iterable:
            if not info['regexp'].search(i.dict().get(info['key'])):
                out.append(i)
    return out


def extract_alarm_actions(default, params, sns, action):
    actions_sns = []
    if params.get(action):
        for _sns in params.get(action):
            if _sns.startswith('arn:'):
                actions_sns.append(_sns)
            elif sns.get(_sns):
                actions_sns.append(sns.get(_sns))

    if len(actions_sns) < 1 and sns.get('default'):
        _sns = sns.get('default')
        if _sns and _sns.startswith('arn:'):
            actions_sns.append(_sns)

    return actions_sns


def resolved_dict(name, instance, original, default, namespace=None,
                  prefix=None, sns={}):
    import copy
    original = copy.deepcopy(original)
    default = copy.deepcopy(default)

    default_params = {}
    default_all_params = {}
    default_instance_params = {}

    if default.get('all'):
        default_all_params = default.get('all').dict()
        for k in default_all_params.keys():
            if not default_all_params[k]:
                del default_all_params[k]

    filtered_instance = list(filter(lambda i: i in instance.name, default.keys()))  # noqa E501
    instance_name = instance.name
    if len(filtered_instance) > 0:
        instance_name = max(filtered_instance, key=len)

    if default.get(instance_name):
        default_instance_params = default.get(instance_name).dict()
        for k in list(default_instance_params):
            if not default_instance_params[k]:
                del default_instance_params[k]

    default_params = dict(default_all_params, **default_instance_params)

    params = {}

    params = dict(original, **default_params)

    params['AlarmActions'] = extract_alarm_actions(default, params, sns, 'AlarmActions')  # noqa E501
    params['OKActions'] = extract_alarm_actions(default, params, sns, 'OKActions')  # noqa E501
    params['InsufficientDataActions'] = extract_alarm_actions(default, params, sns, 'InsufficientDataActions')  # noqa E501

    if prefix is not None:
        params['AlarmName'] = '{}/{}/{}'.format(prefix, instance.name, name)

    if params.get('Dimensions') and len(params.get('Dimensions')) > 0:
        for dim in params['Dimensions']:
            value = dim.get('Value')
            if value:
                dim['Value'] = instance.dict().get(value)
    else:
        params['Dimensions'] = instance.default_dimensions()

    for attr in params:
        method_name = '%s_%s_modifier' % (to_underscore(params['MetricName']), attr.lower())  # noqa E501
        if(hasattr(instance, method_name)):
            params[attr] = getattr(instance, method_name)(params[attr])

    return params
