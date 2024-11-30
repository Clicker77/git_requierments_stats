import logging
from app.celery.tasks import CeleryTasks
from app.config import Config
from app.models.project import Project
from app.models.requirement import Requirement
from app.database import db
from app.services.github_service import GithubClient, GithubRepo

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def start_scarping(num_repos: int = 5) -> None:
    github_service = GithubClient(Config.GITHUB_TOKEN)
    popular_repos = github_service.get_popular_repos(number=num_repos, language="Python")
    for repo_name in popular_repos:
        CeleryTasks.scrape_github_task.delay(repo_name)


def scrape_github_task(project_name: str) -> str:
    """
    Scrape GitHub repository for requirements and create project.
    """
    github_service = GithubClient(Config.GITHUB_TOKEN)
    archive_url = github_service.fetch_repo_archive_url(project_name)
    github_repo = GithubRepo(archive_url=archive_url, token=Config.GITHUB_TOKEN)
    values = github_repo.get_python_req_file_single_api()
    if not values:
        return f"Task: {project_name} without requirements file!"
    requirements_list = values.split('\n')
    validated_requirements = [
        line.split('==', 1) if '==' in line else [line, '']
        for line in requirements_list
    ]
    requirements_dict = {key: value for key, value in validated_requirements}
    create_project_with_requirements(project_name, requirements_dict)
    return f"Task: {project_name} completed successfully!"


def create_project_with_requirements(project_name: str, requirements_dict: dict) -> Project:
    """
    Create a new project and attach requirements with their versions.
    """
    # Input validation
    if not project_name or not project_name.strip():
        raise ValueError("Project name cannot be empty")
    if not isinstance(requirements_dict, dict):
        raise ValueError("Requiremnts must be provided as a dictionary")

    try:
        project = add_project_if_not_exist(project_name)
        add_requirement_if_not_exist(requirements_dict, project)
        logging.info(f"Project '{project_name}' created successfully with ID: {project.id}")
        return project

    except Exception as e:
        logging.error(f"Failed to create project '{project_name}': {str(e)}")
        db.session.rollback()
        raise Exception(f"Failed to create project: {str(e)}")


def add_project_if_not_exist(project_name: str) -> Project:
    """
    Add a project if it does not exist.
    """
    project = Project.query.filter_by(name=project_name).first()
    if not project:
        project = Project(name=project_name)
        db.session.add(project)
        logging.info(f"Creating new project: {project_name}")
        db.session.commit()

    return project

def add_requirement_if_not_exist(requirements_dict: dict, project: Project) -> None:
    """
    Add requirements to the project if they do not exist.
    """
    for req_name, version in requirements_dict.items():
        if not req_name:
            continue
        requirement = db.session.query(Requirement).filter(
            Requirement.name == req_name,
            Requirement.version == version
        ).first()
        if not requirement:
            logging.info(f"Creating new requirement: {req_name}=={version}")
            requirement = Requirement(name=req_name, version=version)
            db.session.add(requirement)
        project.add_requirement(requirement)
    db.session.commit()
