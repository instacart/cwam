===============================
CloudWatch Alarms Manager
===============================

|pypi| |travis| |doc| |pyup|

Easy way to create default CloudWatch Alarms.

Installation
------------

Install using pip:

.. code:: bash

    $ pip install cwam

Requirements
------------

- Python 2.6, 2.7, 3.3, 3.4, or 3.5
- A AWS account

CLI
---

CLI Authentication
~~~~~~~~~~~~~~~~~~

Via environment variables:

.. code:: bash

    $ export AWS_ACCESS_KEY_ID="aws_access_key_id"
    $ export AWS_SECRET_ACCESS_KEY="aws_access_secret_key"
    $ export AWS_DEFAULT_REGION="us-east-1"
    $ cwam elb list

Via implicit ~/cwam/conf.yml:

Edit ~/.cwam/conf.yml

.. code:: yaml
  aws:
    aws_access_key_id: aws_access_key_id
    aws_access_secret_key: aws_access_secret_key
    aws_default_region: aws_default_region

.. code:: bash

    $ cwam elb create

Via (--conf/-c) option:

.. code:: bash

    $ cwam --conf /path/to/config elb create

Via option:

.. code:: bash

    $ cwam ----aws-access-key-id aws_access_key_id \
    --aws-access-secret-key aws_access_secret_key \
    --aws_default_region us-east-1 elb create

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
      -r, --aws_default_region TEXT   AWS Region.
      -c, --conf TEXT                 Path to config
                                      (~/.cwam/conf.yml).
      --version                       Show the version and exit.
      -h, --help                      Show this message and exit.

    Commands:
      elb

ELB
~~~~~~~~

.. code:: plain

    Usage: cwam elb [OPTIONS] COMMAND [ARGS]...

    Options:
      -h, --help  Show this message and exit.

    Commands:
      create         Create alarms configured in --conf file
      list           List ELB.
      local-alarms   List alarms configured in --conf file
      remote-alarms  List alarms configured on AWS

Examples:

.. code:: bash

    $ cwam elb create

RDS
~~~~~~~~

.. code:: plain

    Usage: cwam rds [OPTIONS] COMMAND [ARGS]...

    Options:
      -h, --help  Show this message and exit.

    Commands:
      create         Create alarms configured in --conf file
      list           List RDS.
      local-alarms   List alarms configured in --conf file
      remote-alarms  List alarms configured on AWS

Examples:

.. code:: bash

    $ cwam rds create

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

    Copyright (c) 2017 Instacart <quentin@instacart.com>

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
.. _Quentin Rousseau: https://github.com/instacart

.. |pypi| image:: https://img.shields.io/pypi/v/cwam.svg
   :target: https://pypi.python.org/pypi/cwam
.. |travis| image:: https://img.shields.io/travis/instacart/cwam.svg
   :target: https://travis-ci.org/instacart/cwam
.. |doc| image:: https://readthedocs.org/projects/cwam/badge/?version=latest
   :target: https://cwam.readthedocs.io/en/latest/?badge=latest
.. |pyup| image:: https://pyup.io/repos/github/instacart/cwam/shield.svg
   :target: https://pyup.io/repos/github/instacart/cwam/
