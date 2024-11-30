from app import celery_app

class CeleryTasks:
    @staticmethod
    @celery_app.task
    def scrape_github_task(repo_name):
        from app.services.project_services import scrape_github_task
        scrape_github_task(repo_name)