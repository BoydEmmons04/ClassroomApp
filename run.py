from app import create_app

# Gunicorn and the Flask CLI both import this object from run:app.
app = create_app()


if __name__ == "__main__":
    # This path is handy when running `python run.py` outside Docker.
    app.run(host="0.0.0.0", port=5000, debug=True)
