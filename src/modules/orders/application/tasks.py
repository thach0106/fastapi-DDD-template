from src.core.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="src.modules.orders.application.tasks.process_order_created")
def process_order_created(event_payload: dict):
    """
    Example event handler triggered asynchronously.
    """
    order_id = event_payload.get("order_id")
    logger.info(f"PROCESSING ASYNC EVENT: Order {order_id} created. Sending email...")
    # Logic: Send email, update analytics, etc.
