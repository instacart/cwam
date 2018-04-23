class Alarm(object):

    CREATED_BY_SCRIPT_STR = 'Created by Script'

    def __init__(self, name, namespace=None, info={}):
        self.update(name=name, namespace=namespace, info=info)
        self.resolved = False
        self.is_human = False

    def update(self, name=None, namespace=None, info={}):
        self.name = info.get('AlarmName') or name
        self.namespace = info.get('Namespace') or namespace
        self.arn = info.get('AlarmArn')
        self.metric_name = info.get('MetricName')
        self.statistic = info.get('Statistic')
        self.comparison_operator = info.get('ComparisonOperator')
        self.evaluation_periods = info.get('EvaluationPeriods')
        self.period = info.get('Period')
        self.threshold = info.get('Threshold')
        self.alarm_actions = info.get('AlarmActions')
        self.ok_actions = info.get('OKActions')
        self.dimensions = info.get('Dimensions') or []
        self.description = info.get('AlarmDescription') or self.CREATED_BY_SCRIPT_STR  # noqa E501
        self.treat_missing_data = info.get('TreatMissingData') or 'missing'

    def is_valid(self):
        cond1 = self.name
        cond2 = self.metric_name
        cond3 = self.period
        cond4 = self.evaluation_periods
        cond5 = self.statistic
        cond6 = self.dimensions
        cond7 = self.description
        cond8 = ((self.alarm_actions and len(self.alarm_actions)) > 0 or (self.ok_actions and len(self.ok_actions) > 0))  # noqa E501
        return all([cond1, cond2, cond3, cond4, cond5, cond6, cond7, cond8])

    def is_created_by_script(self):
        cond1 = self.description
        cond2 = self.description == self.CREATED_BY_SCRIPT_STR
        return all([cond1, cond2])

    def dict(self):
        return self.all_dict()

    def all_dict(self):
        return {'AlarmName': self.name,
                'Namespace': self.namespace,
                'MetricName': self.metric_name,
                'Statistic': self.statistic,
                'ComparisonOperator': self.comparison_operator,
                'EvaluationPeriods': self.evaluation_periods,
                'Period': self.period,
                'Threshold': self.threshold,
                'AlarmActions': self.alarm_actions or [],
                'OKActions': self.ok_actions or [],
                'Dimensions': self.dimensions,
                'AlarmDescription': self.description,
                'TreatMissingData': self.treat_missing_data}

    def __str__(self):
        return ('{} ('
                'Namespace: {}, '
                'MetricName: {}, '
                'Statistic: {}, '
                'ComparisonOperator: {}, '
                'EvaluationPeriods: {}, '
                'Period: {}, '
                'Threshold: {}, '
                'Created by script: {}').format(self.name,
                                                self.namespace or None,
                                                self.metric_name,
                                                self.statistic,
                                                self.comparison_operator,
                                                self.evaluation_periods,
                                                self.period,
                                                self.threshold,
                                                self.is_created_by_script())
