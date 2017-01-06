
import colorlog


class AppLogger:

    @staticmethod
    def get_logger(name):
        """
            Set up a logger.
        """

        logger = colorlog.getLogger(name)
        logger.setLevel(colorlog.colorlog.logging.DEBUG)

        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter())
        logger.addHandler(handler)

        return logger
