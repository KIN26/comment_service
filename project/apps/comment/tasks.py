from project.celery import app
from .models import CommentsReport
from .notify import send_report_notification
from .utils import create_report_file


@app.task(bind=True, ignore_results=True)
def get_report_file(self, report_id):
    report = CommentsReport.objects.get(pk=report_id)
    create_report_file(report)
    report.created = True
    report.save()
    send_report_notification(report.user_id, report.id)
