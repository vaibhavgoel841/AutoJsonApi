#!/bin/bash

name=$1
base=$2 

echo Creating virtual environment

python3 -m venv env

echo Created virtual enviornment

. env/bin/activate

echo Activated virtual enviornment

pip3 install django==4.1.2

echo Installed django successfully

pip3 install click==7.0

echo Installed click successfully

pip3 install djangorestframework

echo Installed djangorestframework successfully

django-admin startproject $name

echo Starting project $name

mv env/ $name/

echo Moved virtual enviornment to $name

cd $name/

python3 manage.py startapp $base

echo Started new App $base

echo Writing to $base/urls.py
echo "urlpatterns=[]" > $base/urls.py

python3 manage.py makemigrations

echo Converted python models to SQL classes

echo Creating database

python3 manage.py migrate
