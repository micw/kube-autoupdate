#!/usr/bin/env python3

from kubernetes import client, config
import logging as log
import yaml
import re
import semver
import functools
from dxf import DXF
import os
import argparse
from time import sleep
from image_spec import ImageSpec

def fail(message):
    print(message)
    exit(1)

def getenv(key,default):
    if key in os.environ:
        return os.environ[key]
    if default is not None:
        return default
    fail("Missing env variable %s"%key)

def main():
    log.basicConfig(level=log.getLevelName(getenv("LOG_LEVEL","INFO")))

    parser = argparse.ArgumentParser(description="Kube autoupdater")
    subparsers = parser.add_subparsers(required=True, dest='action')
    subparsers.add_parser("update",help="Check and execute updates now")
    subparsers.add_parser("schedule",help="Check and execute updates periodically")
    args = parser.parse_args()

    try:
        config.load_kube_config()
    except:
        try:
            config.load_incluster_config()
        except:
            fail("Unable to load kube config or cluster servicerole")

    if args.action=="update":
        run_update()
        quit()

    if args.action=="schedule":
        delay=int(getenv("SCHEDULE_DELAY_MINUTES",60))
        initial_delay=int(getenv("SCHEDULE_INITIAL_DELAY_MINUTES",delay))
        if (initial_delay>0):
            log.info("Sleeping %s minutes"%initial_delay)
            sleep(initial_delay*60)
        while True:
            run_update()
            log.info("Sleeping %s minutes"%delay)
            sleep(delay*60)

def run_update():
    log.info("Looking for deployments to update")
    appsv1 = client.AppsV1Api()
    ret = appsv1.list_deployment_for_all_namespaces(watch=False,label_selector="autoupdate/scheduled==true")
    for item in ret.items:
        patch=check_update_and_create_patch("Deployment",item)
        if patch is not None:
            appsv1.patch_namespaced_deployment(name=item.metadata.name,namespace=item.metadata.namespace,body=patch)
    log.info("All done")


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

def check_update_and_create_patch(kind,item):
    if "autoupdate/config" not in item.metadata.annotations:
        log.warning("Missing annotation 'autoupdate/config' in %s %s"%(kind.lower(),item.metadata.name))
        return

    try:
        configs=yaml.load(item.metadata.annotations["autoupdate/config"],Loader=yaml.BaseLoader)
    except:
        log.exception("Unable to parse yaml config from %s '%s'"%(kind.lower(),item.metadata.name))
        return
    
    log.info("Checking %s '%s' for containers to update"%(kind.lower(),item.metadata.name))

    patches=None

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
        image.tag=current_tag
        if patches is None:
            patches={}
        if not "containers" in patches:
            patches["containers"]=[]
        patches["containers"].append({
            "name": container.name,
            "image": image.shortspec()
        })

    if patches is None:
        return None
    
    return {
        "spec": {
            "template": {
                "spec": patches
            }
        }
    }
    



if __name__== "__main__":
    main()
