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
        	script {
           VENV_DIR = 'venv'
           
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
            	      . .myenv/bin/activate
            	      nohup python3 rest_app.py &  # Start rest_app.py in the background
            
             	     # Wait for the backend service to be available (check every 2 seconds for up to 30 seconds)
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
                    .  $VENV_DIR/bin/activate
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
}
