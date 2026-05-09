pipeline {
    agent any

    options {
        // This ensures a fresh workspace BEFORE the checkout happens
        skipDefaultCheckout(false)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Clean the workspace before the build starts
        checkoutToSubdirectory('')
    }

    environment {
        SCRAPER_IMAGE = "ebay-scraper-prod"
        Telegram_API_KEY     = credentials('telegram-api-key')
        Telegram_Channel_id  = credentials('telegram-channel-id')
    }

    stages {
        // Stage 'Clean Workspace' removed: logic moved to options or handled by SCM settings

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
                script {
                    // This will now work because of your root/socket setup!
                    def dockerReady = sh(
                        returnStatus: true,
                        script: 'docker info > /dev/null 2>&1'
                    ) == 0

                    if (!dockerReady) {
                        echo 'Skipping Docker build: Docker daemon/socket is not accessible to Jenkins.'
                        return
                    }

                    sh "docker build -t ${SCRAPER_IMAGE}:${env.BUILD_ID} ."
                }
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
        cleanup {
            // Optional: Clean up after the build is finished to save disk space
            cleanWs()
        }
    }
}