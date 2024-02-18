# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: run

# import debugpy
# debugpy.listen(('localhost', 5678))
# debugpy.wait_for_client()

import os
import config

from utils import path_helper
path_helper.set_exec_file(__file__)

from dotenv import load_dotenv
load_dotenv(path_helper.get_path('.flaskenv'))
load_dotenv()

from ts_common.external_libs.pyhelper.utils.logging_helper import init_logging

LOG_FILE = os.environ.get('TS_LOG_FILE', 'output.log')
LOG_LEVEL = os.environ.get('TS_LOG_LEVEL', 'DEBUG')
init_logging(LOG_FILE, LOG_LEVEL)


from app import create_app, db
app = create_app(config)


# csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()


@app.shell_context_processor
def make_shell_context():
    from app.models import User
    return {'db': db, 'User': User}


if __name__ == '__main__':
    app.run(debug=True)