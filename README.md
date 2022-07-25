# diary manager alpha 2

#
# Build and deploy
#
Command to build the application. PLease remeber to change the project name and application name
```
gcloud builds submit --tag gcr.io/diary-manager-alpha2/sttest2  --project=diary-manager-alpha2 
```

Command to deploy the application
```
gcloud run deploy --image gcr.io/diary-manager-alpha2/sttest2 --platform managed  --project=diary-manager-alpha2 --allow-unauthenticated
```

