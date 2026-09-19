import os
import sys

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gala_project.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application
