from waitress import serve
import logging
from yourapp import *

logger=logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    serve(app, listen='0.0.0.0:80')
