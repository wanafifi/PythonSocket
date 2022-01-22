import logging
file = open("loginfo.log", "a")
file.close()

logging.basicConfig(filename='loginfo.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s\n\n')
logger=logging.getLogger(__name__)

a = 5
b = 0
try:
  c = a / b
except Exception as e:
    file = open("loginfo.log", "a")
    logger.error(e)
    file.write("Aiyaaaaaa::::" + str(e))
    # error_msg = logging.exception("Exception occurred")
    file.close()