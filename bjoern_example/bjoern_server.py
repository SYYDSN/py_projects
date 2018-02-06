#  -*- coding: utf-8 -*-
from flask_server import app
import bjoern

"""bjoern server example"""


bjoern.listen(app, "0.0.0.0", 6000)
bjoern.run()

