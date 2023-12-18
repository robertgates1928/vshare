import requests
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


# Create the BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string('DefaultEndpointsProtocol=https;AccountName=vsharetest;AccountKey=b4SGnD03D66yiFKDYpJ8ylyLOioocHAiP8EEQSLYo1rO1EATeDcFT3rzLkCuJZk2rowYQi3noi0C+AStGUL/oQ==;EndpointSuffix=core.windows.net')

# # Create a unique name for the container
# container_name = str(uuid.uuid4())

# # Create the container
# container_client = blob_service_client.create_container(container_name)
 
# # Create a local directory to hold blob data
local_path = "./data"
# os.mkdir(local_path)

# # Create a file in the local data directory to upload and download
# local_file_name = str(uuid.uuid4()) + ".txt"
# upload_file_path = os.path.join(local_path, local_file_name)

# # Write text to the file
# file = open(file=upload_file_path, mode='w')
# file.write("Hello, World!")
# file.close()

# # Create a blob client using the local file name as the name for the blob
# blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

# print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

# # Upload the created file
# with open(file=upload_file_path, mode="rb") as data:
#     blob_client.upload_blob(data)

container_client = blob_service_client.get_container_client('a828eb69-aa82-4e2b-a68d-b7d9b679b0d5')
print("\nListing blobs...")
download_file_path = os.path.join(local_path,  'DOWNLOAD.txt')
# List the blobs in the container
# blob_list = container_client.list_blobs()
# for blob in blob_list:
#     print("\t" + blob.name)

#     print("\nDownloading blob to \n\t" + download_file_path)

#     with open(file=download_file_path, mode="wb") as download_file:
#         download_file.write(container_client.download_blob(blob.name).readall())

print("Deleting blob container...")
container_client.delete_container()

print("Deleting the local source and downloaded files...")
os.remove(download_file_path)
# os.rmdir(local_path)

print("Done")