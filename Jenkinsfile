pipeline {
    agent any

    options {                   ////This block defines pipeline options.
        buildDiscarder(logRotator(daysToKeepStr: '5', numToKeepStr: '20'))
        // Controls how many old builds Jenkins keeps.
        // daysToKeepStr: '5' → Jenkins will delete builds older than 5 days.
        // numToKeepStr: '20' → Jenkins will keep a maximum of 20 builds, even if they are recent.  
    }

    triggers {
         //Runs every 30 minutes regardless of SCM changes
        cron('H/30 * * * *')
    }

    environment {
        VENV_DIR = "venv"          // Define virtual environment directory
    }


    stages {
        stage('Clean Workspace') {
            steps {
                deleteDir() // Clean workspace before pulling fresh repo
            }
        }

        stage('Clone Repository') {
            steps {

	// This stage clones the repository from GitHub into the Jenkins workspace.
	// It uses Git credentials (github-pat) for authentication.
	// It checks out the main branch.
	// Cloning the repository every time we run Jenkins file ensures Jenkins has the latest code before running the pipeline.

                git credentialsId: 'my_secret_token', url: 'https://github.com/WalaaHijazi1/Advance_DevOps_Project.git', branch: 'AdvanceProject_K8s_Integration'
            }
        }

        stage('Update Repository') {
            steps {

	 // If a previous build modified the repository, this ensures a fresh and clean state.
                sh '''
                    git fetch --all
                    git reset --hard origin/AdvanceProject_K8s_Integration
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh """
	         #Remove existing venv to avoid corruption or permission issues
                        rm -rf ${VENV_DIR}

	         # Create a fresh virtual environment
                        python3 -m venv ${VENV_DIR}

	         # Activate and install dependencies
                        . ${VENV_DIR}/bin/activate
                        pip install -r requirements.txt
                    """
                }
            }
        }

        stage('Start MySQL and Init Table') {
           steps {
        	sh '''
	# remove if there was an sql container that was
        	docker rm -f my-mysql-container || true

	# this creates an sql docker container it's name is: my-mysql-container it's running in a detach mode,
	# there was a few environment variables that is passed when the container's is running, and the port that the 
	# container is running on them maping to the same port's number on the host machine.
	# there are two volmes, the first volume where MySQL stores its data files persistently.
	# The second volume mounts the init.sql file into the special MySQL init directory.

        	docker run -d --name my-mysql-container \
          	    -e MYSQL_ROOT_PASSWORD=restapp \
          	    -e MYSQL_DATABASE=user_db \
         	    -e MYSQL_USER=restuser \
          	    -e MYSQL_PASSWORD=restpass \
          	    -p 3306:3306 \
	    -v mysql_data:/var/lib/mysql \
          	    mysql:8.0
        	sleep 15  # wait for MySQL to start up
        	'''
	   }
         }

        stage('Run rest_app.py') {
            steps {
                sh '''
                    # Activates the virtual environment.
                    . ${VENV_DIR}/bin/activate

	      # Runs rest_app.py in the background and logs output to rest_app.log.
                    nohup python3 rest_app.py > rest_app.log 2>&1 &

	      # Wait for the backend service to be available (check every 2 seconds for up to 30 seconds)
                    counter=0
                    while ! curl -s 127.0.0.1:5000 > /dev/null && [ $counter -lt 15 ]; do
                        echo "Waiting for backend to be available..."
                        sleep 2
                        counter=$((counter + 1))
                    done

	     # If the backend does not start, the script fails the pipeline.
                    if [ $counter -eq 15 ]; then
                        echo "Backend did not start in time."
                        exit 1
                    fi

	     # if the backend started and runs successfully it will print the following.
                    echo "Backend is up and running."
                '''
            }
        }

        stage('Run backend_testing.py') {            // Runs unit tests or API tests for the backend using backend_testing.py.
            steps {
                sh """
                    . ${VENV_DIR}/bin/activate
                    python3 backend_testing.py
                """
            }
        }

        stage('Run clean_environment.py') {     //Runs clean_environment.py to stop both backend servers of the rest app flask server.
            steps {
                script {
                    sh """
                        . ${VENV_DIR}/bin/activate
                        python3 clean_environment.py
                    """
                }
            }
        }

        stage('Build Docker Image') {	            // Build an image of the rest app server.
            steps {
                sh 'docker build -t rest-app-server .'
            }
        }

        stage('Push Docker Image & Set Image Version') {
	// This stage logs into Docker Hub securely, tags the Docker image with the current build ID, and pushes it to your Docker Hub account under the name walaahij/rest-app-server:<build_id>.
            steps {
                script {

	     // withCredentials sets docker username and password to temporary environment variables, DOCKER_USER and DOCKER_PASSWORD.
	     // These variables are only available inside this block — keeps them secure.

                    withCredentials([usernamePassword(credentialsId: 'docker-username', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''
		# Here the image is being tagged with build id, after I access docker personal hub, and then the image is pushed to docker.
                            echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USER} --password-stdin
                            docker tag rest-app-server:latest walaahij/rest-app-server:${BUILD_ID}
                            docker push walaahij/rest-app-server:${BUILD_ID}
                        '''
                    }
                }
            }
        }

        stage('Check & Install Docker-Compose') {                         // This stage ensures Docker Compose is installed properly and uses the latest version.
            steps {
                sh '''

	      # Checks if docker-compose is already installed.
	      # If yes, it removes the old binary from both common paths.

                    if command -v docker-compose &> /dev/null; then
                        echo "Docker Compose found. Removing existing version..."
                        sudo rm -f /usr/local/bin/docker-compose
                        sudo rm -f /usr/bin/docker-compose
                    else
                        echo "Docker Compose not found."
                    fi

	      # Now it installs Docker compose.
                    echo "Installing Docker Compose..."

	      # uname -m returns the machine architecture, it stores it 
	      # in the variable ARCH, so docker-compose in the right binary can be downloaded.
                    ARCH=$(uname -m)

	      # $(uname -s) gives the righ Operating System
                    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$ARCH" -o /usr/local/bin/docker-compose
                    
                    #Making the downloaded file executable
	      sudo chmod +x /usr/local/bin/docker-compose

	     # In the next line I create a symbolic link (shortcut) in /usr/bin so I can run docker-compose from anywhere.
	     #|| true ensures this command won’t break the script even if the link already exists or fails.
                    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose || true
                '''
            }
        }

        stage('Docker Compose stage') {
            steps {
                script {
                    // Substitute the BUILD_ID into the docker-compose.yml file before running
                    sh '''
                        # Remove manually started MySQL container if exists
                        docker rm -f my-mysql-container || true
	    
    	          # Kill any process that is using port 5000 on the host
                        sudo fuser -k 5000/tcp || true

                        # Replace image tag in docker-compose.yml
	          sed -i "s|BUILD_ID_PLACEHOLDER|${BUILD_ID}|g" docker-compose.yml

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

	          # Here I try to curl the app to which the flask server should be running,
	          # If the service is not available yet, it waits 2 seconds, then tries again, 
	          # till the server is up and running.
                        until curl -s http://localhost:5000 > /dev/null || [ $counter -ge 15 ]; do
                            echo "Waiting for service to be available on port 5000..."
                            sleep 2
                            counter=$((counter + 1))
                        done

	          # but if it did not run properly after 15 times of trying it will give a message.
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
	  // Here I ran the backend testing to test the sql container that i ran and the docker image that I pulled from docker HUB.
                sh '''
                    echo "Running backend tests inside Docker Compose..."
                    docker-compose exec rest_app python3 backend_testing.py
                '''
            }
        }

        stage('Docker Compose Down & Remove Image') {
            steps {
        	sh '''

	      # Now, all the services that is defined in docker compose stops.
	      # it also removes all the vlumes that is defined in docker-compose.
	      # --remove-orphans: it removes all the containers that are not defined in the docker compose file.
            	      echo "Stopping and removing Docker Compose services..."
            	      docker-compose down --volumes --remove-orphans

            	      echo "Forcing removal of remaining containers..."
            	      # Remove the REST app container with the BUILD_ID tag and the MySQL container
            	      docker rm -f rest-app-server-${BUILD_ID} my-mysql-container || true

	      # Force-removes the Docker image rest-app-server from the local image cache.
            	      echo "Removing Docker image rest-app-server..."
            	      docker rmi -f rest-app-server || true
        	'''
    	}
          }
        // === Kubernetes via Helm ===
        stage('Verify Kubernetes Access') {
    	steps {
       	      sh '''
            	       echo "Checking Kubernetes cluster accessibility..."
                     export KUBECONFIG=$HOME/.kube/config
                     kubectl cluster-info
        	      '''
    	}
         }

         stage('Install Helm') {
    	steps {
        	      sh '''
            	      echo "Installing Helm..."
            	      curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
        	       '''
    	}
          }
        
         stage('Deploy Helm Chart') {
    	steps {
        	     sh '''
            	     export KUBECONFIG=$HOME/.kube/config
	     helm upgrade --install rest-app-server ./my-helm-chart \
                	--set image.repository=walaahij/rest-app-server \
                	--set image.tag=${BUILD_ID}
        	      '''
    	}
          }

         stage('Port Forward Service & Write URL') {
    	steps {
        	   script {
            		sh '''
                	export KUBECONFIG=$HOME/.kube/config
                	pkill -f "kubectl port-forward" || true

                	# Forward port 80 in service to localhost:5001
                	nohup kubectl port-forward svc/hello-python-service 5001:80 > portforward.log 2>&1 &

                	# Wait until the port becomes available
                	for i in {1..10}; do
                    	    nc -z localhost 5001 && break
                    	    echo "Waiting for port-forward to become ready..."
                    	    sleep 2
                	done

                	echo "http://localhost:5001" > k8s_url.txt
            		'''
        	    }
    	}
         }
        
        stage('Kubernetes Backend Test') {
    	environment {
        	         DB_HOST = 'localhost'
       	         DB_PORT = '3306'
        	         DB_USER = 'restuser'
         	         DB_PASSWORD = 'restpass'
        	         DB_NAME = 'user_db'
    	}
    	steps {
        		sh '''
            		. ${VENV_DIR}/bin/activate
            		python3 K8S_backend_testing.py
        		'''
    	}
         }
     
       stage('Clean HELM Environment') {
    	steps {
        	       sh 'helm delete rest-app-server || true'
    	}
         }
    }
}