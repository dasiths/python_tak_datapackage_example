import hashlib
import os
import socket
import shutil
import threading
import requests

class DataPackageSender:
    def sendCotDataPackage(self):
        try:
            takServerHost = "localhost"
            takServerTcpPort = 8087
            takServerUrl = f"{takServerHost}:8080"

            currentPath = os.path.dirname(os.path.realpath(__file__))
            
            uid = "1793BD2E-28A9-46A7-83CF-670F6BBD3347"
            creatorId = "S-1-12-1-3807762983-1169496742-1797301920-1838764222"           
           
            fileTransferTemplateFileName = "file_transfer_request_template.xml"
            zipFilePrefix = "package"
            zipFileName = f"{zipFilePrefix}.zip"

            dataPackageTemplatePath = os.path.join(currentPath, "data-package-template")
            dataPackagePath = os.path.join(currentPath, "tmp", "data-package")
            cotFile = os.path.join(dataPackagePath, "FILES", "message.cot")
            manifestFile = os.path.join(dataPackagePath, "MANIFEST", "manifest.xml")

            print("Starting: COT data package workflow")
                       
            # copy template to working directory
            shutil.rmtree(dataPackagePath)
            shutil.copytree(dataPackageTemplatePath, dataPackagePath)

            # Update template           
            with open(cotFile, 'r') as cotTemplateFile:
                cotTemplateContent = cotTemplateFile.read()
                cotTemplateContent = cotTemplateContent.format(uid=uid)
            with open(cotFile, 'w') as cotTemplateFile:
                cotTemplateFile.write(cotTemplateContent)

            with open(manifestFile, 'r') as manifestTemplateFile:
                manifestTemplateContent = manifestTemplateFile.read()
                manifestTemplateContent = manifestTemplateContent.format(uid=uid)
            with open(manifestFile, 'w') as manifestTemplateFile:
                manifestTemplateFile.write(manifestTemplateContent)

            # Create zip
            shutil.make_archive(os.path.join(currentPath, "tmp", zipFilePrefix), 'zip', dataPackagePath)
            zippedDataPackagePath = os.path.join(currentPath, "tmp", zipFileName)

            # Calculate SHA256 Hash
            fileHash = self.calculateSha256OfFile(zippedDataPackagePath)
            print("File hash: " + fileHash)

            # Upload data package to Tak Server
            postUrl = (f"http://{takServerUrl}/Marti/sync/missionupload?"
                    f"hash={fileHash}&"
                    f"filename={zipFileName}&"
                    f"creatorUid={creatorId}")
            headers = {'Content-Disposition': f'form-data;name="assetfile";filename="{zipFileName}"'}
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
            fileTransferTemplateFileName = os.path.join(currentPath, fileTransferTemplateFileName)

            with open(fileTransferTemplateFileName, 'r') as templateFile:
                templateContent = templateFile.read()
            fileSize = os.path.getsize(zippedDataPackagePath)
            templateContent = templateContent.format(sendUrl=putUrl, fileHash=fileHash, fileSize=fileSize, filename=zipFileName, senderUid=creatorId)
            self.sendCotDirect(takServerHost, takServerTcpPort, templateContent)
            print("File transfer request COT message sent to Tak Server")
        except Exception as e:
            print("An exception occurred when sending data package to Tak Server: " + e.__traceback__.format_exc() )

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
    d.sendCotDataPackage()

if __name__ == "__main__":
  main()