# import os
# from PIL import Image
# from PIL.ExifTags import TAGS


# img_file = 'IMG_1982.JPG'
# image = Image.open(img_file)

# # print(TAGS)
# # TAGS is a dictionary that has keys as numbers and values that text 
# #value of the particular property is 43222: GPS, 65676: width

# image_tags = {}
# for tag, value in image._getexif().items():
#     if tag in TAGS and  TAGS[tag] != 'MakerNote':
#         image_tags[TAGS[tag]] = value


# # print(image_tags['HostComputer'])
# # print(image_tags['Model'])
# # print(image_tags['Make'])
# print(image_tags['SubjectLocation'])
# print(f"Latitude Reference: {image_tags['GPSInfo'][1]}")
# print(f"Latitude : {image_tags['GPSInfo'][2]}")
# print(f"Longitude Reference: {image_tags['GPSInfo'][3]}")
# print(f"Longitude: {image_tags['GPSInfo'][4]}")
# print(f"Altitude: {image_tags['GPSInfo'][6]}")
# print(f"Unit of Speed: {image_tags['GPSInfo'][12]}") # if Kilometers per hour (K)
# # Miles per hour (M)
# # Knots (N)
# # Meters per second (S)
# print(f"Speed Value: {image_tags['GPSInfo'][13]}")
# print(f"Direction Reference: {image_tags['GPSInfo'][16]}")# if T return True Direction 
# # T': True direction - The direction is referenced to true north.
# # 'M': Magnetic direction - The direction is referenced to magnetic north.
# print(f"Direction Value: {image_tags['GPSInfo'][17]}") 
# print(f"Horizontal dilution of precision : {image_tags['GPSInfo'][31]}")
# print(image_tags['XResolution'])
# print(image_tags['YResolution'])

