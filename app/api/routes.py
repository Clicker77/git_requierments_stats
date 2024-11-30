from flask import Blueprint, jsonify, request
from app.models.project import Project
from app.services.project_services import start_scarping


api = Blueprint('api', __name__)
__cached__ = {}

@api.route('/scrape', methods=['POST'])
def scrape_repositories():
    """Trigger the scraping process for Python repositories"""
    try:
        data = request.get_json()
        num_repos = data.get('num_repos', 5)
        start_scarping(num_repos)
        return jsonify({
            'status': 'success',
            'message': f'Started scraping {num_repos} repositories',
        }), 202
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/project/<path:name>', methods=['GET'])
def get_project(name):
    """Get requirements for a specific project"""
    try:
        if name in __cached__:
            project = __cached__[name]
        else:
            project = Project.query.filter_by(name=name).first()
            if project:
                __cached__[name] = project
        
        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
            
        requirements = [
            {'name': req.name, 'version': req.version}
            for req in project.requirements
        ]
        
        return jsonify({
            'status': 'success',
            'project': {
                'name': project.name,
                'last_update': project.last_update_date.isoformat(),
                'requirements': requirements
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    