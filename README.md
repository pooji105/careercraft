# CareerCraft

A comprehensive Flask web application for career development, featuring resume building, interview preparation, and job tracking capabilities.

## Features

- **Resume Builder**: Create professional resumes with customizable templates
- **Interview Preparation**: AI-powered interview practice and feedback
- **Job Tracker**: Organize and track your job applications
- **User Dashboard**: Centralized view of your career progress
- **Mobile Responsive**: Optimized for all device sizes

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: PostgreSQL/MySQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login
- **Database Migrations**: Flask-Migrate
- **Environment Management**: python-dotenv

## Project Structure

```
edubot_a/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── images/
│   ├── templates/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── interview/
│   │   ├── jobs/
│   │   ├── main/
│   │   ├── resume/
│   │   └── base.html
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── interview.py
│   │   ├── jobs.py
│   │   ├── main.py
│   │   └── resume.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   ├── __init__.py
│   └── models.py
├── instance/
│   └── config.py
├── migrations/
├── .env (create from env.example)
├── env.example
├── requirements.txt
├── run.py
└── README.md
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd edubot_a
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your configuration
   # Update SECRET_KEY, DATABASE_URL, and OPENROUTER_API_KEY
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   # Set Flask app environment variable
   # Windows
   set FLASK_APP=run.py
   
   # macOS/Linux
   export FLASK_APP=run.py
   
   # Run the application
   flask run
   ```

   Or simply run:
   ```bash
   python run.py
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=postgresql://username:password@localhost/careercraft_db
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

## Database Setup

### PostgreSQL
```sql
CREATE DATABASE careercraft_db;
CREATE USER careercraft_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE careercraft_db TO careercraft_user;
```

### MySQL
```sql
CREATE DATABASE careercraft_db;
CREATE USER 'careercraft_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON careercraft_db.* TO 'careercraft_user'@'localhost';
FLUSH PRIVILEGES;
```

## Usage

1. **Access the application**: Open your browser and go to `http://localhost:5000`
2. **Register/Login**: Create an account or log in to access features
3. **Dashboard**: View your career progress and quick actions
4. **Resume Builder**: Create and customize professional resumes
5. **Interview Prep**: Practice interviews with AI feedback
6. **Job Tracker**: Organize and track your job applications

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

### Database Migrations
```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Testing
```bash
# Run tests (when implemented)
python -m pytest
```

## API Keys

### OpenRouter API
This application uses OpenRouter API for AI-powered features. To get an API key:

1. Visit [OpenRouter](https://openrouter.ai/)
2. Create an account
3. Generate an API key
4. Add it to your `.env` file

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@careercraft.com or create an issue in the repository.

## Roadmap

- [ ] User authentication and authorization
- [ ] Resume builder with multiple templates
- [ ] AI-powered interview practice
- [ ] Job application tracking
- [ ] Email notifications
- [ ] Resume sharing and collaboration
- [ ] Advanced analytics and insights
- [ ] Mobile app development 