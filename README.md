Django Instagram Clone
A modern, full-featured web application replicating Instagram's core functionality. Share photos, connect with friends, and build your community.

Built with Python and Django, this project is a robust and scalable solution for photo-sharing social media.

✨ Features
User Authentication: Secure sign-up, login, and logout.

Dynamic Profiles: Personal profile pages displaying a user's posts, follower count, and bio.

Photo Posts: Upload images with captions. Posts are displayed on the user's profile and in a personalized feed.

Social Following: Follow and unfollow other users to see their content in your feed.

Post Interactions: Like and comment on posts to engage with other users.

Responsive Design: A beautiful, mobile-first design built with modern CSS frameworks.

🛠️ Tech Stack
Backend
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge">

<img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django Badge">

<img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL Badge">

Frontend
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5 Badge">

<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3 Badge">

<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript Badge">

Libraries & Tools
<img src="https://img.shields.io/badge/Pillow-239120?style=for-the-badge&logo=pillow&logoColor=white" alt="Pillow Badge"> (Image Processing)

<img src="https://img.shields.io/badge/Whitenoise-181818?style=for-the-badge&logo=heroku&logoColor=white" alt="Whitenoise Badge"> (Static Files)

<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git Badge">

<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Badge">

🚀 Getting Started
Prerequisites
Python 3.8+

PostgreSQL

git installed

1. Clone the Repository
Bash

git clone https://github.com/your-username/django-instagram-clone.git
cd django-instagram-clone
2. Create a Virtual Environment
Bash

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Configure the Database
Create a PostgreSQL database and update your settings.py or .env file with your database credentials.

Python

# settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
5. Run Migrations
Bash

python manage.py migrate
6. Run the Development Server
Bash

python manage.py runserver
Open your browser and navigate to http://127.0.0.1:8000. You're all set!

🤝 Contribution
Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📝 License
Distributed under the MIT License. See LICENSE for more information.

📞 Contact
Your Name - @YourTwitterHandle - your.email@example.com

Project Link: https://github.com/your-username/django-instagram-clone

GitHub Stats
<p align="center">
<img src="https://github-readme-stats.vercel.app/api?username=magdeleine&show_icons=true&theme=radical" alt="Magdeleine's GitHub Stats" />
<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=magdeleine&layout=compact&theme=radical" alt="Top Languages" />
</p>
