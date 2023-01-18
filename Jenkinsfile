pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                bat 'mkdir .venv'
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
                bat 'pipenv run python ./tigerden/manage.py runserver'
            }
        }
    }
}