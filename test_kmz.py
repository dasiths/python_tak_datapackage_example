from datetime import datetime
import os
import shutil
import threading
from PIL import Image, ImageDraw, ImageFont
import time

from pathlib import Path

class KmzGenerator:
    def generateKmz(self):

        while True:
            try:
                print("Start KMZ Generation")
                currentPath = os.path.dirname(os.path.realpath(__file__))

                Path(os.path.join(currentPath, "kmz-server-root", "kml", "files")).mkdir(parents=True, exist_ok=True)
                Path(os.path.join(currentPath, "kmz-server-root", "kmz")).mkdir(parents=True, exist_ok=True)

                templateFilePath = os.path.join(currentPath, "kml_template.xml")

                with open(templateFilePath, 'r') as templateFile:
                    templateContent = templateFile.read()

                # todo: calculate coordinates
                coordinates = """-72.953233112081065,41.636485101307905
-72.372513446588599,41.636485101307905
-72.370536454702133,42.072111355096126
-72.955210103967531,42.072111355096126"""
                templateContent = templateContent.format(coordinates=coordinates)

                # Save generated kml
                kmlFile = os.path.join(currentPath, "kmz-server-root", "kml", "plt.kml")
                with open(kmlFile, "w") as outputFile:
                    outputFile.write(templateContent)

                # save image
                now = datetime.now()    
                current_time = now.strftime("%H:%M:%S")

                my_image = Image.open(os.path.join(currentPath, "image_template.png"))
                image_editable = ImageDraw.Draw(my_image)
                title_font = ImageFont.truetype('Oswald-Regular.ttf', 20)
                image_editable.text((100,200), current_time, fill=(255,255,0), font=title_font)
                my_image.save(os.path.join(currentPath, "kmz-server-root", "kml", "files", "image.Png"))

                # Generate the KMZ and move it to server root
                tempKmzFilePath = os.path.join(currentPath, "tmp", "temp.kmz")
                shutil.make_archive(tempKmzFilePath, 'zip', os.path.join(currentPath, "kmz-server-root", "kml"))
                finalKmzFilePath = os.path.join(currentPath, "kmz-server-root", "kmz", "plt.kmz")
                shutil.move(tempKmzFilePath + ".zip", finalKmzFilePath)

                print("Generated KMZ file")
            except Exception as e:
                print("An exception occurred when generating KMZ: " + e.__traceback__ )

            # sleep for one second
            time.sleep(1)
def main():
    d = KmzGenerator()
    d.generateKmz()

if __name__ == "__main__":
  main()