En tu máquina:

aws cli

eksctl

kubectl

helm

Y en AWS:

Un user/role con permisos para EKS 

Región definida (ej. us-east-1)

Comandos base de arranque:

aws sts get-caller-identity
aws configure list
eksctl version
kubectl version --client
helm version