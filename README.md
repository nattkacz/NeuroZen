# NeuroZen - AI-Powered Mental Wellness Tracker

**NeuroZen** is a holistic wellness application built with **Django** and **PostgreSQL**. It combines productivity tools with mental health support, featuring AI-driven daily summaries, mood tracking, and mindful breathing exercises.

---

## Key Features

* **AI Daily Insights:** Leverages **OpenAI GPT** to analyze your day and provide supportive, personalized feedback.
* **Dynamic Dashboard:** A real-time overview of tasks, Pomodoro sessions, and current mood.
* **Pomodoro Focus Timer:** Integrated task-linked timer to boost productivity without burnout.
* **Interactive Breathing:** Customizable breathing exercises (Inhale/Hold/Exhale) managed via database.
* **Mental Health Journal:** Secure mood logging and personal notes.
* **Gamification:** Point system and streaks to encourage consistent wellness habits.

---

## Security Features

As a security-conscious project, NeuroZen implements:
* **Environment Secret Management:** Sensitive data (API Keys, DB Credentials) are managed via `.env` and never committed to version control.
* **Authentication & Authorization:** Secure user registration and login with Django's robust auth system.
* **Ownership Protection:** Strict database filtering ensures users can only access their own private data.
* **Secure API Integration:** Robust error handling for external API calls (OpenAI) to prevent information leakage.

---

## Tech Stack

* **Backend:** Python 3.x, Django 5.x
* **Database:** PostgreSQL
* **AI Integration:** OpenAI API
* **Frontend:** Bootstrap 5, JavaScript, CSS3
* **Version Control:** Git

---

##  Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nattkacz/NeuroZen.git](https://github.com/nattkacz/NeuroZen.git)
    cd NeuroZen
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the root directory and add:
    ```env
    SECRET_KEY=your_django_secret_key
    OPENAI_API_KEY=your_openai_key
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    ```

5.  **Run migrations and start the server:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

---

##  Author

**Natalia Kaczorowska**
* GitHub: [@nattkacz](https://github.com/nattkacz)