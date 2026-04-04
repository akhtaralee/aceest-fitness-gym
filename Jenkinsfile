pipeline {
    agent {
        docker {
            image 'python:3.10'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        IMAGE_NAME = 'aceest-fitness-gym'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        VENV = 'venv'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Verify Tools') {
            steps {
                echo 'Checking Python & Docker installation...'
                sh '''
                    python --version
                    pip --version
                    docker --version
                '''
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                sh '''
                    python -m venv $VENV
                    . $VENV/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                echo 'Running Flake8 linter...'
                sh '''
                    . $VENV/bin/activate
                    flake8 app.py --max-line-length=120 --statistics
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo 'Running Pytest suite...'
                sh '''
                    . $VENV/bin/activate
                    pytest test_app.py -v --tb=short
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Run Container Tests') {
            steps {
                echo 'Running tests inside Docker container...'
                sh """
                    docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} \
                    python -m pytest test_app.py -v --tb=short
                """
            }
        }

        stage('Cleanup Docker') {
            steps {
                echo 'Cleaning unused Docker images...'
                sh 'docker system prune -f'
            }
        }
    }

    post {
        success {
            echo 'BUILD SUCCESSFUL – All quality gates passed!'
        }
        failure {
            echo 'BUILD FAILED – Check the logs above for errors.'
        }
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
    }
}
