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
        IMAGE_NAME = "walaahij/rest-app-server-${BUILD_ID}"
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

        stage('Start MySQL and Init Table') {
           steps {
        	sh '''
        	docker rm -f my-mysql-container || true
        	docker run -d --name my-mysql-container \
          	    -e MYSQL_ROOT_PASSWORD=restapp \
          	    -e MYSQL_DATABASE=user_db \
         	    -e MYSQL_USER=restuser \
          	    -e MYSQL_PASSWORD=restpass \
          	    -p 3306:3306 \
	    -v mysql_data:/var/lib/mysql \
          	    -v $(pwd)/init.sql:/docker-entrypoint-initdb.d/init.sql \
          	    mysql:8.0
        	sleep 15  # wait for MySQL to start up
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

       stage('Debug Logs') {
           steps {
        	echo "Searching for error.log..."
        	sh 'find . -name "error.log"'
        	echo "Checking workspace contents..."
        	sh 'ls -R'
    	}
         }

       stage('Check REST App Logs') {
            steps {
        	       echo "==== REST APP LOG ====" 
	       sh 'ls -l error.log || echo "No error.log file found"'
        	       sh 'cat error.log || echo "No error.log found or no permissions"'
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
                    # Force remove any existing container
                    docker rm -f rest-app-server-${BUILD_ID} || true
                    # Kill any process using port 5000
                    sudo fuser -k 5000/tcp || true
                    docker run -d --name rest-app-server-${BUILD_ID} -p 5000:5000 rest-app-server
                '''
            }
        }

        stage('Push Docker Image & Set Image Version') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker-username', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
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
                    if command -v docker-compose &> /dev/null; then
                        echo "Docker Compose found. Removing existing version..."
                        sudo rm -f /usr/local/bin/docker-compose
                        sudo rm -f /usr/bin/docker-compose
                    else
                        echo "Docker Compose not found."
                    fi

                    echo "Installing Docker Compose..."
                    ARCH=$(uname -m)
                    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$ARCH" -o /usr/local/bin/docker-compose
                    sudo chmod +x /usr/local/bin/docker-compose
                    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose || true
                '''
            }
        }

        stage('Docker Compose stage') {
            steps {
                script {
                    // Substitute the BUILD_ID into the docker-compose.yml file before running
                    sh '''
                        sed -i "s|walaahij/rest-app-server-${BUILD_ID}|${IMAGE_NAME}|g" docker-compose.yml
                        docker-compose up -d --build
                    '''
                }
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
                    docker-compose exec rest_app python3 backend_testing.py

                    echo "Running frontend tests inside Docker Compose..."
                    docker-compose exec rest_app python3 frontend_testing.py
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
