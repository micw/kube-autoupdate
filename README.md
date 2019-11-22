# *kube-autoupdate* - Keep your kubernetes deployments up-to-date

*kube-autoupdate* is for kubernetes what *watchtower* or *ouroboros* is for docker. A service that updates your deployments when new versions are in the repository.

Current status: early development, minimal functions, little testing

## Installation / Upgrade

Unless the helm chart is officially released, you need to clone this repository and run (optionally with a --namespace parameter):

```
helm upgrade --install kube-autoupdate helm-chart
```

## Usage

Add the label `autoupdate/scheduled: "true"` to deployments that shall be periodically checked for updated.
Add the annotation `autoupdate/config` which is a yaml with the following format:

```yaml
container1: ^1\.10\.\d+$
container2:
  tag: ^1\.10\.\d+$
```

The key is the container name. The value is either a string or an object with a "tag" attribute. The value must be an expression that
is used to filter available tags for the image. The highest tag version of this filtered list will be used to upgrade the container.
Versions are compared as semantic version numbers using the 'semver' library.

Currently expressions are always regular expressions and should always start with ^ and end with $ (regular expression syntax for whole-string match).
Further versions might interprete expressions not starting/ending with these characters differently.

Examples can be found in the `examples` folder.


## Planned / Implemented features

* Driven with annotations/labels :heavy_check_mark:
* Upgrade *Deployments* :heavy_check_mark:, *StatefulSets* :x:, *DaemonSets* :x: and *CronJobs* :x: when a new version is in the repository
* Upgrade container :heavy_check_mark: and initContainer :x: definitions
* Filter versions (tags) via regular expressions :heavy_check_mark:
* Compare versions using *semver* semantics, so 1.10.1 will be correctly be taken as new version over 1.9.99 :heavy_check_mark:
* *digest* mode: detect if a new image is available under the same tag :x:
    * either by setting the container image tag to the digest, enforcing that specific version
    * or by creating an annotation containing the digest, just enforcing an upgrade/redeploy
* Run as service and periodically update all labeled deployments :heavy_check_mark:
* Run as admission controller to replace image tags on-the-fly on new deployments or upgrades :x:
* Easily deployable via helm chart :heavy_check_mark:
* K3S based integration tests :x:
* Support for image pull secrets :x:

### Ideas

* prometheus endpoint for monitoring
* nice api+webui showing the current state of upgrades
