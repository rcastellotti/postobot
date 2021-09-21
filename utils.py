import logging.config


def get_logger(filename):
  logging.config.dictConfig({
      "version": 1,
      "disable_existing_loggers": False,
      "formatters": {
          "default": {
              "format": "%(asctime)s [PID %(process)d] [Thread %(thread)d] [%(levelname)s] [%(name)s] %(message)s"
          }
      },
      "handlers": {
          "file": {
              "class": "logging.FileHandler",
              "level": "INFO",
              "formatter": "default",
              "filename": f"{filename}.log",
              "mode": "w"
          }
      },
      "root": {
          "level": "INFO",
          "handlers": [
              "file"
          ]
      }
  })
  return logging.getLogger()
