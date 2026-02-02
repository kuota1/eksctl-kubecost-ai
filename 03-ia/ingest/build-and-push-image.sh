docker build -t chroma-ingest:latest .

export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo $ACCOUNT_ID

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com

aws ecr describe-repositories --repository-names chroma-ingest --region us-east-1 >/dev/null 2>&1 \
  || aws ecr create-repository --repository-name chroma-ingest --region us-east-1

docker tag chroma-ingest:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/chroma-ingest:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/chroma-ingest:latest
