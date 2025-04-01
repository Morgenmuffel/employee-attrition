.DEFAULT_GOAL := default
#################### PACKAGE ACTIONS ###################
reinstall_package:
	@pip uninstall -y employee_attrition || :
	@pip install -e .


run_train:
	python -c 'from employee_attrition.interface.main import train; train()'

NUM_SAMPLES = 10

run_predict:
	python -c 'from employee_attrition.interface.main import predict_risk; predict_risk(num_samples=$(NUM_SAMPLES))'

run_evaluate:
	python -c 'from employee_attrition.interface.main import evaluate; evaluate()'

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr employee_attrition-*.dist-info
	@rm -fr employee_attrition.egg-info

# run_train -s will train the model and pickle (save) it
# run_train:
# python -c 'from employee_attrition.interface.main import train; train(save_model=True if "-s" in "$(MAKEFLAGS)" else False)'
 	# python -c 'from employee_attrition.interface.main import train; train()'

run_train_select:
  python -c 'from employee_attrition.interface.main import train_model_with_selection; train_model_with_selection(save=True)'

run_workflow:
	PREFECT__LOGGING__LEVEL=${PREFECT_LOG_LEVEL} python -m taxifare.interface.workflow

run_api:
	uvicorn employee_attrition.api.fast:app --reload


################### LOCAL REGISTRY ################

# Retrieve the user's home directory using Python
# HOME := $(shell python -c "from os.path import expanduser; print(expanduser('~'))")

# LOCAL_REGISTRY_PATH =  ~/.lewagon/data_bpm

# reset_local_files:
# 	rm -rf ${LOCAL_REGISTRY_PATH}
# 	mkdir -p ${LOCAL_REGISTRY_PATH}
# 	mkdir ${LOCAL_REGISTRY_PATH}/training_outputs
# 	mkdir ${LOCAL_REGISTRY_PATH}/training_outputs/models
# 	mkdir ${LOCAL_REGISTRY_PATH}/training_outputs/pipes


run_local_docker_image:
	docker run -e PORT=8000 -p 8080:8000 --env-file .env ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${DOCKER_REPO_NAME}/${DOCKER_IMAGE_NAME}:dev_14

build_docker_image:
	docker build -t ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${DOCKER_REPO_NAME}/${DOCKER_IMAGE_NAME}:dev_14 .

push_docker_image:
	docker push ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${DOCKER_REPO_NAME}/${DOCKER_IMAGE_NAME}:dev_14

run_gcs_docker_image:
	gcloud run deploy --image ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${DOCKER_REPO_NAME}/${DOCKER_IMAGE_NAME}:dev_14 --region ${GCP_REGION} --env-vars-file .env.yaml


reset_local_files:
	rm -rf employee_attrition/training_outputs
	mkdir -p employee_attrition/training_outputs
	mkdir employee_attrition/training_outputs/models
	mkdir employee_attrition/training_outputs/pipes
