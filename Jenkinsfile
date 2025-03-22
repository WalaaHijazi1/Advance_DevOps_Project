pipeline {
    //This tells Jenkins to run the pipeline on any available node (agent).
    agent any
    options {         //This block defines pipeline options.
        buildDiscarder(logRotator(daysToKeepStr: '5', numToKeepStr: '20'))
        // Controls how many old builds Jenkins keeps.
        // daysToKeepStr: '5' → Jenkins will delete builds older than 5 days.
        // numToKeepStr: '20' → Jenkins will keep a maximum of 20 builds, even if they are recent.
    }

    triggers {   //This block defines when the pipeline should run automatically.
        pollSCM('H/30 * * * *')
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

                git credentialsId: 'github-pat', url: 'https://github.com/WalaaHijazi1/Advance_DevOps_Project.git', branch: 'main'
            }
        }

        stage('Update Repository') {
            steps {
	 // If a previous build modified the repository, this ensures a fresh and clean state.
        	 sh '''
               git fetch --all                              # Fetches all branches and updates remote-tracking branches.
               git reset --hard origin/main       #  Ensures the local repository is in sync with the remote repository.
        	'''
    	}
         }

        stage('Install Dependencies') {
            steps {
        	script {      
 	 # Remove existing venv to avoid corruption or permission issues
            	sh "rm -rf ${VENV_DIR}"
            	# Create a fresh virtual environment
            	sh "python3 -m venv ${VENV_DIR}"
            	# Activate and install dependencies
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

        stage('Run web_app.py') {    //This is the frontend server
            steps {
                sh '''
            	      . ${VENV_DIR}/bin/activate                  # Activates the virtual environment.

	      nohup python3 web_app.py > web_app.log 2>&1 &         # Runs web_app.py in the background and logs output to web_app.log.

            
             	     # Wait for the backend service to be available (check every 2 seconds for up to 30 seconds)
            	     counter=0
            	     while ! curl -s 127.0.0.1:5001 > /dev/null && [ $counter -lt 15 ]; do               # Waits for the frontend to start on port 5001 (max 30 seconds).
                	echo "Waiting for backend to be available..."
                	sleep 2
                	counter=$((counter + 1))
                   done
            
            	     if [ $counter -eq 15 ]; then                   # If the frontend does not start, the script fails the pipeline.
                	echo "Backend did not start in time."
                	exit 1
            	     fi
                    echo "Backend is up and running."
        	'''
    	}
         }

        stage('Run backend_testing.py') {       // Runs unit tests or API tests for the backend using backend_testing.py.
            steps {
                sh '''
                    . $VENV_DIR/bin/activate
                    python3 backend_testing.py
                '''
            }
        }

        stage('Run frontend_testing.py') {        // Runs unit tests or UI tests for the frontend using frontend_testing.py.
            steps {
                sh '''
                    . $VENV_DIR/bin/activate
                    python3 frontend_testing.py
                '''
            }
        }

        stage('Run combined_testing.py') {       // Runs end-to-end (E2E) tests using combined_testing.py.
            steps {
                sh '''
                    .  $VENV_DIR/bin/activate
                    python3 combined_testing.py
                '''
            }
        }

        stage('Stop Servers') {     //Runs clean_environment.py to stop both backend and frontend servers.
            steps {
                 script {
            		sh '''
                    	.  $VENV_DIR/bin/activate              # Activates the virtual environment.
            		# Stop the backend and frontend servers
            		python3 clean_environment.py
            	'''
        }
    }
}
    }

}