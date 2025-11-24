import json
import pika
from pika.exceptions import AMQPConnectionError, StreamLostError

from src.main.python.events.GameEvent import GameEvent


class GameBcPublisher:
    """
    Publishes game events to the GameBC (Spring) via RabbitMQ.
    """

    def __init__(
            self,
            amqp_url: str,
            exchange: str = "game-events",
            routing_key: str = "tictactoe.state"
    ):
        self.amqp_url = amqp_url
        self.exchange = exchange
        self.routing_key = routing_key

        self.connection = None
        self.channel = None


    def _ensure_connection(self):
        if self.connection and self.connection.is_open:
            return

        try:
            params = pika.URLParameters(self.amqp_url)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()

            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type="topic",
                durable=True
            )

            print("RabbitMQ connected for GameBC publishing.")

        except AMQPConnectionError as e:
            print(f"[RabbitMQ] Connection failed: {e}")
            raise
        except Exception as e:
            print(f"[RabbitMQ] Unexpected error: {e}")
            raise

    # --------------------------------------------------------
    # PUBLISHER
    # --------------------------------------------------------
    def publish_state(self, event: GameEvent):
        """
        Publish the game event to RabbitMQ.
        Automatically reconnects if connection was lost.
        """
        payload = event.to_dict()
        print("[GAME BC EVENT]", payload)

        try:
            # Ensure connection
            self._ensure_connection()

            # Send message
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=json.dumps(payload).encode("utf-8"),
                properties=pika.BasicProperties(delivery_mode=2),
            )

        except (AMQPConnectionError, StreamLostError):
            print("[RabbitMQ] Lost connection. Reconnecting...")
            self.connection = None
            self.channel = None

            # Try again once
            self._ensure_connection()

            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=json.dumps(payload).encode("utf-8"),
                properties=pika.BasicProperties(delivery_mode=2),
            )

        except Exception as e:
            print(f"[RabbitMQ] Failed to publish message: {e}")
