#!/usr/bin/env python3

from kubernetes import client, config
import logging as log
import yaml
import re
import semver
import functools
from dxf import DXF

class ImageSpec:

    LEGACY_REGISTRY_HOST = "index.docker.io"
    DEFAULT_REGISTRY_HOST = "registry.hub.docker.com"

    def __init__(self, rawspec):
        self.host=None
        self.prefix=None
        self.tag=None

        self.repo=rawspec

        # Image contains a tag?
        if ":" in self.repo:
            self.repo, self.tag = self.repo.rsplit(":",1)
        
        # Repo contains a prefix?
        if "/" in self.repo:
            self.prefix, self.repo = self.repo.rsplit("/",1)
        
        # prefix contains a host?
        if self.prefix is not None and "/" in self.prefix:
            self.host, self.prefix = self.repo.rsplit("/",1)

    def __str__(self):
        return self.shortspec()
    
    def fullhost(self):
        if self.host is None or self.host == self.LEGACY_REGISTRY_HOST:
            return self.DEFAULT_REGISTRY_HOST
        return self.host

    def fullprefix(self):
        if self.prefix is None and self.fullhost() == self.DEFAULT_REGISTRY_HOST:
            return "library"
        return self.prefix

    def fullrepo(self):
        repo=self.repo
        prefix=self.fullprefix()
        if prefix is not None:
            repo=prefix+"/"+repo
        return repo

    def fulltag(self):
        if self.tag is None:
            return "latest"
        return self.tag

    def shortspec(self):
        return self.create_spec(self.host,self.prefix,self.repo,self.tag)

    def fullspec(self):
        return self.create_spec(self.fullhost(),self.fullprefix(),self.repo,self.fulltag())

    def create_spec(self,host,prefix,repo,tag):
        spec=repo
        if prefix is not None:
            spec=prefix+"/"+spec
        if host is not None:
            spec=host+"/"+spec
        if tag is not None:
            spec=spec+":"+tag
        return spec


def fail(message):
    print(message)
    exit(1)

def main():
    log.basicConfig(level=log.INFO)

    try:
        config.load_kube_config()
    except:
        fail("Unable to load kube config")
    
    appsv1 = client.AppsV1Api()
    ret = appsv1.list_deployment_for_all_namespaces(watch=False,label_selector="autoupdate/enabled==true")
    for item in ret.items:
        check_update("Deployment",item)

def registry_auth(dxf, response):
    dxf.authenticate(response=response)


def find_current_tag(image,config):
    registry=DXF(image.fullhost(),image.fullrepo(),registry_auth)
    # FIXME: fail if check fails
    #print(registry.api_version_check())
    p=re.compile(config["tag"])
    candidates=[]
    for tag in registry.list_aliases(iterate=True):
        if p.match(tag):
            candidates.append(tag)
    if len(candidates)==0:
        return None

    # more than one? sort by semver, highest 1st
    if len(candidates)>1:
        candidates=sorted(candidates,reverse=True,key=functools.cmp_to_key(semver.compare))
    
    return candidates[0]

def check_update(kind,item):
    if "autoupdate/config" not in item.metadata.annotations:
        log.warning("Missing annotation 'autoupdate/config' in %s %s"%(kind.lower(),item.metadata.name))
        return

    try:
        configs=yaml.load(item.metadata.annotations["autoupdate/config"],Loader=yaml.BaseLoader)
    except:
        log.exception("Unable to parse yaml config from %s '%s'"%(kind.lower(),item.metadata.name))
        return
    
    log.info("Checking %s '%s' for containers to update"%(kind.lower(),item.metadata.name))

    for container in item.spec.template.spec.containers:
        if container.name not in configs:
            continue
        config=configs[container.name]
        if type(config) is str:
            config={ "tag": config}
        
        if "tag" not in config:
            log.warning("Missing 'tag' in %s '%s' config for container '%s'"%(kind.lower(),item.metadata.name,container.name))
            return

        log.info("Checking tag for container '%s'"%container.name)
        image=ImageSpec(container.image)
        current_tag=find_current_tag(image, config)
        if current_tag is None:
            log.warning("Found no tag for container '%s' that matches '%s'"%(container.name,config["tag"]))
            continue
        if current_tag==image.fulltag():
            log.info("Container '%s' with tag '%s' is up-to-date"%(container.name,image.fulltag()))
            continue

        log.info("Container '%s' needs update from tag '%s' to '%s'"%(container.name,image.fulltag(),current_tag))


if __name__== "__main__":
    main()