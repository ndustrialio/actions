#!/usr/bin/env python3

import os
import sys
import yaml
import argparse
import pprint as pp
from mergedeep import merge, Strategy
from github import Github

class CreateBackstageConfig(object):
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Project metadata to Backstage config  conversion tool.')
        self.parser.add_argument(
            '-r', '--repo', help='Name of repository you would like to pull metadata from.', required=False)
        self.parser.add_argument(
            '-y', '--yaml', help='Raw meta yaml contents.', required=False) 
        self.args = self.parser.parse_args()

    # Runs the things
    def run(self):
        self.data = {}
        self.catalog_yaml= {}
        self.catalog_component = {}

        if self.args.repo:
            self.data = self.get_remote_meta_yaml(self.args.repo)
        elif self.args.yaml:
            self.data["meta_yaml"] = yaml.safe_load(self.args.yaml)
        else:
            print("No repo specified. Using local meta.yaml.")
            self.data = self.get_local_meta_yaml()
            if os.path.exists('./catalog-info.yaml'):
                self.catalog_yaml = self.get_local_catalog_yaml()
                self.catalog_component = self.parse_catalog_yaml(self.catalog_yaml)

        if self.data:
            self.component = self.generate_component(self.data["meta_yaml"])
            self.depends = self.generate_depends(self.data["meta_yaml"]["ndustrial"]["depends"])
            self.component["spec"]["dependsOn"] = self.depends


        if self.catalog_component:
            self.merged_components = self.merge_components(self.catalog_component, self.component)
    
        with open(r'./catalog-info.yaml', 'w') as file:
            catalog = yaml.dump(self.merged_components, file)    

    # Build meta yaml dir
    def get_remote_meta_yaml(self, repo):
        yml = {}
        # Get file and return conents
        res = self.github_get_file(repo, "/", "meta.yaml")

        if res:
            yml = self.parse_meta_yaml(res)

        return {"meta_yaml": yml}

    def get_local_meta_yaml(self):
        yml = {}
        # Get file and return conents
        res = open("./meta.yaml",'r')

        if res:
            yml = self.parse_meta_yaml(res)

        return {"meta_yaml": yml}

    def parse_meta_yaml(self, meta):
        keys = ["name", "organization", "owner",
                "managed_by", "project", "type", "depends"]

        yml = yaml.safe_load(meta)

        # Loop through keys to and set to none if does not exist
        for i in yml:
            if i == "ndustrial":
                for j in keys:
                    if yml["ndustrial"].get(j) is None:
                        yml["ndustrial"][j] = None
        
        return yml
    
    def parse_catalog_yaml(self, catalog):
        for i in yaml.safe_load_all(catalog):
            if i["kind"] == "Component":
                component = i
        return component



    def get_local_catalog_yaml(self):
        component_yml = {}
        # Get file and return conents
        res = open("./catalog-info.yaml",'r')

        return res

 
    # Create a Backstage component object based on meta.yml contents
    def generate_component(self, meta):
        # Create component
        component = {
            "apiVersion": "backstage.io/v1alpha1",
            "kind": "Component",
            "metadata": {
                "name": meta["ndustrial"]["name"],
                "annotations": {
                    "github.com/project-slug": meta["ndustrial"]["project"]
                }
            },
            "spec": {
                "type": meta["ndustrial"]["type"],
                "system": meta["ndustrial"]["project"],
                "lifecycle": "production",
                "owner": meta["ndustrial"]["owner"]
                
            }
        }
        return component

    def generate_depends(self, metaDepends):
        # Create depends array from the depend field in meta.yml
        dependsOnList = []
        for dependency in metaDepends:
            if "project" in dependency:
                env = dependency.get("env", "default")
                dependsOnList.append("component:{}/{}".format(env, dependency["name"]))
            if "external" in dependency:
                env = dependency.get("env", "default")
                dependsOnList.append("resource:{}/{}".format(env, dependency["name"]))
        return dependsOnList

    def merge_components(self, catalog, meta):
        res  = merge({}, meta, catalog, strategy=Strategy.ADDITIVE)
        pp.pprint(res)
        return res

   # (UNUSED) Check repo for file and return contents of file
    def github_get_file(self, repo, path, f_name):
        # Auth to github
        g = self.github_auth()
        # Check if repo exists
        try:
            res = g.get_repo(repo)
        except Exception as e:
            print("Unable to get repo: {}".format(repo))
            return None

        # Check if f_name file exists in root dir of repo
        if f_name in [i.path for i in res.get_contents(path)]:
            file_content = res.get_contents(f_name)
            return file_content.decoded_content.decode()
        else:
            print("{} not found in path of {}".format(
                f_name, path, res.full_name))
            return None

    # (UNUSED) Authenticate to github using local GITHUB_TOKEN env
    def github_auth(self):
        if os.getenv('GITHUB_TOKEN') is None:
            print("GITHUB_TOKEN env variable not set. Please set and re-run script.")
            return None
        else:
            token = os.getenv('GITHUB_TOKEN')
        return Github(token)
    
if __name__ == '__main__':
    CreateBackstageConfig().run()
