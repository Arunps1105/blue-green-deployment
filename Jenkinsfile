 pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out Blue-Green deployment project'
            }
        }

        stage('Build') {
            steps {
                bat 'where docker'
                bat 'docker version'
                bat 'docker build -t blue-green-demo:v2 .'
            }
        }

        stage('Deploy Green') {
            steps {
                bat 'docker rm -f green 2>NUL || exit 0'
                bat 'docker run -d --name green -p 5002:5000 blue-green-demo:v2'
            }
        }

        stage('Smoke Test') {
            steps {
                bat 'curl -f http://localhost:5002/health'
                bat 'curl -f http://localhost:5002/'
            }
        }
 
        stage('Detect Active Environment') {
     steps {
        bat 'curl http://localhost:8080/'
    }
}
    }
}