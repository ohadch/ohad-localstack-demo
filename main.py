import os
from typing import Dict

import boto3
from botocore.exceptions import ClientError

SAMPLE_BUCKET_NAME = "test-bucket"
TENANTS: Dict[str, dict] = {
    "tenant1": {
        "region": "us-east-1",
        "endpoint_url": "http://localhost:4566",
    }
}


def create_tenant_sample_file(tenant: str) -> str:
    """
    Creates a sample file for the tenant.
    :param tenant: The tenant to create the sample file for.
    :return: The path to the sample file.
    """
    print(f"Creating sample file for tenant {tenant}")

    file_name = f"sample-{tenant}.txt"
    with open(file_name, "w") as f:
        f.write(tenant)

    return file_name


def create_bucket(s3_client: boto3.client, bucket_name: str) -> dict:
    """
    Create an S3 bucket
    :param s3_client: Client to use to create the bucket.
    :param bucket_name: Name of the bucket to create.
    :return: Response from S3 API
    """
    print(f"Creating bucket {bucket_name}")
    try:
        response = s3_client.create_bucket(Bucket=bucket_name)
    except ClientError:
        print('Could not create S3 bucket locally.')
        raise
    else:
        return response


def create_s3_client(tenant: str) -> boto3.client:
    """
    Create an S3 client for the tenant.
    :param tenant: The tenant to create the client for.
    :return: The S3 client.
    """
    region = TENANTS[tenant]["region"]
    endpoint_url = TENANTS[tenant]["endpoint_url"]
    return boto3.client("s3", region_name=region, endpoint_url=endpoint_url)


def upload_file_to_s3(s3_client: boto3.client, local_path: str, bucket: str, key: str) -> dict:
    """
    Upload a file to S3
    :param s3_client: Client to use to upload the file.
    :param local_path: Path to the file to upload.
    :param bucket: Name of the bucket to upload to.
    :param key: Key to use for the file.
    :return: Response from S3 API
    """
    print(f"Uploading {local_path} to {bucket}/{key}")
    try:
        response = s3_client.upload_file(local_path, bucket, key)
    except ClientError:
        print('Could not upload file to S3.')
        raise
    else:
        return response


def list_s3_objects(s3_client: boto3.client, bucket: str, prefix: str) -> dict:
    """
    List objects in an S3 bucket under a prefix
    :param s3_client: Client to use to list the objects.
    :param bucket: Name of the bucket.
    :param prefix: Prefix to list objects under.
    :return: Response from S3 API
    """
    try:
        response = s3_client.list_objects(Bucket=bucket, Prefix=prefix)
    except ClientError:
        print('Could not list S3 objects.')
        raise
    else:
        return response


def print_s3_objects(response: Dict) -> None:
    """
    Prints out the contents of an S3 bucket.
    """
    for obj in response["Contents"]:
        print(f'-\t{obj["Key"]}')


def process_tenant(tenant: str) -> None:
    """
    Processes a tenant.
    :param tenant: The tenant to process.
    """
    # Create sample file
    sample_file_path = create_tenant_sample_file(tenant=tenant)
    bucket_key = os.path.basename(sample_file_path)
    s3_client = create_s3_client(tenant=tenant)

    # Create bucket
    create_bucket(
        s3_client=s3_client,
        bucket_name=SAMPLE_BUCKET_NAME
    )

    # Upload file to S3
    upload_file_to_s3(
        s3_client=s3_client,
        local_path=sample_file_path,
        bucket=SAMPLE_BUCKET_NAME,
        key=bucket_key
    )

    # List files in S3
    response = list_s3_objects(
        s3_client=s3_client,
        bucket=SAMPLE_BUCKET_NAME,
        prefix=""
    )

    print("\nFiles in S3 bucket:")
    print_s3_objects(response)


def main():
    for tenant in TENANTS:
        print(f"\n\n======= Processing tenant {tenant} =======\n")
        process_tenant(tenant)
        print(f"\n======= Finished processing tenant {tenant} =======\n\n")


if __name__ == '__main__':
    main()
