from celery import Celery
from celery.schedules import crontab

from core.settings import settings

app = Celery(
    __name__,
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    include=["apps.users.tasks"],
    timezone=settings.TIMEZONE,
)

app.conf.beat_schedule = {
    "delete-unverified-users-every-10-seconds": {
        "task": "apps.users.tasks.delete_unverified_users",
        "schedule": crontab(hour=0, minute=0),  # yarim kechasi UZB vaqti
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
