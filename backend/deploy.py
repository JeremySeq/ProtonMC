"""Runs the flask app with frontend attached."""

import main

if __name__ == "__main__":
    main.run_app(host="0.0.0.0", port=80, include_frontend=True)