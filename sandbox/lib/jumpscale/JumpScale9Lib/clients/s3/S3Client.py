from js9 import j

try:
    # import boto3
    from minio import Minio
    from minio.error import (
        ResponseError,
        BucketAlreadyOwnedByYou,
        BucketAlreadyExists
    )
except:
    print("WARNING: s3 pip client (minio) not found please install do j.clients.s3.install()")


TEMPLATE = """
address = ""
port = 9000
accesskey_ = ""
secretkey_ = ""
bucket = ""
bucket_ok = false
"""

JSConfigBase = j.tools.configmanager.base_class_config


class S3Client(JSConfigBase):
    """

    """

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        c = self.config.data

        # s3 = boto3.resource('s3',
        #                     endpoint_url='http://%s:%s' % (c["address"], c["port"]),
        #                     config=boto3.session.Config(signature_version='s3v4'),
        #                     aws_access_key_id=c["accesskey_"],
        #                     aws_secret_access_key=c["secretkey_"]
        #                     )

        self.logger.info("open connection to minio:%s"%self.instance)
        self.client = Minio('%s:%s' % (c["address"], c["port"]),
                            access_key=c["accesskey_"],
                            secret_key=c["secretkey_"],
                            secure=False)

        if not self.config.data["bucket_ok"]:
            self._bucket_create(self.config.data["bucket"])

    def _bucket_create(self, name):
        try:
            self.client.make_bucket(name, location="us-east-1")
        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            raise

    def upload(self, bucket_name, object_name, file_path, content_type='text/plain', meta_data=None):
        if not j.sal.fs.exists(file_path):
            raise ValueError("file: %s not found" % file_path)
        return self.client.fput_object(bucket_name, object_name, file_path, content_type, meta_data)

    def download(self, bucket_name, object_name, file_path):
        return self.client.fget_object(bucket_name, object_name, file_path)

    def list_buckets(self):
        return self.client.list_buckets()

    def list_objects(self, bucket_name, prefix=None, recursive=None):
        return self.client.list_objects(bucket_name, prefix=prefix, recursive=recursive)

    def remove_bucket(self, bucket_name):
        return self.client.remove_bucket(bucket_name)

    def remove_object(self, bucket_name, object_name):
        return self.client.remove_object(bucket_name, object_name)
