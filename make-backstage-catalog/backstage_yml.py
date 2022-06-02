#!/usr/bin/env python3
'''Script to generate a Backstage catalog-config.yaml file from a meta.yaml file.'''

import os
import argparse
import yaml
from mergedeep import merge, Strategy
from github import Github


class CreateBackstageConfig():
    '''Class that does all of the things to generate Backstage catalog-config.yaml'''

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Metadata to Backstage config conversion tool.')
        self.parser.add_argument(
            '-r', '--repo',
            help='Name of repository you would like to pull metadata from.', required=False)
        self.parser.add_argument(
            '-y', '--yaml', help='Raw meta yaml contents.', required=False)
        self.args = self.parser.parse_args()
        
        self.data = {}
        self.catalog_yaml = {}
        self.catalog_component = {}
        self.catalog_docs = []
        self.final_yaml = []
        self.component = {}
        self.depends = {}
        self.merged_components = {}

    def run(self):
        '''Runs the things'''

        #Pull remote yaml
        if self.args.repo:
            self.data = self.get_remote_meta_yaml(self.args.repo)
        #Use meta yaml contents passed in as arg
        elif self.args.yaml:
            self.data["meta_yaml"] = yaml.safe_load(self.args.yaml)

        #Use local meta.yaml file + parse local catalog-info.yaml
        else:
            print("No repo specified. Using local meta.yaml.")
            self.data = self.get_local_meta_yaml()
            if os.path.exists('./catalog-info.yaml'):
                self.catalog_yaml = self.get_local_catalog_yaml()
                self.catalog_component, self.catalog_docs = self.parse_catalog_yaml(self.catalog_yaml)

        #Parse meta yaml data
        if self.data:
            self.component = self.generate_component(self.data["meta_yaml"])
            self.depends = self.generate_depends(self.data["meta_yaml"]["ndustrial"]["depends"])
            self.component["spec"]["dependsOn"] = self.depends

        #Merge catalog-info.yaml with meta.yaml
        if self.catalog_component:
            self.merged_components = self.merge_components(self.catalog_component, self.component)

        #Merge component and docs
        if self.catalog_docs:
            self.final_yaml.append(self.merged_components)
            for i in self.catalog_docs:
                self.final_yaml.append(i)

        with open(r'./catalog-info.yaml', 'w') as file:
            yaml.dump_all(self.final_yaml, file)


    def get_remote_meta_yaml(self, repo):
        '''Build meta yaml dir'''
        yml = {}
        # Get file and return conents
        res = self.github_get_file(repo, "/", "meta.yaml")

        if res:
            yml = self.parse_meta_yaml(res)

        return {"meta_yaml": yml}

    def get_local_meta_yaml(self):
        '''Function to get a local meta.yaml file'''
        yml = {}

        res = open("./meta.yaml", 'r')

        if res:
            yml = self.parse_meta_yaml(res)

        return {"meta_yaml": yml}

    def parse_meta_yaml(self, meta):
        '''Function to parse a local meta yaml contents into yaml object'''
        keys = ["name", "organization", "owner",
                "managed_by", "project", "type", "depends"]

        yml = yaml.safe_load(meta)

        #Loop through keys to and set to none if does not exist
        for i in yml:
            if i == "ndustrial":
                for j in keys:
                    if yml["ndustrial"].get(j) is None:
                        yml["ndustrial"][j] = None

        return yml

    def parse_catalog_yaml(self, catalog):
        '''Function to parse a pre-existing catalog-info.yaml'''
        docs = []
        for i in yaml.safe_load_all(catalog):
            if i["kind"] == "Component":
                component = i
            else:
                docs.append(i)
        return component, docs

    def get_local_catalog_yaml(self):
        '''Function to read a local catalog-info.yaml'''

        res = open("./catalog-info.yaml", 'r')

        return res

    def generate_component(self, meta):
        '''Create a Backstage component object based on meta.yml contents'''
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

    def generate_depends(self, meta_depends):
        '''Create depends array from the depend field in meta.yml'''
        depends_on_list = []
        for dependency in meta_depends:
            if "project" in dependency:
                env = dependency.get("env", "default")
                depends_on_list.append(f"component:{env}/{dependency['name']}")
            if "external" in dependency:
                env = dependency.get("env", "default")
                depends_on_list.append(f"resource:{env}/{dependency['name']}")
        return depends_on_list

    def merge_components(self, catalog, meta):
        '''Run deepmerge to capture diffs from catalog-info and meta'''
        res = merge({}, meta, catalog, strategy=Strategy.ADDITIVE)
        return res

    def github_get_file(self, repo, path, f_name):
        '''(UNUSED) Check repo for file and return contents of file'''
        
        github_connection = self.github_auth()

        try:
            res = github_connection.get_repo(repo)
        except Exception as github_error:
            print(f"Unable to get repo: {repo}\nError: {github_error}")
            return None

        #Check if f_name file exists in root dir of repo
        if f_name in [i.path for i in res.get_contents(path)]:
            file_content = res.get_contents(f_name)
            return file_content.decoded_content.decode()

        print(f"{f_name} not found in path of {path}")

        return None

    def github_auth(self):
        '''(UNUSED) Authenticate to github using local GITHUB_TOKEN env'''
        if os.getenv('GITHUB_TOKEN') is None:
            print("GITHUB_TOKEN env variable not set. Please set and re-run script.")
            return None

        token = os.getenv('GITHUB_TOKEN')
        return Github(token)

if __name__ == '__main__':
    CreateBackstageConfig().run()
