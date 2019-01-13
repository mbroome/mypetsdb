import os
import sys


#scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
#sys.path.append(scriptPath + '/lib/')

from lib.app import app

import lib.controllers.species
import lib.controllers.pets

# Register blueprint(s)
app.register_blueprint(lib.controllers.species.routes)
app.register_blueprint(lib.controllers.pets.routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
