#!/usr/bin/env python2.7
# -*- coding: utf8 -*-

import requests
import argparse
import os
import base64
import yaml
import sys
import ConfigParser as configparser
from giturlparse import parse

class ServiceFinder:
    def __init__(self, base_url):
        self.url = base_url
    
    def create_service(self, service_name, auth_header, service_title=None, service_status=None, repo=None, lib_repos=None):
        url = "%s/v1/services" % (self.url)
        create_params = {'name':service_name}
        if service_title:
            create_params['title'] = service_title
        if service_status:
            create_params['status'] = service_status
        if repo:
            create_params['repo'] = repo
        if lib_repos:
            create_params['lib-repos'] = lib_repos
        resp = requests.post(url, 
            json=create_params, 
            headers={'Authorization':'Bearer '+auth_header}
        )
        resp.raise_for_status()
        return resp.json().get('data')

    def update_service(self, service_name, auth_header, service_title=None, service_status=None, repo=None, lib_repos=None):
        url = "%s/v1/services/%s" % (self.url, service_name)
        update_params = {'name':service_name}
        if service_title:
            update_params['title'] = service_title
        if service_status:
            update_params['status'] = service_status
        if repo:
            update_params['repo'] = repo
        if lib_repos:
            update_params['lib-repos'] = lib_repos
        resp = requests.put(url, 
            json=update_params, 
            headers={'Authorization':'Bearer '+auth_header}
        )
        resp.raise_for_status()
        return resp.json().get('data')
    
    def upload_document_content(self, service_name, directory, filename, content_type, auth_header):
        url = "%s/v1/services/%s/docs" % (self.url, service_name)

        with open(os.path.join(directory, filename)) as f:
            content = f.read()
            resp = requests.post(url, 
                json={
                    'name':filename, 
                    'content-type':content_type,
                    'content':base64.b64encode(content.encode('utf-8')).decode('utf-8')
                    }, 
                headers={'Authorization':'Bearer '+auth_header}
            )
            resp.raise_for_status()
            return resp.json().get('data')


def get_git_repo(path):
    config_path = os.path.join(path, '.git/config')
    if not os.path.exists(config_path):
        raise Exception("couldn't find .git/config in root")

    config = configparser.ConfigParser()
    config.read(config_path)
    git_url = config['remote "origin"'].get('url')
    parsed_git_url = parse(git_url)
    ssh_url = parsed_git_url.url2ssh
    return ssh_url

def get_docker_env(docker_path):
    env = {}
    if not os.path.exists(docker_path):
        raise Exception("couldn't find "+docker_path)

    with open(docker_path, "r") as stream:
        try:
            y = yaml.load(stream)
            if len(y.keys()) != 1:
                raise Exception("expect 1 root key in file")
            service_root = list(y.keys())[0]
            if 'environment' not in y[service_root]:
                raise Exception("expect environment to be present in first level of file")

            for e in y[service_root]['environment']:
                (k,v) = e.split("=", 1)
                env[k] = v
        except yaml.YAMLError as exc:
            raise exc
    return env

def get_jwt():
    params = {"scope":"openid app_metadata"}
    for k in ['connection', 'client_id', 'username', 'password', 'url']:
        env_key = "AUTH_"+k.upper()
        v = os.environ.get(env_key)
        if v is None:
            raise Exception("missing environment variable ",env_key)
        params[k] = v
    resp = requests.post(params['url'], json=params)
    resp.raise_for_status()
    return resp.json()['id_token']

def main(params):
    try:
        jwt = get_jwt()
    except Exception as e:
        print("Unable to retrieve JWT:", e)
        sys.exit(1)
    
    service_path = os.path.abspath(params.servicepath)
    git_path = os.path.abspath(params.gitpath)

    ### Get info from the docker compose file (we need the service name, and optionally the status route)
    try:
        docker_env = get_docker_env(os.path.join(service_path, params.dockerfile))
    except Exception as e:
        print("Unable to obtain docker environment:", e)
        sys.exit(1)

    if 'SERVICE_NAME' not in docker_env:
        print("SERVICE_NAME not in docker environment:", e)
        sys.exit(1)
    service_name = docker_env['SERVICE_NAME']

    service_status = None
    if 'SERVICE_80_CHECK_HTTP' not in docker_env:
        print("SERVICE_80_CHECK_HTTP not in docker environment:", e)
    else:
        service_status = docker_env['SERVICE_80_CHECK_HTTP']

    ### Try to get the git url (optional)
    git_ssh_url = None
    try:
        git_ssh_url = get_git_repo(git_path)
    except Exception as e:
        print("Unable to obtain git url, skipping:", e)

    service_finder = ServiceFinder(params.sfs_url)
    try:
        # Attempt to create the service
        service_finder.create_service(service_name, jwt, service_status=service_status, repo=git_ssh_url)
    except requests.HTTPError as e:
        if e.response.status_code != 409:
            print("Create failed:", e)
            sys.exit(1)
        elif params.force:
            # Service already exists, and we're forcing an update
            try:
                service_finder.update_service(service_name, jwt, service_status=service_status, repo=git_ssh_url)
            except requests.HTTPError as e:
                print("Forced update failed:", e)
                sys.exit(1)

    # Only searches the root of the folder for now
    for (dirpath, _, filenames) in os.walk(service_path):
        for filename in filenames:
            if filename.endswith('.md'):
                try:
                    service_finder.upload_document_content(service_name, dirpath, filename, 'text/markdown', jwt)
                except requests.HTTPError as e:
                    print("Unable to upload, skipping:", filename, e)
                    continue
        break

def parse_arguments():
    parser = argparse.ArgumentParser(description="Upload service documentation")
    parser.add_argument("sfs_url", help='URL for Service Finder Service')
    parser.add_argument("-s", "--servicepath", help='Path to analyze for documentation', default=os.getcwd())
    parser.add_argument("-g", "--gitpath", help='Path to analyze for repo information', default=os.getcwd())
    parser.add_argument("-d", "--dockerfile", help='Name of docker-compose file (should be in service path)', default="docker-compose-prod.yml")
    parser.add_argument("-f", "--force", help="force update of service with new details if it already exists", action="store_true")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
