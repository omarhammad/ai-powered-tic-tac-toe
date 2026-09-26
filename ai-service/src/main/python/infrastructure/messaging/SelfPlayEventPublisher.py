import json
import pika


class SelfPlayEventPublisher:

    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.exchange = "ml.logs"
        self.routing_key = "ml.tictactoe.self_play_run.completed"

        params = pika.URLParameters(amqp_url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        # Ensure exchange exists
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type="topic",
            durable=True
        )

    def publish_completion_event(self, total_games: int):
        """
        Sends a small JSON event that Spring Boot will listen to.
        """
        payload = {
            "message": "Self-play run completed",
            "gamesGenerated": total_games
        }

        body = json.dumps(payload).encode("utf-8")

        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        print(f"[EVENT] Published self-play completion event → {self.routing_key}")

    def close(self):
        try:
            self.connection.close()
        except Exception:
            pass
