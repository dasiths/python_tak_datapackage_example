import hashlib
import os
import socket
import shutil
import threading
import requests

class DataPackageSender:
    def sendCotDataPackage(self, uid, cotMessage, imagePath):
        try:
            currentPath = os.path.dirname(os.path.realpath(__file__))
            print("Starting: COT data package workflow1")

            # todo: generate data package temp folder using a template or pycot
            dataPackagePath = os.path.join(currentPath, "data-package")

            # Create zip
            shutil.make_archive(os.path.join(currentPath, "tmp", "package"), 'zip', dataPackagePath)
            zippedDataPackagePath = os.path.join(currentPath, "tmp", "package.zip")

            # Calculate SHA256 Hash
            fileHash = self.calculateSha256OfFile(zippedDataPackagePath)
            print("File hash: " + fileHash)

            # Upload data package to Tak Server
            takServerHost = "localhost"
            takServerTcpPort = 8087
            takServerUrl = "localhost:8080"
            postUrl = (f"http://{takServerUrl}/Marti/sync/missionupload?"
                    f"hash={fileHash}&"
                    "filename=package.zip&"
                    "creatorUid=S-1-12-1-3807762983-1169496742-1797301920-1838764222")
            headers = {'Content-Disposition': 'form-data;name="assetfile";filename="package.zip"'}
            with open(zippedDataPackagePath, 'rb') as f:
                formData = {'assetfile': f}
                r = requests.post(postUrl, headers=headers, files=formData)
                print("Posted to TAK Server with status code: " + str(r.status_code))

            # Update meta data in Tak Server
            putUrl = f"http://{takServerUrl}/Marti/api/sync/metadata/{fileHash}/tool"
            r = requests.put(putUrl)
            print("PUT url: " + putUrl)
            print("Meta data Put to TAK Server with status code: " + str(r.status_code))

            # Send COT message to TAK Server
            fileTransferTemplateFilePath = os.path.join(currentPath, "file_transfer_request_template.xml")

            with open(fileTransferTemplateFilePath, 'r') as templateFile:
                templateContent = templateFile.read()
            fileSize = os.path.getsize(zippedDataPackagePath)
            templateContent = templateContent.format(sendUrl=putUrl, fileHash=fileHash, fileSize=fileSize)
            self.sendCotDirect(takServerHost, takServerTcpPort, templateContent)
            print("File transfer request COT message sent to Tak Server")
        except Exception as e:
            print("An exception occurred when sending data package to Tak Server: " + e.__traceback__ )

    def calculateSha256OfFile(self, fileName):
        sha256_hash = hashlib.sha256()
        with open(fileName, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()

    def sendCotDirect(self, takServerUrl, takServerPort, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((takServerUrl, int(takServerPort)))
        s.sendall(bytes(message, "utf-8"))
        s.close()

def main():
    d = DataPackageSender()
    d.sendCotDataPackage("","","")

if __name__ == "__main__":
  main()