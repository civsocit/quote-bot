rm -rf aws
rm aws.zip
python -m pip install -r aws_requirements.txt --target aws
cp -r quote_bot aws/
cp lambda_function.py aws/

cd aws
zip -9 -r aws.zip .
cd ..
mv aws/aws.zip .
