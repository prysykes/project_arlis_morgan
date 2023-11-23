#!/bin/bash
# Sync ipynb from sagemaker dir to given s3 bucket every min.
#
S3NB="mlwb-nbks/emmy"
date
echo "------------------------------------------------------------"
echo "Syncing notebooks from /home/ec2-user/SageMaker/ to S3 (${S3NB})" 
aws s3 sync /home/ec2-user/SageMaker/ s3://${S3NB}/  --exclude 'Untitled*.*' --exclude '.sparkmagic/*' --exclude '.ipynb_checkpoints/*'
echo "------------------------------------------------------------"
