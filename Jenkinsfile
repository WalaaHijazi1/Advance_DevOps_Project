pipeline {
    //This tells Jenkins to run the pipeline on any available node (agent).
    agent any
    options {         //This block defines pipeline options.
        buildDiscarder(logRotator(daysToKeepStr: '5', numToKeepStr: '20'))
        // Controls how many old builds Jenkins keeps.
        // daysToKeepStr: '5' → Jenkins will delete builds older than 5 days.
        // numToKeepStr: '20' → Jenkins will keep a maximum of 20 builds, even if they are recent.
    }

     triggers {
    	// Runs every 30 minutes regardless of SCM changes
    	cron('H/30 * * * *')
	}

    environment {
        VENV_DIR = "venv"  // Define virtual environment directory
    }

    stages {
        stage('Clone Repository') {
            steps {
	// This stage clones the repository from GitHub into the Jenkins workspace.
	// It uses Git credentials (github-pat) for authentication.
	// It checks out the main branch.
	// Cloning the repository every time we run Jenkins file ensures Jenkins has the latest code before running the pipeline.

                git credentialsId: 'my_secret_token', url: 'https://github.com/WalaaHijazi1/Advance_DevOps_Project.git', branch: 'main'
            }
        }

        stage('Update Repository') {
            steps {
	 // If a previous build modified the repository, this ensures a fresh and clean state.
        	 sh """
               git fetch --all                              # Fetches all branches and updates remote-tracking branches.
               git reset --hard origin/main       #  Ensures the local repository is in sync with the remote repository.
        	"""
    	}
         }

        stage('Install Dependencies') {
            steps {
        	script {      
 	 // Remove existing venv to avoid corruption or permission issues
            	sh "rm -rf ${VENV_DIR}"
            	// Create a fresh virtual environment
            	sh "python3 -m venv ${VENV_DIR}"
            	// Activate and install dependencies
            	sh """
                . ${VENV_DIR}/bin/activate
                pip install -r requirements.txt
            """
    	    	}
    	}
         }
        stage('Run rest_app.py') {
            steps {
                sh '''
            	      . ${VENV_DIR}/bin/activate        # Activates the virtual environment.

	     nohup python3 rest_app.py > rest_app.log 2>&1 &       # Runs rest_app.py in the background and logs output to rest_app.log.
            
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
        stage('Run backend_testing.py') {       // Runs unit tests or API tests for the backend using backend_testing.py.
            steps {
                sh """
                    . $VENV_DIR/bin/activate
                    python3 backend_testing.py
                """
            }
        }
        stage('Run frontend_testing.py') {        // Runs unit tests or UI tests for the frontend using frontend_testing.py.
            steps {
                sh """
                    . $VENV_DIR/bin/activate
                    python3 frontend_testing.py
                """
            }
        }
        stage('Run clean_environment.py') {     //Runs clean_environment.py to stop both backend and frontend servers.
            steps {
                 script {
            		sh """
                    	.  $VENV_DIR/bin/activate              # Activates the virtual environment.
            		# Stop the backend and frontend servers
            		python3 clean_environment.py
            			"""
       		 }
   	       }
	    }
	stage('Build Docker Image'){
	   steps{
		sh 'docker build -t rest-app-server .'
	    }
	}
	stage('Run Docker Image'){
	  steps{
	       sh """
		docker rm -f rest-app-server-{$env.BUILD_ID} || true
		docker run -d -name rest-app-server-{$env.BUILD_ID} -p 5000:5000
			"""
	   }
	}
        stage('Push Docker Image & Set Image Version'){
	   steps{
	     script{
		withCredentials([usernamePassword(
			credentialsId: 'docker_username',
			usernameVariable: 'DOCKER_USER',
			passwordVariable: 'DOCKER_PASSWORD'
				)])   {
			sh """
			echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin        #Accessing Docker using --password-stdin ensures the password won't be exposed in the process.
			docker tag rest-app-server:latest walaahij/rest-app-server:${env.BUILD_ID}
			docker push walaahij/rest-app-server:${env.BUILD_ID}
			"""
		}
	      }
	}
    }
       stage('Check & Install Docker-Compose'){
	  steps{
	     sh """
		if ! command -v docker-compose &> /dev/null; then
		    echo "Docker Compose not found. Installing..."
		    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    sudo chmod +x /usr/local/bin/docker-compose
                    sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
		    echo "Docker Compose Installed ..."
		else
		    echo "Docker Compose is already installed ..."
		fi
	     """
	}
    }
       stage('Docker Compose stage'){
	  steps{
		sh 'docker-compose up -d --build'
      }
   }
      stage('Wait for Docker-Compose'){
	 script{
	            sh """
            echo "Waiting for Docker Compose services to be up..."

            # Try hitting the main service on localhost:5000 (or change to whatever your target service is)
            counter=0
            until curl -s http://localhost:5000 > /dev/null || [ \$counter -ge 15 ]; do
                echo "Waiting for service to be available on port 5000..."
                sleep 2
                counter=\$((counter + 1))
            done

            if [ \$counter -ge 15 ]; then
                echo "Service did not become available in time. Failing build."
                exit 1
            fi

            echo "Service is up and running."
        """
	}
     }
      stage('Docker Compose Test') {
   	 steps {
        	sh """
            	echo "Running backend tests inside Docker Compose..."
            	docker-compose exec app python3 backend_testing.py

            	echo "Running frontend tests inside Docker Compose..."
            	docker-compose exec app python3 frontend_testing.py
       		 """
         }
      }
       stage('Docker Compose Down & Remove Image') {
	  steps {
        	sh """
            	echo "Stopping and removing Docker Compose services..."
            	docker-compose down --volumes --remove-orphans

            	echo "Removing Docker image rest-app-server..."
            	docker rmi -f rest-app-server || true
        	"""
    	}
      }
   }
}
