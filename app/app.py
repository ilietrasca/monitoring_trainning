try:
	import random
	import time
	import os
	import logging
	import sys
	import unittest
	from prometheus_client import start_http_server
	from prometheus_client.openmetrics.exposition import generate_latest
	from prometheus_client import Counter, Summary, Gauge, Histogram, Enum 
except ImportError:
    print("could not load needed modules, exiting_transaction...")
    sys_transaction.exit(2)
		
__version__ = "0.7"

metrics_port= os.environ.get("METRICS_PORT", 8001)

log_levels = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20, "DEBUG": 10, "NOTSET": 0}
log_level_name = os.environ.get("LOG_LEVEL", "INFO")
log_level = log_levels[log_level_name]
log_fmt = "[%(asctime)s] [%(levelname)s] %(message)s"

logging.basicConfig(level = log_level, datefmt = "%Y-%m-%d %H:%M:%S %z", format = log_fmt)
logging.info("Starting program version {0}".format(__version__))
logging.info("Using log level {0}".format(log_level_name))


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorate function with metric_transaction.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)
    g_transaction.labels(method='POST',operation='transaction').inc()
    g_enroll.labels(method='POST',operation='enrollment').inc()
#set the curent timi for last seen metrics 
    g_transaction_last_seen.labels(method='POST',operation='transaction').set_to_current_time()
    g_enroll_last_seen.labels(method='POST',operation='enrollment').set_to_current_time()
    if t < 0.5 : 
        c_transaction.labels(method='POST', outcome='SUCCESS',operation='transaction').inc()
#        c_err.labels(method='POST', outcome='SUCCESS').inc()

    else:
#        c_transaction.labels(method='POST', outcome='ERROR').inc()
        c_err.labels(method='POST', outcome='ERROR',error_code='TIME-OUT',operation='transaction').inc()

    if t < 0.5 : 
        c_enroll.labels(method='POST', outcome='SUCCESS',operation='enrollment').inc()

    else:
        c_enroll_err.labels(method='POST', outcome='ERROR',error_code='TIME-OUT',operation='enrollment').inc()




    s_transaction.labels(method='POST').observe(t)
    h_transaction.labels(method='POST',operation='transaction').observe(t)
    s_enroll.labels(method='POST').observe(t)
    h_enroll.labels(method='POST',operation='enrollment').observe(t)

#from prometheus_client import Counter    
c_transaction = Counter('transactions', 'Number of transactions',['method','outcome','operation'])
c_err = Counter('transactions_failed', 'Number of failed transactions',['method','outcome','error_code','operation'])

c_enroll = Counter('enrollments', 'Number of enrollments',['method','outcome','operation'])
c_enroll_err = Counter('enrollments_failed', 'Number of failed enrollments',['method','outcome','error_code','operation'])

#c_transaction.inc()     # Increment by 1
#c_transaction.inc(1.6)  # Increment by given value
c_transaction.labels(method='POST', outcome='SUCCESS',operation='transaction').inc()

@c_transaction.count_exceptions()

def f():
  pass

with c_transaction.count_exceptions():
  pass

# Count only one type of exception
with c_transaction.count_exceptions(ValueError):
  pass

#from prometheus_client import Gauge
g_transaction = Gauge('transaction_my_inprogress', 'Number of in_progress transactions ',['method','operation'])
g_enroll = Gauge('enrollment_my_inprogress', 'Number of in_progress transactions ',['method','operation'])

g_transaction.labels(method='POST',operation='transaction').inc()      # Increment by 1
#g_transaction.dec(10)    # Decrement by given value
#g_transaction.set(4.2)   # Set to a given value


g_transaction.labels(method='POST',operation='transaction').set_to_current_time()   # Set to current unixtime

# Increment when entered, decrement when exited.
@g_transaction.track_inprogress()
def f():
  pass

with g_transaction.labels(method='POST',operation='transaction').track_inprogress():
  pass

#from prometheus_client import Summary
s_transaction = Summary('transaction_latency_seconds', 'Transaction latency in milliseconds',['method'])
s_enroll = Summary('enrollment_latency_seconds', 'Transaction latency in milliseconds',['method'])

#s_transaction.observe(4.7)    # Observe 4.7 (seconds in this case)

@s_transaction.time()
def f():
  pass

with s_transaction.labels(method='POST').time():
  pass

  
#from prometheus_client import Histogram
h_transaction = Histogram('transaction_histogram_latency_seconds', 'Transaction latency histogram',['method','operation'])
h_enroll = Histogram('enrollment_histogram_latency_seconds', 'Transaction latency histogram',['method','operation'])

#h_transaction.observe(6.9)    # Observe 4.7 (seconds in this case)	
#h_transaction.observe(2.1) 
#h_transaction.observe(0.5) 
#h_transaction.observe(1) 
#h_transaction.observe(0.5) 
#h_transaction.observe(1.1) 
#h_transaction.observe(13.2) 


@h_transaction.time()
def f():
  pass

with h_transaction.labels(method='POST',operation='transaction').time():
  pass


#from prometheus_client import Enum
e = Enum('app_status', 'Application status ',
        states=['starting', 'running', 'stopped'])
e.state('running')
  
#
g_transaction_last_seen = Gauge('transaction_last_seen', 'last seen transactions ',['method','operation'])
g_enroll_last_seen = Gauge('enroll_last_seen', 'last seen enroll ',['method','operation'])






# start the http server to expose the prometheus metrics
logging.info("Starting web-server...")
start_http_server(metrics_port, "0.0.0.0")
logging.info("Server started and listening at 0.0.0.0:{0}".format(metrics_port))
  
if __name__ == '__main__':
#	main()
	while True:
#		process_request(random.uniform(0.1, 20.0))
		process_request(random.random())
