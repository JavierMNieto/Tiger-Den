pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                bat 'if not exist .venv mkdir .venv'
                bat 'pipenv install'
                bat 'pipenv run python ./tigerden/manage.py migrate'
            }
        }
        stage('Test') {
            steps {
                bat 'pipenv run python ./tigerden/manage.py test'
            }
        }
        stage('Deploy') {
            steps {
                bat 'pipenv run python ./tigerden/manage.py collectstatic --noinput'
                bat '%windir%\\system32\\inetsrv\\appcmd stop site /site.name:"Tiger Den"'
                bat '%windir%\\system32\\inetsrv\\appcmd start site /site.name:"Tiger Den"'
            }
        }
    }
}