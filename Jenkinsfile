// ─────────────────────────────────────────────
// ACEest Fitness & Gym – Jenkins Pipeline
// 
// ─────────────────────────────────────────────

pipeline {
    agent any

    environment {
        IMAGE_NAME = 'aceest-fitness-gym'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo ' Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo ' Setting up Python virtual environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                echo 'Running Flake8 linter...'
                sh '''
                    . venv/bin/activate
                    flake8 app.py --max-line-length=120 --statistics
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo ' Running Pytest suite...'
                sh '''
                    . venv/bin/activate
                    pytest test_app.py -v --tb=short
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo ' Building Docker image...'
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Run Container Tests') {
            steps {
                echo ' Running tests inside Docker container...'
                sh """
                    docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} \
                        python -m pytest test_app.py -v --tb=short
                """
            }
        }
    }

    post {
        success {
            echo 'BUILD SUCCESSFUL – All quality gates passed!'
        }
        failure {
            echo ' BUILD FAILED – Check the logs above for errors.'
        }
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
    }
}
