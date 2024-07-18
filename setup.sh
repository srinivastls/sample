#!/bin/bash

# Install Java
sudo apt-get update
sudo apt-get install -y openjdk-8-jdk

# Set JAVA_HOME environment variable
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

