import os

try:
    ENV = os.environ['RUNTIME_ENV']
except KeyError:
    ENV = 'dev'

if ENV == 'prod':
    from .prod import *
else:
    from .dev import *

