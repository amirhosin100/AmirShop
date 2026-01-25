bind = "0.0.0.0:8000"
workers = 3
loglevel = "info"
accesslog = "-"      # stdout
errorlog = "-"       # stdout
capture_output = True
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"'
