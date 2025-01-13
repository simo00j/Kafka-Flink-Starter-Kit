import os

class AdminConfig:
    def __init__(self):
        self.bootstrap_servers = os.getenv('ADMIN_BOOTSTRAP_SERVERS', 'kafka-broker-1:9092')


admin_config = AdminConfig()