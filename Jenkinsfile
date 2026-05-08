pipeline {
    agent any

    environment {
        SCRAPER_IMAGE = "ebay-scraper-prod"
        Telegram_API_KEY     = credentials('telegram-api-key')
        Telegram_Channel_id  = credentials('telegram-channel-id')
    }

    stages {
        stage('Setup Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install .
                    pip install flake8 pytest
                '''
            }
        }

        stage('Static Analysis (Linting)') {
            steps {
                sh '''
                    . venv/bin/activate
                    flake8 src tests setup.py --format=default --output-file=flake8-warnings.txt || true
                '''
                recordIssues(tools: [flake8(pattern: 'flake8-warnings.txt')])
            }
        }

        stage('Unit & Mock Testing') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest tests/ --ignore=tests/scripts --junitxml=results.xml
                '''
            }
            post {
                always {
                    junit 'results.xml'
                }
            }
        }

        stage('Build Scraper Image') {
            steps {
                sh "docker build -t ${SCRAPER_IMAGE}:${env.BUILD_ID} ."
            }
        }
    }

    post {
        success {
            echo 'Pipeline passed: scraper is ready for deployment.'
        }
        failure {
            echo 'Pipeline failed: review linting or test results.'
        }
    }
}
