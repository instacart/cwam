class DefaultAlarm(object):

    def __init__(self, namespace=None, info={}):
        self.namespace = info.get('Namespace') or namespace
        self.evaluation_periods = info.get('EvaluationPeriods')
        self.period = info.get('Period')
        self.alarm_actions = info.get('AlarmActions') or []
        self.ok_actions = info.get('OKActions') or []
        self.dimensions = info.get('Dimensions') or []

    def dict(self):
        return {'AlarmActions': self.alarm_actions,
                'EvaluationPeriods': self.evaluation_periods,
                'Period': self.period,
                'OKActions': self.ok_actions,
                'Dimensions': self.dimensions}

    def __str__(self):
        return ('(AlarmActions: {1}, '
                'EvaluationPeriods: {2}, '
                'Period: {3}, '
                'OKActions: {4}, '
                'Dimensions: {5})').format(self.alarm_actions,
                                           self.evaluation_periods,
                                           self.period,
                                           self.ok_actions,
                                           self.dimensions)
