# *kube-autoupdate* - Keep your kubernetes deployments up-to-date

*kube-autoupdate* is for kubernetes what *watchtower* or *ouroboros* is for docker. A service that updates your deployments when new versions are in the repository.

Current status: early development, minimal functions, little testing

## Planned features

* Driven with annotations/labels
* Upgrade *Deployments*, *StatefulSets*, *DaemonSets* and *CronJobs* when a new version is in the repository
* Upgrade container and initContainer definitions
* Filter versions (tags) via regular expressions
* Compare versions using *semver* semantics, so 1.10.1 will be correctly be taken as new version over 1.9.99
* *digest* mode: detect if a new image is available under the same tag
    * either by setting the container image tag to the digest, enforcing that specific version
    * or by creating an annotation containing the digest, just enforcing an upgrade/redeploy
* Run as service and periodically update all labeled deployments
* Run as admission controller to replace image tags on-the-fly on new deployments or upgrades
* Easily deployable via helm chart
* K3S based integration tests

## Implements features

* command-line only
* Driven with annotations/labels
* Upgrade *Deployments* when a new version is in the repository
* Upgrade container definitions (no init containers yet)
* Filter versions (tags) via regular expressions
* Compare versions using *semver* semantics, so 1.10.1 will be correctly be taken as new version over 1.9.99


### Ideas

* prometheus endpoint for monitoring
* nice api+webui showing the current state of upgrades
