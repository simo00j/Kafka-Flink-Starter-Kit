from dataclasses import asdict, dataclass, field
from typing import List, Tuple
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from jinja2 import Environment, FileSystemLoader



# Dependency JARs for Kafka and PostgreSQL connectors
REQUIRED_JARS = [
    "file:///opt/flink/flink-sql-connector-kafka-1.17.0.jar",
    "file:///opt/flink/flink-connector-jdbc-3.0.0-1.16.jar",
    "file:///opt/flink/postgresql-42.6.0.jar",
]
@dataclass(frozen=True)
class StreamJobConfig:
    job_name: str = 'flink_job'
    jars: List[str] = field(default_factory=lambda: REQUIRED_JARS)
    checkpoint_interval: int = 10
    checkpoint_pause: int = 5
    checkpoint_timeout: int = 60
    parallelism: int =1  # Adjust based on available slots



@dataclass(frozen=True)
class KafkaConfig:
    connector: str = 'kafka'
    bootstrap_servers: str = 'kafka-broker-1:9092'
    scan_startup_mode: str = 'earliest-offset'
    consumer_group_id: str = 'flink-consumer-group-1'
    format: str = 'json'


@dataclass(frozen=True)
class UserEventsTopicConfig(KafkaConfig):
    topic: str = 'user_events'


@dataclass(frozen=True)
class CheckoutEventsTopicConfig(KafkaConfig):
    topic: str = 'checkout_events'


@dataclass(frozen=True)
class NotificationsTopicConfig(KafkaConfig):
    topic: str = 'notifications'


@dataclass(frozen=True)
class ProcessedEventsKafkaSinkConfig(KafkaConfig):
    topic: str = 'processed_events'

@dataclass(frozen=True)
class PostgreSQLConfig:
    connector: str = 'jdbc'
    url: str = 'jdbc:postgresql://postgres:5432/postgres'
    table_name: str = ''
    username: str = 'postgres'
    password: str = 'postgres'
    driver: str = 'org.postgresql.Driver'

@dataclass(frozen=True)
class ProcessedEventsPostgresSinkConfig(PostgreSQLConfig):
    table_name: str = 'processed_events'

@dataclass(frozen=True)
class UpdatesTopicConfig(KafkaConfig):
    topic: str = 'updates'
    consumer_group_id: str = 'flink-updates-consumer-group'  # Unique group ID


@dataclass(frozen=True)
class ProductsPostgresSinkConfig(PostgreSQLConfig):
    table_name: str = 'products'





def get_execution_environment(
    config: StreamJobConfig,
) -> Tuple[StreamExecutionEnvironment, StreamTableEnvironment]:
    s_env = StreamExecutionEnvironment.get_execution_environment()
    for jar in config.jars:
        s_env.add_jars(jar)
    # Start a checkpoint every 10,000 ms (10 s)
    s_env.enable_checkpointing(config.checkpoint_interval * 1000)
    # Ensure 5,000 ms (5 s) of progress between checkpoints
    s_env.get_checkpoint_config().set_min_pause_between_checkpoints(
        config.checkpoint_pause * 1000
    )
    # Checkpoints have to complete within 60 seconds
    s_env.get_checkpoint_config().set_checkpoint_timeout(
        config.checkpoint_timeout * 1000
    )
    execution_config = s_env.get_config()
    execution_config.set_parallelism(config.parallelism)
    t_env = StreamTableEnvironment.create(s_env)
    job_config = t_env.get_config().get_configuration()
    job_config.set_string("pipeline.name", config.job_name)
    return s_env, t_env

def get_sql_query(
    entity: str,
    query_type: str = 'source',
    template_env: Environment = Environment(loader=FileSystemLoader("/opt/flink/code/microservices/flink_app/"))
) -> str:
    config_map = {
        'user_events': UserEventsTopicConfig(),
        'checkout_events': CheckoutEventsTopicConfig(),
        'updates': UpdatesTopicConfig(),
        'notifications': NotificationsTopicConfig(),
        'user_profiles': PostgreSQLConfig(table_name='users'),
        'processed_events_kafka': ProcessedEventsKafkaSinkConfig(),
        'processed_events_postgres': ProcessedEventsPostgresSinkConfig(),
        'products': ProductsPostgresSinkConfig(), 
    }

    config = config_map.get(entity)
    if config is not None:
        config_dict = asdict(config)
    else:
        config_dict = {}  # Use an empty dictionary if config is None

    return template_env.get_template(f"{query_type}/{entity}.sql").render(
        **config_dict
    )

