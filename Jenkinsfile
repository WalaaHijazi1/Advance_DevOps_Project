pipeline {
    agent any

    environment {
        VENV_DIR = "myenv"  // Define virtual environment directory
    }

    stages {
        stage('Clone Repository') {
            steps {
                git credentialsId: 'github-pat', url: 'https://github.com/WalaaHijazi1/DevOps_Advance_Project.git', branch: 'main'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    pip install --no-cache-dir --upgrade -r requirements.txt
                '''
            }
        }

        stage('Start Backend') {
            steps {
                sh '''
                    . $VENV_DIR/bin/activate
                    nohup python3 rest_app.py > rest_app.log 2>&1 &
                    echo $! > rest_app.pid  # Store the process ID
                '''
            }
        }

        stage('Wait for Backend') {
            steps {
                sh '''
                    counter=0
                    while ! curl -s 127.0.0.1:5000 > /dev/null && [ $counter -lt 15 ]; do
                        echo "Waiting for backend to be available..."
                        sleep 2
                        counter=$((counter + 1))
                    done
            
                    if [ $counter -eq 15 ]; then
                        echo "Backend did not start in time."
                        exit 1
                    fi
                    echo "Backend is up and running."
                '''
            }
        }

        stage('Run backend_testing.py') {
            steps {
                sh '''
                    . $VENV_DIR/bin/activate
                    python3 backend_testing.py
                '''
            }
        }

        stage('Run combined_testing.py') {
            steps {
                sh '''
                    source $VENV_DIR/bin/activate
                    python3 combined_testing.py
                '''
            }
        }

        stage('Run frontend_testing.py') {
            steps {
                sh '''
                    . $VENV_DIR/bin/activate
                    python3 frontend_testing.py
                '''
            }
        }
    }

    post {
        always {
            sh '''
                if [ -f rest_app.pid ]; then
                    echo "Stopping backend..."
                    kill $(cat rest_app.pid) || true
                    rm -f rest_app.pid
                fi
            '''
        }
    }
}
