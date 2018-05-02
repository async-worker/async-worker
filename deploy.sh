#! /bin/bash

if [[ -z "$PYPI_USERNAME" || -z "$PYPI_PASSWORD" || -z "$PYPI_URL" ]]; then
    echo "You must set PYPI_USERNAME, PYPI_PASSWORD, and PYPI_URL to run this script"
    exit 1
fi

cat << EOF > /root/.pypirc
[distutils]
index-servers=pypi

[pypi]
repository=${PYPI_URL}
username=${PYPI_USERNAME}
password=${PYPI_PASSWORD}
EOF

python setup.py sdist bdist_wheel upload -r pypi
