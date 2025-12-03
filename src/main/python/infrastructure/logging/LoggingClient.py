import json
import pika


class LoggingClient:
    """
    Publishes game state logs to RabbitMQ instead of HTTP.

    Exchange: ml.logs
    Routing Key: ml.tictactoe.state
    """

    def __init__(
            self,
            amqp_url: str,
            exchange: str = "ml.logs",
            routing_key: str = "ml.tictactoe.state"
    ):
        self.amqp_url = amqp_url
        self.exchange = exchange
        self.routing_key = routing_key

        # Establish connection
        params = pika.URLParameters(self.amqp_url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        # Ensure exchange exists
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type="topic",
            durable=True
        )

    def log_game_state(self, game_state_dict: dict) -> None:
        """
        Publish GameState row to RabbitMQ as JSON message.
        """

        try:
            message = json.dumps(game_state_dict)

            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=message.encode("utf-8"),
                properties=pika.BasicProperties(
                    delivery_mode=2  # persistent message
                )
            )

        except Exception as e:
            print(f"[ML LOGGING ERROR] Failed to publish message: {e}")
