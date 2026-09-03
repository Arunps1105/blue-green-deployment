pipeline {
    agent any

    environment {
        IMAGE = "blue-green-demo:build-${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out Blue-Green deployment project'
            }
        }

        stage('Detect Active Environment') {
            steps {
                script {

                    def nginxConfig = 'C:\\Users\\arunp\\blue-green-demo\\nginx.conf'

                    def blueResult = bat(
                        script: "findstr /C:\"5001\" \"${nginxConfig}\"",
                        returnStatus: true
                    )

                    def greenResult = bat(
                        script: "findstr /C:\"5002\" \"${nginxConfig}\"",
                        returnStatus: true
                    )

                    if (blueResult == 0 && greenResult != 0) {

                        env.ACTIVE = 'BLUE'
                        env.TARGET = 'GREEN'

                    } else if (greenResult == 0 && blueResult != 0) {

                        env.ACTIVE = 'GREEN'
                        env.TARGET = 'BLUE'

                    } else {

                        error "Could not determine active environment from Nginx configuration"
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

                bat 'docker build -t %IMAGE% .'
            }
        }

        stage('Deploy Target') {
            steps {
                script {

                    if (env.TARGET == 'BLUE') {

                        bat 'docker rm -f blue 2>NUL || exit 0'

                        bat 'docker run -d --name blue -p 5001:5000 -e ENVIRONMENT=BLUE %IMAGE%'

                    } else {

                        bat 'docker rm -f green 2>NUL || exit 0'

                        bat 'docker run -d --name green -p 5002:5000 -e ENVIRONMENT=GREEN %IMAGE%'
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

                        bat 'curl -f http://localhost:5001/version'

                    } else {

                        bat 'curl -f http://localhost:5002/health'

                        bat 'curl -f http://localhost:5002/'

                        bat 'curl -f http://localhost:5002/version'
                    }
                }
            }
        }

        stage('Verify Target Environment') {
            steps {
                script {

                    if (env.TARGET == 'BLUE') {

                        def response = bat(
                            script: 'curl -s http://localhost:5001/version',
                            returnStdout: true
                        ).trim()

                        echo "BLUE target response: ${response}"

                        if (!response.contains('"environment":"BLUE"')) {
                            error "BLUE target verification failed"
                        }

                    } else {

                        def response = bat(
                            script: 'curl -s http://localhost:5002/version',
                            returnStdout: true
                        ).trim()

                        echo "GREEN target response: ${response}"

                        if (!response.contains('"environment":"GREEN"')) {
                            error "GREEN target verification failed"
                        }
                    }

                    echo "Target environment verification successful."
                }
            }
        }

        stage('Switch Traffic') {
            steps {
                script {

                    def nginxConfig = 'C:\\Users\\arunp\\blue-green-demo\\nginx.conf'

                    if (env.TARGET == 'BLUE') {

                        bat "powershell -Command \"(Get-Content '${nginxConfig}') -replace '5002','5001' | Set-Content '${nginxConfig}'\""

                    } else {

                        bat "powershell -Command \"(Get-Content '${nginxConfig}') -replace '5001','5002' | Set-Content '${nginxConfig}'\""
                    }

                    bat 'docker exec nginx nginx -t'

                    bat 'docker exec nginx nginx -s reload'

                    echo "Traffic successfully switched to ${env.TARGET}"
                }
            }
        }

        stage('Production Verification') {
            steps {

                echo 'Verifying production traffic...'

                bat 'curl -f http://localhost:8080/health'

                bat 'curl -f http://localhost:8080/'

                bat 'curl -f http://localhost:8080/version'

                echo "Production verification successful."

                echo "============================================"
                echo "INTENTIONAL FAILURE FOR ROLLBACK DEMO"
                echo "============================================"

                bat 'exit /b 1'
            }
        }
    }

    post {

        failure {
            script {

                def nginxConfig = 'C:\\Users\\arunp\\blue-green-demo\\nginx.conf'

                def switchHappened = false

                if (env.TARGET == 'BLUE') {

                    def result = bat(
                        script: "findstr /C:\"5001\" \"${nginxConfig}\"",
                        returnStatus: true
                    )

                    if (result == 0) {
                        switchHappened = true
                    }

                } else if (env.TARGET == 'GREEN') {

                    def result = bat(
                        script: "findstr /C:\"5002\" \"${nginxConfig}\"",
                        returnStatus: true
                    )

                    if (result == 0) {
                        switchHappened = true
                    }
                }

                if (switchHappened) {

                    echo "Deployment failed after traffic was switched."

                    echo "Starting automatic rollback..."

                    echo "Restoring previous environment: ${env.ACTIVE}"

                    if (env.ACTIVE == 'BLUE') {

                        bat "powershell -Command \"(Get-Content '${nginxConfig}') -replace '5002','5001' | Set-Content '${nginxConfig}'\""

                    } else if (env.ACTIVE == 'GREEN') {

                        bat "powershell -Command \"(Get-Content '${nginxConfig}') -replace '5001','5002' | Set-Content '${nginxConfig}'\""
                    }

                    bat 'docker exec nginx nginx -t'

                    bat 'docker exec nginx nginx -s reload'

                    echo "Rollback completed."

                    echo "Production restored to: ${env.ACTIVE}"

                } else {

                    echo "Deployment failed before traffic was switched."

                    echo "No rollback required."
                }
            }
        }

        success {

            echo "Blue-Green deployment completed successfully."

            echo "Production environment: ${env.TARGET}"
        }
    }
}