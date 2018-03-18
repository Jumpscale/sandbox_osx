from colorlog import ColoredFormatter

class LimitFormater(ColoredFormatter):

    def __init__(self, fmt, datefmt, reset, log_colors, secondary_log_colors, style, lenght):
        super(LimitFormater, self).__init__(
            fmt=fmt,
            datefmt=datefmt,
            reset=reset,
            log_colors=log_colors,
            secondary_log_colors=secondary_log_colors,
            style=style)
        self.lenght = lenght

    def format(self, record):
        if len(record.pathname) > self.lenght:
            record.pathname = "..." + record.pathname[-self.lenght:]
        return super(LimitFormater, self).format(record)
