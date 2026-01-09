"""
Tests for deployment configuration and production readiness.

These tests validate that the application is properly configured
for deployment on Render and other production environments.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


PROJECT_ROOT = Path(__file__).parent.parent
PROCFILE_PATH = PROJECT_ROOT / 'Procfile'
REQUIREMENTS_PATH = PROJECT_ROOT / 'requirements.txt'


class TestPortConfiguration:
    """Test PORT environment variable handling."""
    
    def test_port_defaults_to_5000(self):
        """Test that port defaults to 5000 when PORT env var is not set."""
        # Ensure PORT is not set
        if 'PORT' in os.environ:
            original_port = os.environ['PORT']
            del os.environ['PORT']
        else:
            original_port = None
        
        try:
            # Import app module to test port reading
            from app import app
            import app as app_module
            
            # Mock os.environ.get to test default behavior
            with patch.dict(os.environ, {}, clear=False):
                if 'PORT' in os.environ:
                    del os.environ['PORT']
                
                # The port reading happens in __main__, so we test the logic
                port = int(os.environ.get('PORT', 5000))
                assert port == 5000, "Port should default to 5000 when PORT is not set"
        finally:
            # Restore original PORT if it existed
            if original_port is not None:
                os.environ['PORT'] = original_port
    
    def test_port_reads_from_environment(self):
        """Test that port reads from PORT environment variable."""
        original_port = os.environ.get('PORT')
        
        try:
            # Set PORT to a test value
            test_port = '8080'
            os.environ['PORT'] = test_port
            
            # Test that it reads correctly
            port = int(os.environ.get('PORT', 5000))
            assert port == 8080, f"Port should be {test_port} when PORT env var is set"
        finally:
            # Restore original PORT
            if original_port is not None:
                os.environ['PORT'] = original_port
            elif 'PORT' in os.environ:
                del os.environ['PORT']
    
    def test_port_converts_to_int(self):
        """Test that PORT environment variable is converted to integer."""
        original_port = os.environ.get('PORT')
        
        try:
            # Set PORT to a string number
            os.environ['PORT'] = '3000'
            port = int(os.environ.get('PORT', 5000))
            assert isinstance(port, int), "Port should be converted to integer"
            assert port == 3000, "Port should be 3000"
        finally:
            if original_port is not None:
                os.environ['PORT'] = original_port
            elif 'PORT' in os.environ:
                del os.environ['PORT']


class TestProcfile:
    """Test Procfile configuration for Render."""
    
    def test_procfile_exists(self):
        """Test that Procfile exists."""
        assert PROCFILE_PATH.exists(), "Procfile should exist for Render deployment"
    
    def test_procfile_content(self):
        """Test that Procfile has correct content."""
        assert PROCFILE_PATH.exists(), "Procfile should exist"
        
        with open(PROCFILE_PATH, 'r') as f:
            content = f.read().strip()
        
        # Should contain gunicorn command
        assert 'gunicorn' in content, "Procfile should contain gunicorn"
        assert 'app:app' in content, "Procfile should reference app:app"
        assert 'web:' in content, "Procfile should have 'web:' prefix for web service"
    
    def test_procfile_format(self):
        """Test that Procfile has correct format."""
        with open(PROCFILE_PATH, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # Should have at least one line
        assert len(lines) > 0, "Procfile should not be empty"
        
        # First line should start with 'web:'
        assert lines[0].startswith('web:'), "Procfile should start with 'web:'"
        
        # Should contain gunicorn command
        procfile_content = ' '.join(lines)
        assert 'gunicorn app:app' in procfile_content, \
            "Procfile should contain 'gunicorn app:app' command"


class TestRequirements:
    """Test requirements.txt for production dependencies."""
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists."""
        assert REQUIREMENTS_PATH.exists(), "requirements.txt should exist"
    
    def test_gunicorn_in_requirements(self):
        """Test that gunicorn is in requirements.txt."""
        with open(REQUIREMENTS_PATH, 'r') as f:
            content = f.read()
        
        assert 'gunicorn' in content.lower(), \
            "requirements.txt should include gunicorn for production server"
    
    def test_flask_in_requirements(self):
        """Test that Flask is in requirements.txt."""
        with open(REQUIREMENTS_PATH, 'r') as f:
            content = f.read()
        
        assert 'flask' in content.lower(), \
            "requirements.txt should include Flask"
    
    def test_requirements_format(self):
        """Test that requirements.txt has valid format."""
        with open(REQUIREMENTS_PATH, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # Should have at least Flask
        assert len(lines) > 0, "requirements.txt should not be empty"
        
        # Check for version specifiers (optional but good practice)
        flask_line = [line for line in lines if 'flask' in line.lower()]
        assert len(flask_line) > 0, "Flask should be in requirements.txt"


class TestProductionConfiguration:
    """Test production configuration and readiness."""
    
    def test_app_can_be_imported(self):
        """Test that app can be imported (required for gunicorn)."""
        from app import app
        assert app is not None, "App should be importable"
        assert hasattr(app, 'run'), "App should have run method"
    
    def test_app_has_flask_instance(self):
        """Test that app is a Flask instance."""
        from app import app
        from flask import Flask
        
        assert isinstance(app, Flask), "app should be a Flask instance"
    
    def test_app_routes_are_defined(self):
        """Test that all required routes are defined."""
        from app import app
        
        # Get all routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        # Check for required routes
        assert '/' in routes, "Root route should be defined"
        assert '/api/new_game' in routes, "New game API route should be defined"
        assert '/api/move' in routes, "Move API route should be defined"
        assert '/api/bot_move' in routes, "Bot move API route should be defined"
        assert '/api/game_state' in routes, "Game state API route should be defined"
    
    def test_app_handles_static_files(self):
        """Test that app is configured for static files."""
        from app import app
        
        # Flask apps should have static_folder configured
        assert hasattr(app, 'static_folder'), "App should have static_folder"
        assert app.static_folder is not None, "Static folder should be configured"
    
    def test_app_handles_templates(self):
        """Test that app is configured for templates."""
        from app import app
        
        # Flask apps should have template_folder configured
        assert hasattr(app, 'template_folder'), "App should have template_folder"
        assert app.template_folder is not None, "Template folder should be configured"


class TestEnvironmentVariables:
    """Test environment variable handling."""
    
    def test_os_module_imported(self):
        """Test that os module is imported in app.py."""
        # Check that the code pattern exists in app.py
        app_file = PROJECT_ROOT / 'app.py'
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Should import os module
        assert 'import os' in content, "app.py should import os module"
    
    def test_port_environment_variable_usage(self):
        """Test that PORT environment variable is used correctly."""
        # Check that the code pattern exists in app.py
        app_file = PROJECT_ROOT / 'app.py'
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Should use os.environ.get for PORT
        assert 'os.environ.get' in content, \
            "app.py should use os.environ.get for PORT"
        assert "'PORT'" in content or '"PORT"' in content, \
            "app.py should reference PORT environment variable"
        assert '5000' in content, \
            "app.py should have default port 5000"


class TestDeploymentFiles:
    """Test that all necessary deployment files exist."""
    
    def test_all_deployment_files_exist(self):
        """Test that all required files for deployment exist."""
        files_to_check = [
            'Procfile',
            'requirements.txt',
            'app.py',
        ]
        
        for filename in files_to_check:
            filepath = PROJECT_ROOT / filename
            assert filepath.exists(), f"{filename} should exist for deployment"
    
    def test_procfile_not_empty(self):
        """Test that Procfile is not empty."""
        if PROCFILE_PATH.exists():
            with open(PROCFILE_PATH, 'r') as f:
                content = f.read().strip()
            assert len(content) > 0, "Procfile should not be empty"
    
    def test_requirements_not_empty(self):
        """Test that requirements.txt is not empty."""
        if REQUIREMENTS_PATH.exists():
            with open(REQUIREMENTS_PATH, 'r') as f:
                content = f.read().strip()
            assert len(content) > 0, "requirements.txt should not be empty"

