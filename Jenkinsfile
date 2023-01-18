pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'pipenv install'
                sh 'pipenv run python ./tigerden/manage.py migrate'
            }
        }
        stage('Test') {
            steps {
                sh 'pipenv run python ./tigerden/manage.py test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'pipenv run python ./tigerden/manage.py runserver'
            }
        }
    }
}