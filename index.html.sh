#!/bin/bash

cat << EOF
<html>
<body>
<h1>Public repo for kube-autoupdate helm chart</h1>
<h2>Installation</h2>
<p>
<pre>
helm repo add kube-autoupdate https://micw.github.io/kube-autoupdate/
helm install kube-autoupdate/kube-autoupdate
</pre>
</p>
<h2>Available versions</h2>
<ul>
EOF

grep index.yaml -e "version:" | awk -F': ' '{print "<li>"$2"</li>"}' | sort -n -r

cat << EOF
</ul>
</body>
</html>
EOF

