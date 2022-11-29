import os
from tempfile import mkdtemp

# Set file Upload Folder and make a directory if doesn't exist
path = os.getcwd()
uploadfolder = os.path.join(path, 'static\\uploads')
if not os.path.isdir(uploadfolder):
    os.mkdir(uploadfolder)
UPLOAD_FOLDER = uploadfolder


# Ensure templates are auto-reloaded
EXPLAIN_TEMPLATE_LOADING = True
TEMPLATES_AUTO_RELOAD = True
ENV = 'development'
DEBUG = True

# Configure session to use filesystem (instead of signed cookies)
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = True
SESSION_TYPE = "filesystem"