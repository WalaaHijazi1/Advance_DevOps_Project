//2. Parameterized build:
// Read about “Parameterized build” https://wiki.jenkins.io/display/jenkins/parameterized+build
// Create another pipeline with the same steps as the previous pipeline and disable
//poll scm mechanism (the new pipeline will be triggered manually only.
//E.g: “build now” button).
// The pipeline will get an int parameter which will cause the below modes:
//o In case the int value is 1 – only frontend_testing.py will run.
//o In case the int value is 2 – only backend_testing.py will run.
//o In case the int value is 3 – only combined_testing.py will run.
// Default int value will be 3.



pipeline {
    agent any
    parameters {
        string(name: 'TEST_MODE', defaultValue: '3', description: '1 - Frontend, 2 - Backend, 3 - Combined')
    }
    environment {
        VENV_DIR = "venv"  // Define virtual environment directory
    }
    stages {
        stage('Clone Repository') {
            steps {
                git credentialsId: 'github-pat', url: 'https://github.com/WalaaHijazi1/Advance_DevOps_Project.git', branch: 'Jenkins-ParameterizedBuild'
            }
        }
        stage('Setup Virtual Environment') {
            steps {
                 script {
	            sh '''
	                python3 -m venv ${VENV_DIR}
	                . ${VENV_DIR}/bin/activate
	                pip install -r requirements.txt
            		'''
        		}
    	        }
	}
         stage('Run Tests') {
            steps {
                script {
                    def test_script = ""
                    if (params.TEST_MODE == '1') {
                        test_script = "frontend_testing.py"
	          server_name = "web_app.py"
	          port = "5001"
                    } else if (params.TEST_MODE == '2') {
                        test_script = "backend_testing.py"
	          server_name = "rest_app.py"
	          port = "5000"
                    } else {
                        test_script = "combined_testing.py"
	          server_name = "rest_app.py"
	          port = "5000"
                    }
            		sh """
            	      	. ${VENV_DIR}/bin/activate
            	      	nohup python3 {server_name} &  # Start rest_app.py in the background
            
             	     	# Wait for the backend service to be available (check every 2 seconds for up to 30 seconds)
            	     	counter=0
            	    	 while ! curl -s 127.0.0.1:${port} > /dev/null && [ $counter -lt 15 ]; do
                		echo "Waiting for backend to be available..."
                		sleep 2
                		counter=$((counter + 1))
                   	done
            
            	     	if [ $counter -eq 15 ]; then
                		echo "Backend did not start in time."
                		exit 1
            	     	fi
                    	echo "Backend is up and running."

                	python3 ${test_script}
            		"""
                }
            }
        }
    }
}