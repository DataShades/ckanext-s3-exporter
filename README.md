[![Tests](https://github.com/DataShades/ckanext-s3-exporter/actions/workflows/test.yml/badge.svg)](https://github.com/DataShades/ckanext-s3-exporter/actions/workflows/test.yml)

# ckanext-s3-exporter

Creates a dataset resources from files uploaded to AWS s3 bucket.

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible? |
| --------------- | ----------- |
| 2.9 and earlier | no          |
| 2.10+           | yes         |

## Installation

Use `pypi` or install from source. Refer to CKAN documentation to know how to install an extension from source.

**TODO**: upload to pypi

## Config settings

List of available config options:

1. Publicly known and shared identifier that is used to identify the AWS account when making requests to Amazon S3
   * `ckanext.s3_exporter.access_key = xxx`
2. Secret key that is used to authenticate and authorize requests made using the Access Key ID
   * `ckanext.s3_exporter.secret_key`
3. A container name that is used for storing data and objects in AWS
   * `ckanext.s3_exporter.bucket_name`
4. Specify to which queue the export job will be added. Will be added to default queue if not specified.
   * `ckanext.s3_exporter.queue_name`

## Developer installation

To install ckanext-s3-exporter for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/DataShades/ckanext-s3-exporter.git
    cd ckanext-s3-exporter
    python setup.py develop
    pip install -r dev-requirements.txt

## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
