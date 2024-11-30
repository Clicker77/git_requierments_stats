import requests
from github import Github
import tarfile
import io


class GithubClientException(Exception):
    pass


class GithubClient:
    """
    Object for connecting to github and querying data
    """

    def __init__(self, token):
        self.client = Github(token)

    def get_popular_repos(self, number, language):
        """
        Get a list of the most popular repositories for the given language from Github
        """
        repos = self.client.search_repositories(query='language:{}'.format(language))[:number]
        return [repo.full_name for repo in repos]
        # return ', '.join(map(lambda repo: repo.full_name, repos))

    def _fetch_repo_raw_data(self, repo_name):
        try:
            repo_raw_data = self.client.get_repo(repo_name)
        except Exception as e:
            raise GithubClientException("Caught exception when fetching repo {}, "
                                        "exception details: {}".format(repo_name, e))
        return repo_raw_data

    def fetch_repo_archive_url(self, repo_name):
        """
        Get the archive URL for the given repository name.
        """
        repo_raw_data = self._fetch_repo_raw_data(repo_name)
        return repo_raw_data.archive_url.replace("{archive_format}{/ref}", "tarball")


class GithubRepo:

    def __init__(self, archive_url, token):
        self.archive_url = archive_url
        self.token = token

        # Returns tar.gz in the response body
        res = requests.get(archive_url, params={"Authorization": "token token".format(self.token)})
        file_like_data = io.BytesIO(res.content)
        self.tar_obj = tarfile.open(name=None, mode='r:gz', fileobj=file_like_data, bufsize=10240)
        self.repo_contents = self.tar_obj.getnames()

    def get_python_req_file_single_api(self):
        """
        Get the contents of the requirements.txt file for the repository
        """
        req_file = [item for item in self.repo_contents if 'requirements.txt' in item]
        if not req_file:
            return None
        else:
            return self.tar_obj.extractfile(req_file[0]).read().decode("utf-8")


