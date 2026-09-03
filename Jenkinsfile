 pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out Blue-Green deployment project'
            }
        }

        stage('Detect Active Environment') {
            steps {
                script {
                    def response = bat(
                        script: 'curl -s http://localhost:8080/',
                        returnStdout: true
                    ).trim()

                    echo "Production response: ${response}"

                    if (response.contains('GREEN')) {
                        env.ACTIVE = 'GREEN'
                        env.TARGET = 'BLUE'
                    } else if (response.contains('BLUE')) {
                        env.ACTIVE = 'BLUE'
                        env.TARGET = 'GREEN'
                    } else {
                        error "Could not determine active environment"
                    }

                    echo "Active environment: ${env.ACTIVE}"
                    echo "Deployment target: ${env.TARGET}"
                }
            }
        }

        stage('Build') {
            steps {
                bat 'where docker'
                bat 'docker version'
                bat 'docker build -t blue-green-demo:v2 .'
            }
        }

        stage('Deploy Target') {
            steps {
                script {
                    if (env.TARGET == 'BLUE') {
                        bat 'docker rm -f blue 2>NUL || exit 0'
                        bat 'docker run -d --name blue -p 5001:5000 blue-green-demo:v2'
                    } else {
                        bat 'docker rm -f green 2>NUL || exit 0'
                        bat 'docker run -d --name green -p 5002:5000 blue-green-demo:v2'
                    }
                }
            }
        }

        stage('Smoke Test') {
            steps {
                script {
                    if (env.TARGET == 'BLUE') {
                        bat 'curl -f http://localhost:5001/health'
                        bat 'curl -f http://localhost:5001/'
                    } else {
                        bat 'curl -f http://localhost:5002/health'
                        bat 'curl -f http://localhost:5002/'
                    }
                }
            }
        }

        stage('Switch Traffic') {
            steps {
                script {
                    if (env.TARGET == 'BLUE') {
                        bat 'powershell -Command "(Get-Content nginx.conf) -replace \\"5002\\",\\"5001\\" | Set-Content nginx.conf"'
                    } else {
                        bat 'powershell -Command "(Get-Content nginx.conf) -replace \\"5001\\",\\"5002\\" | Set-Content nginx.conf"'
                    }

                    bat 'docker exec nginx nginx -t'
                    bat 'docker exec nginx nginx -s reload'
                }
            }
        }
    }
}