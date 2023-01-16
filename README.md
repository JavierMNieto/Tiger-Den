# Tiger Den
Online ordering system for Tiger Den. The Tiger Den is a cafe shop in Edwardsville High School ran by students with special needs.

[Test Site Here](https://javiermnieto.pythonanywhere.com/)

Made with:

- [Django](https://github.com/django/django)
- [Django-Oscar](https://github.com/django-oscar/django-oscar)

The ordering system works more as a group ordering system where students place their order requests to their teacher, and the teacher then can review the orders and either place the orders all at once to the Tiger Den where they can fullfill the orders or cancel orders.

Students -> Teacher -> Tiger Den

## Installation

1. Clone the repository
```bash
git clone https://github.com/JavierMNieto/Tiger-Den.git
```

2. Install [Python](https://www.python.org/downloads/) and [Pip](https://pip.pypa.io/en/stable/installation/)

3. Install [Pipenv](https://pypi.org/project/pipenv/)
```bash
pip install pipenv
```
If you are on Windows, you may need to add the python Scripts folder to your PATH environment variable as indicated in the [Pipenv documentation (see Note)](https://pipenv.pypa.io/en/latest/install/#pragmatic-installation-of-pipenv)

4. Navigate to the project directory
```bash
cd Tiger-Den
```

5. Install dependencies
```bash
pipenv install
```

6. Activate the virtual environment
```bash
pipenv shell
```

7. Initialize the database
```bash
python utils.py initdb
```
Migrations will be made and you will be prompted to create a superuser. Fill in a username, email, and password.

8. Run the server
```bash
python utils.py runserver
```