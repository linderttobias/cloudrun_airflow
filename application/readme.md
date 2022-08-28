
### Local Developement

1. Authenticate to GCloud:  
    ``gcloud auth application-default login``
2. Run app locally:  
`poetry install`  
`poetry run python main.py --bucket_name experimentplanet`


### Containerization

1. Build:   
``docker build -t simpleapp . ``


### Create Artifact Registry Project and Tag/Push image

1. Authenticate CLI:  
``gcloud auth login``
2. Set Up Vars:  
````
PROJECT=...
REPO_NAME=testrepo
LOCATION=europe-west1
LABELS="owner=me,project=testing"
DESCRIPTION="Repository for Testing"
APP=simpleapp
```` 
3. Create Artifact Registry Repository:
````
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$LOCATION \
    --labels=$LABELS \
    --description=$DESCRIPTION \
    --project=$PROJECT
````
4. Check & set up docker:  
````
gcloud artifacts repositories describe $REPO_NAME --location $LOCATION
gcloud auth configure-docker $LOCATION-docker.pkg.dev
````
5. Tag and push Image to Artifact Registry:
```
docker tag $APP $LOCATION-docker.pkg.dev/$PROJECT/$REPO_NAME/$APP:latest
docker push $LOCATION-docker.pkg.dev/$PROJECT/$REPO_NAME/$APP:latest`
```