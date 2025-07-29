from flask import Flask
from app.routes.resume import resume_bp

app = Flask(__name__)

# Set the secret key for session handling
app.secret_key = 'f3c1d5e6e7a1b3f459e6a64a5d83a51a7624d0f3bbaf651b405e34e3c92f3f08'

# Register the resume blueprint
app.register_blueprint(resume_bp)

if __name__ == '__main__':
    app.run(debug=True)
