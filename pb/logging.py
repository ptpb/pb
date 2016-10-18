import watchtower
import logging


logging.basicConfig(level=logging.DEBUG)


def init_logging(app):
    handler = watchtower.CloudWatchLogHandler(
        log_group = 'pb-app',
        stream_name = 'pb'
    )

    app.logger.addHandler(handler)
    logging.getLogger("werkzeug").addHandler(handler)
