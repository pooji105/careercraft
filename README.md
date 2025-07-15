# 💼 CareerCraft – AI-Powered Career Development Platform

**CareerCraft** is a full-stack web application that empowers users to build resumes, get AI-powered suggestions, simulate interviews, track job applications, and explore personalized job roles — all enhanced by the [OpenRouter API](https://openrouter.ai/).

🎯 Built for students and job seekers, developed as part of an academic project at **SRM University – AP**.

---

## 📁 Folder Structure

```
edubot_a/
├── app/
│   ├── static/         # CSS, JS, assets
│   ├── templates/      # Jinja2 HTML templates
│   │   ├── base.html
│   │   └── [feature]/[template.html]
│   ├── models.py       # SQLAlchemy models
│   ├── routes/         # Feature-based route modules
│   ├── utils/          # File parsers, AI utilities
│   └── __init__.py     # App factory
├── instance/
│   └── config.py       # (optional)
├── migrations/         # Flask-Migrate DB files
├── env.example         # Sample .env file
├── .env                # Your environment secrets (not tracked)
├── requirements.txt    # Python dependencies
├── run.py              # Entry point
├── README.md
```

---

## 🛠️ Tech Stack

| Layer       | Tech                                      |
|-------------|-------------------------------------------|
| Frontend    | HTML, CSS, Bootstrap 5                    |
| Backend     | Python (Flask), Jinja2                    |
| Database    | SQLite (Dev) / PostgreSQL or MySQL (Prod) |
| AI API      | [OpenRouter API](https://openrouter.ai/)  |
| File Tools  | PyMuPDF, pdfminer, Pillow                 |
| Auth        | Flask-Login                               |
| Deployment  | Localhost (Dev), Render/Heroku (Optional) |

---

## 🌟 Features

- 🧾 **Resume Builder** — Create resumes and export as PDFs  
- 📤 **Resume Analyzer (AI)** — Upload your resume and get smart suggestions  
- 🔍 **Job Role Matcher (AI)** — Get job role and skill recommendations  
- 🎤 **Interview Simulator (AI)** — Practice and get feedback on interview questions  
- 📊 **Dashboard** — View your resume, job, and skill stats with quick links  
- 🧠 **Skill Tracker** — Manage and visualize technical and soft skills  
- 📋 **Job Tracker** — Log job applications and upload job descriptions  
- 🌙 **Dark/Light Mode** — Toggle between visual modes  
- 📚 **Resource Repository** — Curated links for resumes, tech prep, soft skills  
- 🔐 **User Auth** — Registration, login, and logout with session handling  
- 🛡️ **Security** — CSRF protection, file validation, safe uploads  

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/edubot_a.git
cd edubot_a
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

- Copy `env.example` to `.env` and fill in your OpenRouter API key and database URI.

### 5. Initialize the Database

```bash
flask db upgrade
```

### 6. Run the Application

```bash
# On Windows:
set FLASK_APP=app.py
flask run
# On Mac/Linux:
export FLASK_APP=app.py
flask run
```

---

## 🔑 .env Format

Your `.env` file should include at least:

```
OPENROUTER_API_KEY=your_key
DATABASE_URL=sqlite:///instance/careercraft.db  # or your production DB URI
SECRET_KEY=your_secret_key
```

---

## 🧪 Testing

### 1. **Routes & Forms**
- Visit `/register`, `/login`, `/logout` to test authentication.
- Use `/resume/builder` to create a resume and download as PDF.
- Use `/resume/upload` to upload a resume and receive AI feedback.
- Use `/resume/job-matcher` to get job role suggestions.
- Use `/interview` to simulate interviews and get feedback.
- Use `/skills` and `/job-tracker` to test skill/job tracking CRUD.
- Try dashboard and resources pages for navigation and stats.

### 2. **OpenRouter Integrations**
- Ensure your `.env` has a valid `OPENROUTER_API_KEY`.
- Test AI features (resume analyzer, job matcher, interview simulator) for real-time responses.
- Check error handling for invalid/missing API keys.

### 3. **Forms & Validation**
- All forms have client-side and server-side validation.
- File uploads are restricted to allowed types (PDF/TXT).
- CSRF protection is enabled for all POST forms.

---

## 🖼️ Sample Screenshots

> _Add screenshots or a GIF here to showcase the UI and features!_
>
> ![Dashboard Screenshot](screenshots/dashboard.png)
> ![Resume Builder Screenshot](screenshots/resume_builder.png)
> ![Job Matcher Screenshot](screenshots/job_matcher.png)

---

## 🚀 Deployment Notes

- For production, set `FLASK_ENV=production` and use a production-ready database (PostgreSQL/MySQL).
- Configure a secure `SECRET_KEY` and restrict allowed hosts.
- Deploy on [Render](https://render.com/), Heroku, or any WSGI-compatible host.
- Set environment variables in your deployment dashboard.
- Use HTTPS in production for security.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.