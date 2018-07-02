#!/usr/bin/env python3

import boto3
import sys

def find_repository(client, repo_name):
	try:
		response = client.describe_repositories(repositoryNames=[repo_name])
		return True
	except client.exceptions.RepositoryNotFoundException:
		return False

def create_repository(client, repo_name):
	response = client.create_repository(repositoryName=repo_name)
	return True

if __name__ == "__main__":
	try:
		repo_name = sys.argv[1]
	except IndexError:
		print("Usage: create_repo <repo_name>")
		sys.exit(1)

	client = boto3.client('ecr')
	if not find_repository(client, repo_name):
		create_repository(client, repo_name)
	else:
		print("{} already exists.".format(repo_name))
