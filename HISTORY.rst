=======
History
=======

1.0.0 (2018-05-17)
------------------

* First release on PyPI.


2.0 (2018-10-09)
----------------
* Fix bugs casued by references to elaticache not being uniform (elastic_cache, elasticaches, etc.)

* Stop modifying CPUUtilization metric for redis elasticache alarms as this behavior was obscure to the user.
    * Before, application would divide set CPU threshold by number of cores to get an approximation of CPU use by single-threaded redis process.  Now EngineCPUUtilization is available, which give exact CPU use by redis, so obscured modification of configured thresholds makes even less sense.
    * See amazon recomendations here: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/CacheMetrics.WhichShouldIMonitor.html
