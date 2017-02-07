# -*- coding: utf-8 -*-
import json
import os
import re
import yaml
from os.path import expanduser

import click

from .default_alarm import DefaultAlarm
from .alarm import Alarm
from .alb import ALB
from .elb import ELB
from .rds import RDS
from .elastic_cache import ElasticCache
from .utils import json_serializer

# Fix Python 2.x vs 3.x.
try:
    bool(type(unicode))
    UNICODE_TYPE = unicode
except NameError:
    UNICODE_TYPE = str


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
CONF_FILE = "{0}/{1}/{2}".format(expanduser("~"),
                                 '.cwam',
                                 'conf.yml')
ALB_TMP_FILE = "{0}/{1}/{2}".format(expanduser("~"),
                                    '.cwam',
                                    'alb.template.yml')
ELB_TMP_FILE = "{0}/{1}/{2}".format(expanduser("~"),
                                    '.cwam',
                                    'elb.template.yml')
RDS_TMP_FILE = "{0}/{1}/{2}".format(expanduser("~"),
                                    '.cwam',
                                    'rds.template.yml')
ELASTIC_CACHE_TMP_FILE = "{0}/{1}/{2}".format(expanduser("~"),
                                              '.cwam',
                                              'elastic_cache.template.yml')


def json_dumps(dict, pretty=False):
    if pretty:
        return json.dumps(dict, indent=2, default=json_serializer)
    else:
        return json.dumps(dict, default=json_serializer)


def parse_yml(ctx, path):
    with open(path, 'r') as stream:
        try:
            content = yaml.load(stream)
        except yaml.YAMLError as e:
            ctx.fail(e)
        return content


def parse_exclude_only(infos):
    if infos:
        d = [dict(key=i['key'], regexp=re.compile(i['regexp'])) for i in infos]
        return d
    else:
        return infos


def parse_default_alarm(namespace, objects):
    alarms = {}
    for k, v in objects.iteritems():
        alarms[k] = DefaultAlarm(namespace=namespace, info=v)
    return alarms


def parse_alarms(namespace, objects):
    alarms = {}
    for k, v in objects.iteritems():
        alarms_obj = []
        for alarm in v:
            name = next(iter(alarm))
            alarms_obj.append(Alarm(name=name,
                                    namespace=namespace,
                                    info=alarm.get(name)))
        alarms[k] = alarms_obj
    return alarms


def parse_alarms_yml(ctx, command, conf):
    if os.path.isfile(conf):
        namespace = parse_yml(ctx, conf).get(command).get('namespace')
        alarms = parse_yml(ctx, conf).get(command).get('alarms')
        return namespace, alarms
    else:
        ctx.fail('Conf file not found. Make sure --template is a valid path.')


@click.version_option('0.1.0')
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug', '-d', flag_value=True, default=False,
              help='Debug mode.')
@click.option('--pretty', '-p', flag_value=True, default=False,
              help='Prettify JSON output.')
@click.option('--aws-access-key-id', '-k', type=UNICODE_TYPE,
              envvar='AWS_ACCESS_KEY_ID',
              help='AWS Access Key ID.')
@click.option('--aws-access-secret-key', '-s', type=UNICODE_TYPE,
              envvar='AWS_SECRET_ACCESS_KEY',
              help='AWS Secret Access Key.')
@click.option('--aws_default_region', '-r', type=UNICODE_TYPE,
              envvar='AWS_DEFAULT_REGION',
              help='AWS Region.')
@click.option('--conf', '-c', type=UNICODE_TYPE,
              default=CONF_FILE,
              help='Path to configuration file. Default: {0}.'.format(CONF_FILE))
@click.pass_context
def main(ctx, debug, pretty, aws_access_key_id, aws_access_secret_key,
         aws_default_region, conf):
    if not aws_access_key_id:
        if os.path.isfile(conf):
            aws = parse_yml(ctx, conf)['aws']
            aws_access_key_id = aws['aws_access_key_id']
        else:
            ctx.fail("""AWS Access Key ID not found.
AWS Access Key ID not found in AWS_ACCESS_KEY_ID environment variable.
AWS Access Key ID not found in -k/--aws-access-key-id option.
AWS Access Key ID not found in configuration file: {0}.""".format(conf))

    if not aws_access_secret_key:
        if os.path.isfile(conf):
            aws = parse_yml(ctx, conf)['aws']
            aws_access_secret_key = aws['aws_access_secret_key']
        else:
            ctx.fail("""AWS Secret Access Key not found.
AWS Secret Access Key not found in AWS_SECRET_ACCESS_KEY environment variable.
AWS Secret Access Key not found in -s/--aws-access-secret-key option.
AWS Secret Access Key not found in configuration file: {0}.""".format(conf))

    if not aws_default_region:
        if os.path.isfile(conf):
            aws = parse_yml(ctx, conf)['aws']
            aws_access_secret_key = aws['aws_default_region']
        else:
            ctx.fail("""AWS Region not found.
AWS Region not found in AWS_DEFAULT_REGION environment variable.
AWS Region not found in -r/--region option.
AWS Region not found in configuration file: {0}.""".format(conf))

    ctx.obj = {}
    ctx.obj['PRETTY'] = pretty if pretty else None
    ctx.obj['DEBUG'] = debug if debug else None

    if aws_access_key_id:
        ctx.obj['AWS_ACCESS_KEY_ID'] = aws_access_key_id
    else:
        ctx.obj['AWS_ACCESS_KEY_ID'] = None

    if aws_access_secret_key:
        ctx.obj['AWS_SECRET_ACCESS_KEY'] = aws_access_secret_key
    else:
        ctx.obj['AWS_SECRET_ACCESS_KEY'] = None

    if aws_default_region:
        ctx.obj['AWS_DEFAULT_REGION'] = aws_default_region
    else:
        ctx.obj['AWS_DEFAULT_REGION'] = None

@main.group()
@click.pass_context
def alb(ctx):
    pass


@alb.command(name='list')  # noqa: F811
@click.pass_context
def alb_list(ctx):
    """List ALB."""
    instances = ALB(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
                    aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
                    aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
                    debug=ctx.obj['DEBUG']).list()
    for instance in instances:
        click.echo(instance)


@alb.command(name='create')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=ALB_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(ALB_TMP_FILE))
@click.option('--simulate', '-s', is_flag=True, default=False,
              help='Simulate only. Do not take actions')
def alb_create(ctx, template, simulate):
    """Create alarms configured in --template file"""
    if os.path.isfile(template):
        template = parse_yml(ctx, template)['alb']
        namespace = template.get('namespace')
        prefix = template.get('prefix')
        only = template.get('only')
        exclude = template.get('exclude')
        sns = template.get('sns')
        default = template.get('default')
        alarms = template.get('alarms')
    else:
        ctx.fail('Conf file not found. Make sure --template is a valid path.')

    if len(alarms) > 0:
        alb = ALB(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
                  aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
                  aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
                  debug=ctx.obj['DEBUG'])
        alb.create(objects=parse_alarms(namespace, alarms),
                   namespace=namespace,
                   prefix=prefix,
                   default=parse_default_alarm(namespace, default),
                   only=parse_exclude_only(only),
                   exclude=parse_exclude_only(exclude),
                   sns=sns,
                   simulate=simulate)
    else:
        click.echo('No alarms found.')


@alb.command(name='local-alarms')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=ALB_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(ALB_TMP_FILE))
def alb_local_alarms(ctx, template):
    namespace, alarms = parse_alarms_yml(ctx, 'alb', template)
    for k, v in parse_alarms(namespace, alarms).iteritems():
        click.echo(k)
        for alarm in v:
            click.echo(str(alarm))


@alb.command(name='remote-alarms')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=ALB_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(ALB_TMP_FILE))
@click.option('--no-human', '-h', is_flag=True, default=False,
              help='Show only human alarms.')
@click.option('--no-script', '-s', is_flag=True, default=False,
              help='Show only script alarms.')
def alb_remote_alarms(ctx, template, no_human, no_script):
    """List alarms configured on AWS"""
    if os.path.isfile(template):
        template = parse_yml(ctx, template)['alb']
        namespace = template.get('namespace')
        prefix = template.get('prefix')
    else:
        namespace = None
        prefix = None

    alb = ALB(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
              aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
              aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
              debug=ctx.obj['DEBUG'])
    human_alarms, script_alarms = alb.remote_alarms(namespace=namespace,
                                                    prefix=prefix)

    if not no_human:
        click.echo('Human alarms.')
        if len(human_alarms) > 0:
            for alarm in human_alarms:
                click.echo(str(alarm))
        else:
            click.echo('None.')

    if not no_script:
        click.echo('Script alarms.')
        if len(script_alarms) > 0:
            for alarm in script_alarms:
                click.echo(str(alarm))
        else:
            click.echo('None.')


@main.group()
@click.pass_context
def elb(ctx):
    pass


@elb.command(name='list')  # noqa: F811
@click.pass_context
def elb_list(ctx):
    """List ELB."""
    instances = ELB(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
                    aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
                    aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
                    debug=ctx.obj['DEBUG']).list()
    for instance in instances:
        click.echo(instance)


@elb.command(name='create')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=ELB_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(ELB_TMP_FILE))
@click.option('--simulate', '-s', is_flag=True, default=False,
              help='Simulate only. Do not take actions')
def elb_create(ctx, template, simulate):
    """Create alarms configured in --template file"""
    if os.path.isfile(template):
        template = parse_yml(ctx, template)['elb']
        namespace = template.get('namespace')
        prefix = template.get('prefix')
        only = template.get('only')
        exclude = template.get('exclude')
        sns = template.get('sns')
        default = template.get('default')
        alarms = template.get('alarms')
    else:
        ctx.fail('Conf file not found. Make sure --template is a valid path.')

    if len(alarms) > 0:
        elb = ELB(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
                  aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
                  aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
                  debug=ctx.obj['DEBUG'])
        elb.create(objects=parse_alarms(namespace, alarms),
                   namespace=namespace,
                   prefix=prefix,
                   default=parse_default_alarm(namespace, default),
                   only=parse_exclude_only(only),
                   exclude=parse_exclude_only(exclude),
                   sns=sns,
                   simulate=simulate)
    else:
        click.echo('No alarms found.')


@elb.command(name='local-alarms')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=ELB_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(ELB_TMP_FILE))
def elb_local_alarms(ctx, template):
    namespace, alarms = parse_alarms_yml(ctx, 'elb', template)
    for k, v in parse_alarms(namespace, alarms).iteritems():
        click.echo(k)
        for alarm in v:
            click.echo(str(alarm))


@elb.command(name='remote-alarms')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=ELB_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(ELB_TMP_FILE))
@click.option('--no-human', '-h', is_flag=True, default=False,
              help='Show only human alarms.')
@click.option('--no-script', '-s', is_flag=True, default=False,
              help='Show only script alarms.')
def elb_remote_alarms(ctx, template, no_human, no_script):
    """List alarms configured on AWS"""
    if os.path.isfile(template):
        template = parse_yml(ctx, template)['elb']
        namespace = template.get('namespace')
        prefix = template.get('prefix')
    else:
        namespace = None
        prefix = None

    elb = ELB(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
              aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
              aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
              debug=ctx.obj['DEBUG'])
    human_alarms, script_alarms = elb.remote_alarms(namespace=namespace,
                                                    prefix=prefix)

    if not no_human:
        click.echo('Human alarms.')
        if len(human_alarms) > 0:
            for alarm in human_alarms:
                click.echo(str(alarm))
        else:
            click.echo('None.')

    if not no_script:
        click.echo('Script alarms.')
        if len(script_alarms) > 0:
            for alarm in script_alarms:
                click.echo(str(alarm))
        else:
            click.echo('None.')


@main.group()
@click.pass_context
def rds(ctx):
    pass


@rds.command(name='list')  # noqa: F811
@click.pass_context
def rds_list(ctx):
    """List RDS clusters."""
    instances = RDS(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
                    aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
                    aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
                    debug=ctx.obj['DEBUG']).list()
    for instance in instances:
        click.echo(instance)


@rds.command(name='create')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=RDS_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(RDS_TMP_FILE))
@click.option('--simulate', '-s', is_flag=True, default=False,
              help='Simulate only. Do not take actions')
def rds_create(ctx, template, simulate):
    """Create alarms configured in --template file"""
    if os.path.isfile(template):
        template = parse_yml(ctx, template)['rds']
        namespace = template.get('namespace')
        prefix = template.get('prefix')
        only = template.get('only')
        exclude = template.get('exclude')
        sns = template.get('sns')
        default = template.get('default')
        alarms = template.get('alarms')
    else:
        ctx.fail('Conf file not found. Make sure --template is a valid path.')

    if len(alarms) > 0:
        rds = RDS(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
                  aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
                  aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
                  debug=ctx.obj['DEBUG'])
        rds.create(objects=parse_alarms(namespace, alarms),
                   namespace=namespace,
                   prefix=prefix,
                   default=parse_default_alarm(namespace, default),
                   only=parse_exclude_only(only),
                   exclude=parse_exclude_only(exclude),
                   sns=sns,
                   simulate=simulate)
    else:
        click.echo('No alarms found.')


@rds.command(name='local-alarms')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=RDS_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(RDS_TMP_FILE))
def rds_local_alarms(ctx, template):
    namespace, alarms = parse_alarms_yml(ctx, 'rds', template)
    for k, v in parse_alarms(namespace, alarms).iteritems():
        click.echo(k)
        for alarm in v:
            click.echo(str(alarm))


@rds.command(name='remote-alarms')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=RDS_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(RDS_TMP_FILE))
@click.option('--no-human', '-h', is_flag=True, default=False,
              help='Show only human alarms.')
@click.option('--no-script', '-s', is_flag=True, default=False,
              help='Show only script alarms.')
def rds_remote_alarms(ctx, template, no_human, no_script):
    """List alarms configured on AWS"""
    if os.path.isfile(template):
        template = parse_yml(ctx, template)['rds']
        namespace = template.get('namespace')
        prefix = template.get('prefix')
    else:
        namespace = None
        prefix = None

    rds = RDS(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
              aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
              aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
              debug=ctx.obj['DEBUG'])
    human_alarms, script_alarms = rds.remote_alarms(namespace=namespace,
                                                    prefix=prefix)

    if not no_human:
        click.echo('Human alarms.')
        if len(human_alarms) > 0:
            for alarm in human_alarms:
                click.echo(str(alarm))
        else:
            click.echo('None.')

    if not no_script:
        click.echo('Script alarms.')
        if len(script_alarms) > 0:
            for alarm in script_alarms:
                click.echo(str(alarm))
        else:
            click.echo('None.')

@main.group()
@click.pass_context
def elastic_cache(ctx):
    pass


@elastic_cache.command(name='list')  # noqa: F811
@click.pass_context
def elastic_cache_list(ctx):
    """List ElasticCache clusters."""
    instances = ElasticCache(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
                    aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
                    aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
                    debug=ctx.obj['DEBUG']).list()
    for instance in instances:
        click.echo(instance)


@elastic_cache.command(name='create')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=ELASTIC_CACHE_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(ELASTIC_CACHE_TMP_FILE))
@click.option('--simulate', '-s', is_flag=True, default=False,
              help='Simulate only. Do not take actions')
def elastic_cache_create(ctx, template, simulate):
    """Create alarms configured in --template file"""
    if os.path.isfile(template):
        template = parse_yml(ctx, template)['elastic_caches']
        namespace = template.get('namespace')
        prefix = template.get('prefix')
        only = template.get('only')
        exclude = template.get('exclude')
        sns = template.get('sns')
        default = template.get('default')
        alarms = template.get('alarms')
    else:
        ctx.fail('Conf file not found. Make sure --template is a valid path.')

    if len(alarms) > 0:
        elastic_cache = ElasticCache(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
                  aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
                  aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
                  debug=ctx.obj['DEBUG'])
        elastic_cache.create(objects=parse_alarms(namespace, alarms),
                   namespace=namespace,
                   prefix=prefix,
                   default=parse_default_alarm(namespace, default),
                   only=parse_exclude_only(only),
                   exclude=parse_exclude_only(exclude),
                   sns=sns,
                   simulate=simulate)
    else:
        click.echo('No alarms found.')


@elastic_cache.command(name='local-alarms')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=ELASTIC_CACHE_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(ELASTIC_CACHE_TMP_FILE))
def elastic_cache_local_alarms(ctx, template):
    namespace, alarms = parse_alarms_yml(ctx, 'elastic_caches', template)
    for k, v in parse_alarms(namespace, alarms).iteritems():
        click.echo(k)
        for alarm in v:
            click.echo(str(alarm))


@elastic_cache.command(name='remote-alarms')  # noqa: F811
@click.pass_context
@click.option('--template', '-t', type=UNICODE_TYPE,
              default=ELASTIC_CACHE_TMP_FILE,
              help='Path to template file. Default: {0}.'.format(ELASTIC_CACHE_TMP_FILE))
@click.option('--no-human', '-h', is_flag=True, default=False,
              help='Show only human alarms.')
@click.option('--no-script', '-s', is_flag=True, default=False,
              help='Show only script alarms.')
def elastic_cache_remote_alarms(ctx, template, no_human, no_script):
    """List alarms configured on AWS"""
    if os.path.isfile(template):
        template = parse_yml(ctx, template)['elastic_caches']
        namespace = template.get('namespace')
        prefix = template.get('prefix')
    else:
        namespace = None
        prefix = None

    elastic_cache = ElasticCache(aws_access_key_id=ctx.obj['AWS_ACCESS_KEY_ID'],
              aws_access_secret_key=ctx.obj['AWS_SECRET_ACCESS_KEY'],
              aws_default_region=ctx.obj['AWS_DEFAULT_REGION'],
              debug=ctx.obj['DEBUG'])
    human_alarms, script_alarms = elastic_cache.remote_alarms(namespace=namespace,
                                                    prefix=prefix)

    if not no_human:
        click.echo('Human alarms.')
        if len(human_alarms) > 0:
            for alarm in human_alarms:
                click.echo(str(alarm))
        else:
            click.echo('None.')

    if not no_script:
        click.echo('Script alarms.')
        if len(script_alarms) > 0:
            for alarm in script_alarms:
                click.echo(str(alarm))
        else:
            click.echo('None.')

if __name__ == "__main__":
    main()
