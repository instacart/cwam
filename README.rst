===============================
CloudWatch Alarms Manager
===============================

|pypi| |travis| |doc| |pyup|

Easy way to create default CloudWatch Alarms.

**CWAM** is creating default alarms associated with default metrics for different kind of AWS resources.

Installation
------------

Install using pip:

.. code:: bash

    $ pip install cwam

Requirements
------------

- Python 2.6, 2.7, 3.3, 3.4, or 3.5
- An AWS account

CWAM
------------

Resources supported
~~~~~~~~~~~~~~~~~~~

- ELB
- ALB
- RDS
- Kinesis
- ElasticCache

Templates samples
~~~~~~~~~~~~~~~~~

- https://github.com/instacart/cwam/blob/master/templates/alb.template.yml
- https://github.com/instacart/cwam/blob/master/templates/rds.template.yml
- https://github.com/instacart/cwam/blob/master/templates/kinesis.template.yml
- https://github.com/instacart/cwam/blob/master/templates/elastic_cache.template.yml

Human interaction
~~~~~~~~~~~~~~~~~

At any time, a human can modify an alarm value created by **CWAM**.
To make sure **CWAM** is not overriding that value again, the alarm description
field needs to be updated with a string different from ``Created by Script``.

CLI
---

CLI Authentication
~~~~~~~~~~~~~~~~~~

Via environment variables:

.. code:: bash

    $ export AWS_ACCESS_KEY_ID="aws_access_key_id"
    $ export AWS_SECRET_ACCESS_KEY="aws_access_secret_key"
    $ export AWS_SESSION_TOKEN="aws_session_token"
    $ export AWS_DEFAULT_REGION="us-east-1"
    $ cwam --conf ~/.cwam/conf.yml elb create -t /path/to/template.yml

Via (--conf/-c) option:

Edit ~/.cwam/conf.yml

.. code:: yaml

    aws:
      aws_access_key_id: aws_access_key_id
      aws_access_secret_key: aws_access_secret_key
      aws_session_token: aws_session_token
      aws_default_region: aws_default_region

.. code:: bash

    $ cwam --conf ~/.cwam/conf.yml elb create -t /path/to/template.yml

Via CLI options:

.. code:: bash

    $ cwam ----aws-access-key-id aws_access_key_id \
    --aws-access-secret-key aws_access_secret_key \
    --aws-session-token aws_session_token \
    --aws_default_region us-east-1 elb create -t /path/to/template.yml

Subcommands
~~~~~~~~~~~

.. code:: plain

    Usage: cwam [OPTIONS] COMMAND [ARGS]...

    Options:
      -d, --debug                     Debug mode.
      -p, --pretty                    Prettify JSON output.
      -k, --aws-access-key-id TEXT    AWS Access Key ID.
      -s, --aws-access-secret-key TEXT
                                      AWS Secret Access Key.
      -t, --aws-session-token TEXT    AWS Secret Access Key.
      -r, --aws_default_region TEXT   AWS Region.
      --version                       Show the version and exit.
      -h, --help                      Show this message and exit.

    Commands:
      alb
      elastic_cache
      elb
      kinesis
      rds

Documentation
=============

- https://cwam.readthedocs.io

History
=======

View the `changelog`_

Authors
=======

-  `Quentin Rousseau`_

License
=======

.. code:: plain

    Copyright (c) 2018 Instacart <quentin@instacart.com>

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

.. _changelog: https://github.com/instacart/cwam/blob/master/HISTORY.rst
.. _Quentin Rousseau: https://github.com/kwent

.. |pypi| image:: https://img.shields.io/pypi/v/cwam.svg
   :target: https://pypi.python.org/pypi/cwam
.. |travis| image:: https://img.shields.io/travis/instacart/cwam.svg
   :target: https://travis-ci.org/instacart/cwam
.. |doc| image:: https://readthedocs.org/projects/cwam/badge/?version=latest
   :target: https://cwam.readthedocs.io/en/latest/?badge=latest
.. |pyup| image:: https://pyup.io/repos/github/instacart/cwam/shield.svg
   :target: https://pyup.io/repos/github/instacart/cwam/
