"""Runs the flask app with frontend attached."""

import main

if __name__ == '__main__':
    main.create_app(include_frontend=True).run(host="0.0.0.0", port=80, debug=False)
