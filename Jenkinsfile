pipeline {
    agent any

    options {
        buildDiscarder(logRotator(daysToKeepStr: '5', numToKeepStr: '20'))
    }

    triggers {
        cron('H/30 * * * *')
    }

    environment {
        VENV_DIR = "venv"
    }

    stages {

       stage('Clean Workspace') {
            steps {
                deleteDir() // Clean workspace before pulling fresh repo
            }
        }

        stage('Clone Repository') {
            steps {
                git credentialsId: 'my_secret_token', url: 'https://github.com/WalaaHijazi1/Advance_DevOps_Project.git', branch: 'Advance_project_Docker'
            }
        }

        stage('Update Repository') {
            steps {
                sh '''
                    git fetch --all
                    git reset --hard origin/Advance_project_Docker
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh """
                        rm -rf ${VENV_DIR}
                        python3 -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install -r requirements.txt
                    """
                }
            }
        }

        stage('Start SQL Container for Non-Docker Testing') {
            steps {
                sh '''
                    echo "Starting SQL container for rest_app.py..."
                    docker rm -f my-mysql-container || true
                    docker run -d --name my-mysql-container \
                        -e MYSQL_ROOT_PASSWORD=restapp \
                        -e MYSQL_DATABASE=restuser \
                        -e MYSQL_USER=restuser \
                        -e MYSQL_PASSWORD=restpass \
                        -p 3306:3306 \
                        mysql:8.0

                    echo "Waiting for MySQL to be ready..."
                    counter=0
                    until docker exec my-mysql-container mysqladmin ping -h "localhost" --silent; do
                        sleep 2
                        counter=$((counter + 1))
                        if [ $counter -ge 15 ]; then
                            echo "MySQL container did not start in time"
                            exit 1
                        fi
                    done

                    echo "MySQL container is ready!"
                '''
            }
        }

        stage('Run rest_app.py') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    nohup python3 rest_app.py > rest_app.log 2>&1 &

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
                sh """
                    . ${VENV_DIR}/bin/activate
                    python3 backend_testing.py
                """
            }
        }

        stage('Run clean_environment.py') {
            steps {
                script {
                    sh """
                        . ${VENV_DIR}/bin/activate
                        python3 clean_environment.py
                    """
                }
            }
        }

        stage('Debug Workspace') {
            steps {
        	   sh 'ls -la'
    	}
          }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t rest-app-server .'
            }
        }

        stage('Run Docker Image') {
            steps {
                sh '''
                    docker rm -f rest-app-server-${BUILD_ID} || true
                    docker run -d --name rest-app-server-${BUILD_ID} -p 5000:5000 rest-app-server
                '''
            }
        }

        stage('Push Docker Image & Set Image Version') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker_username', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''
                            echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USER} --password-stdin
                            docker tag rest-app-server:latest walaahij/rest-app-server:${BUILD_ID}
                            docker push walaahij/rest-app-server:${BUILD_ID}
                        '''
                    }
                }
            }
        }

        stage('Check & Install Docker-Compose') {
            steps {
                sh '''
                    if ! command -v docker-compose &> /dev/null; then
                        echo "Docker Compose not found. Installing..."
                        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                        sudo chmod +x /usr/local/bin/docker-compose
                        sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
                        echo "Docker Compose Installed ..."
                    else
                        echo "Docker Compose is already installed ..."
                    fi
                '''
            }
        }

        stage('Docker Compose stage') {
            steps {
                sh 'docker-compose up -d --build'
            }
        }

        stage('Wait for Docker-Compose') {
            steps {
                script {
                    sh '''
                        echo "Waiting for Docker Compose services to be up..."
                        counter=0
                        until curl -s http://localhost:5000 > /dev/null || [ $counter -ge 15 ]; do
                            echo "Waiting for service to be available on port 5000..."
                            sleep 2
                            counter=$((counter + 1))
                        done

                        if [ $counter -ge 15 ]; then
                            echo "Service did not become available in time. Failing build."
                            exit 1
                        fi

                        echo "Service is up and running."
                    '''
                }
            }
        }

        stage('Docker Compose Test') {
            steps {
                sh '''
                    echo "Running backend tests inside Docker Compose..."
                    docker-compose exec app python3 backend_testing.py

                    echo "Running frontend tests inside Docker Compose..."
                    docker-compose exec app python3 frontend_testing.py
                '''
            }
        }

        stage('Docker Compose Down & Remove Image') {
            steps {
                sh '''
                    echo "Stopping and removing Docker Compose services..."
                    docker-compose down --volumes --remove-orphans

                    echo "Removing Docker image rest-app-server..."
                    docker rmi -f rest-app-server || true
                '''
            }
        }
    }
}
