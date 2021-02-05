# Build layer
rm aws-layer.zip
rm aws_requirements.txt
poetry export -f requirements.txt --without-hashes --output aws_requirements.txt
docker rmi aws -f
docker build -f DockerfileAWS -t aws .
id=$(docker create aws:latest)
docker cp $id:/app/aws.zip aws-layer.zip

# Build lambda
rm -rf aws
rm aws.zip
mkdir aws
cp -r quote_bot aws/
cp lambda_function.py aws/
cd aws
zip -r ../aws.zip .
cd ..