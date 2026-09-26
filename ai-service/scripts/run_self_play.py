import argparse
import sys
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src" / "main" / "python"))

from services.SelfPlayService import SelfPlayService
from services.AiService import AIService
from infrastructure.logging.LoggingClient import LoggingClient
from infrastructure.messaging.SelfPlayEventPublisher import SelfPlayEventPublisher

# docker exec -it container_id python scripts/run_self_play.py
def parse_args():
    parser = argparse.ArgumentParser(
        description="Run AI self-play games to generate ML training data."
    )

    parser.add_argument(
        "--games",
        type=int,
        default=int(os.getenv("SELFPLAY_GAMES", 1)),
        help="Number of self-play games to generate."
    )

    parser.add_argument(
        "--noise",
        type=float,
        default=float(os.getenv("SELFPLAY_NOISE", 0.1)),
        help="Exploration noise ratio (0.0 - 1.0). Default: 0.15"
    )

    parser.add_argument(
        "--amqp-url",
        type=str,
        default=os.getenv("AMQP_URL", "amqp://user:password@localhost:5671/"),
        help="RabbitMQ connection URL."
    )

    return parser.parse_args()


def main():
    args = parse_args()

    print("\n===============================")
    print("  AI SELF-PLAY DATA GENERATOR  ")
    print("===============================\n")
    print(f"Games to generate: {args.games}")
    print(f"Exploration noise: {args.noise}")
    print("\nStarting...\n")

    # Initialize services
    ai_service = AIService()
    logger = LoggingClient(amqp_url=args.amqp_url)
    self_play_service = SelfPlayService(
        ai_service=ai_service,
        logging_client=logger,
        exploration_noise=args.noise
    )

    # Run the data generation
    self_play_service.generate_self_play_dataset(num_games=args.games)

    print("\n--------------------------------")
    print(" Self-play dataset generation finished.")
    print(" Publishing completion event...")
    print("--------------------------------\n")

    # Publish completion event
    event_publisher = SelfPlayEventPublisher(amqp_url=args.amqp_url)
    event_publisher.publish_completion_event(total_games=args.games)
    event_publisher.close()

    print("[DONE] Self-play run completed event sent.\n")


if __name__ == "__main__":
    main()
