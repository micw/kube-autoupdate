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
