# ˜”*°•.˜”*°• Advance DevOps Project - Kubernetes •°*”˜.•°*”˜
#                  ˜”*°•.˜”*°• Walaa Hijazi •°*”˜.•°*”˜

<p align="center">
  <img src="images/jenkins_K8s_integration.png" alt="jenkins Diagram with K8s" width="450" height="700">
</p>


## Jenkins pipeline explenation:
- The pipeline runs on any available node.
- Before the pipeline I defined an Option block that configures how the pipeline behaves:
   * the block automatically delets old builds and states to delete builds after 5 days, and no more than 20 builds should be saved.
- the trigger block define when the pipeline should start a build, for example in this specific pipeline it starts building every 30 minutes (every hour).
- the 'environment' block defines an environment variable that is used through the pipeline.

### Stages:
- Clean Workspace stage:
   * Clean workspace before pulling fresh repository.
- Clone Repository stage:
   * clonning the git repository with branch name of 'AdvanceProject_K8s_Integration' into Jenkins workspace directory in the host machine of Jenkins, in my case it's a Docker container.
- Update Repostory stage:
   * update all the branches of the clonned repository.
   * ensures the local repository is the same as the remote one (or cloned one).
- Install Dependencies stage:
   * Removes any virtual environment folder.
   * create a new virtual environment folder.
   * activates the virtual environment.
   * install all the dependencies.
- Start MySQL and Init Table stage:
   * remove if there was an sql container.
   * creates an sql docker container.
   * environment variables are passed when the container runs and the port number.
   * creating a volume for MySQL to store its data files persistently.
   * also the volume is mounted from the host machine into the docker container file.
- Run rest_app.py stage:
   * activates the virtual environment.
   * Runs rest_app.py in the background.
   * Wait for the backend service to be available.
   * will return a message, if the backend started or failed.
- Run backend_testing.py stage:
   * activates the virtual environment.
   * Runs the backend_testing.py to test the Flask server functionality.
- Run clean_environment.py stage:
   * activates the virtual environment.
   * Runs clean_environment.py to stop both backend servers of the rest app flask server.
   
**_The explenation of the Docker Compose stages and the testing of the server after creating the server flask container and the sql container is explained in the AdvanceProject_Docker_Integration branch_**

#### Kubernetes Integration via Helm stages:
- Verify Kubernetes Access stage:
   * in this stage, I verify access to a Kubernetes cluster.
   * setting KUBECONFIG as an environment variable that would tells kubectl where is the configuration file of kubernetes is.
   * $HOME/.kube/config is the default path where tools like Minikube or kubectl store cluster credentials and access info.
   * prints details about the Kubernetes cluster, such as:
      * The Kubernetes master (API server) endpoint
      * DNS service and other core components
   * kubectl cluster-info: if this command succeeds, you have access to the cluster and it’s running correctly. If it fails, there may be issues with:
      * Credentials
      * Network access
      * Misconfigured or missing kubeconfig
**_Helm is a Kubernetes package manager. it helps in streamlining the application management by using “Charts” to package the Kubernetes resources. It facilitates simplifying the deployment, upgrades, and dependency resolution within Kubernetes clusters._**
- Install Helm stage:
   * downloads the official Helm installation script from the Helm GitHub repository.
   * | bash: pipes the downloaded script directly into bash to execute it.

#### Helm Chart Folder:
<p align="center">
  <img src="images/Helm_chart_folder.png" alt="helm chart folder map" width="300" height="300">
</p>


- Deploy Helm Chart stage:
   * 