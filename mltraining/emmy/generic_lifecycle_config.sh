#!/bin/bash

set -e

if [ "s3://mlwb-scripts/emmy/sagemaker_inst_bootstrap.sh" != "s3://" ]; then
  echo "Running user defined bootstrap script..."
  aws s3 cp s3://mlwb-scripts/emmy/sagemaker_inst_bootstrap.sh user_bootstrap.sh
  exitCode=$?
  if [ $exitCode -ne 0 ]; then
    echo "ERROR: Could not download user defined bootstrap script. Make sure it exists and permissions are correct."
    exit $exitCode
  else
    chmod +x user_bootstrap.sh
    sudo yum install -y dos2unix
    wait
    dos2unix user_bootstrap.sh
    bash ./user_bootstrap.sh |& tee /tmp/user_bootstrap.log &
  fi
else
  echo "No user-defined bootstrap script provided. Skipping.."
fi

