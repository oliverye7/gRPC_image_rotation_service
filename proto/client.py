import argparse
import cv2
import io
import grpc
import image_pb2 as pb
import image_pb2_grpc as pg_grpc
import numpy as np
from PIL import Image, ImageOps

def isgray(imgpath):
    img = cv2.imread(imgpath)
    if len(img.shape) < 3: return True
    if img.shape[2]  == 1: return True
    b,g,r = img[:,:,0], img[:,:,1], img[:,:,2]
    if (b==g).all() and (b==r).all(): return True
    return False

if __name__ == '__main__':
  # initialize
  parser = argparse.ArgumentParser(
    description = "Parse Arguments for NLImage Service"
  )

  # parameters (positional/optional ones)
  #parser.add_argument('-p', '--port', help="specify port. Default port is 8080", default="8080")
  #parser.add_argument('-t', '--host', help="specify host")
  parser.add_argument('-i', '--input', help="specify path to input file (jpeg or png)")
  parser.add_argument('-o', '--output', help="specify path to output folder")
  parser.add_argument('-r', '--rotate', help="specify degrees of rotation -- options are: NONE, NINETY_DEG, ONE_EIGHTY_DEG, TWO_SEVENTY_DEG. Default rotation if not provided is NONE", default="NONE")
  parser.add_argument('--mean', help="specify the mean filter operation on the input", action="store_true")


  # parse
  args = parser.parse_args()
  print()
  print(args)

  isgray = isgray(args.input)
  print(isgray)

  im = Image.open(args.input, mode='r')
  im_byte_arr = io.BytesIO()
  im.save(im_byte_arr, format="PNG")
  im_byte_arr = im_byte_arr.getvalue()
  print(type(im_byte_arr))
  #print(im_byte_arr)
  pix_val = list(im.getdata())

  # get width and height
  width = im.width
  height = im.height

	
  print(width)
  print(height)
  print(width * height)
  if (isgray):
    data = []
    for i in range(len(pix_val)):
        data.append(pix_val[i][0])
    #for i in range(len(pix_val)):
    #    data[i] = int.from_bytes(data[i], "big")
  else:
    print(len(pix_val))
    if (type(pix_val[0]) != int):
      if (len(pix_val[0]) == 4):
        #RGBA
        data = [x for sets in pix_val for x in sets]
        del data[4-1::4]
      elif (len(pix_val[0]) == 3):
        data = [x for sets in pix_val for x in sets]
    else:
      data = pix_val

	# convert to bytes
    #for i in range(len(pix_val_flat)):
    #  pix_val_flat[i] = (pix_val_flat[i]).to_bytes(1, byteorder='big')
  bytesArray = bytes(data)
  #for i in range(len(data)):
  #  data[i] = (data[i]).to_bytes(1, 'big')
  print(type(data))
  print(type(bytesArray))
	

  if (args.rotate == 'NONE'):
    req = pb.NLImageRotateRequest.NONE
  elif (args.rotate == 'NINETY_DEG'):
    req = pb.NLImageRotateRequest.NINETY_DEG
  elif (args.rotate == 'ONE_EIGHTY_DEG'):
    req = pb.NLImageRotateRequest.ONE_EIGHTY_DEG
  elif (args.rotate == 'TWO_SEVENTY_DEG'):
    req = pb.NLImageRotateRequest.TWO_SEVENTY_DEG
  else:
    print("invalid rotation specification")

  with grpc.insecure_channel("localhost:8080", options=[('grpc.max_message_length', 100000000), ('grpc.max_receive_message_length', 100000000)]) as ch:
    stub = pg_grpc.NLImageServiceStub(ch)
    NLImg = pb.NLImage(color=(not isgray), data=bytesArray, width=width, height=height)
    #bytesArray = bytes([1,2,3,4,5,6,7,8,9,10,11,12])
    #bytesArray = bytes([3,6,9,12, 2,5,8,11,1,4,7,10])
    #NLImg = pb.NLImage(color=(not isgray), data=bytesArray, width=3, height=4)
    request = pb.NLImageRotateRequest(
      rotation=req,
      image=NLImg
    )
    if (args.mean):
      result = stub.RotateImage(request)
      result = stub.MeanFilter(result)
    else:
      print("what up")
      result = stub.RotateImage(request)
      print("bye")
  #print(list(result.data))
  processedData = list(result.data)
  #print(processedData)
  out = []
  if (isgray):
    for i in range(len(processedData)):
        out.append((processedData[i], processedData[i], processedData[i], 255))
  else:
    for i in range(0, len(processedData), 3):
        out.append((processedData[i], processedData[i + 1], processedData[i + 2], 255))
  #print(out)

  im2 = Image.new(mode="RGB", size = (result.width, result.height))
  im2.putdata(out)
  filename = args.input.split("/")
  filename = filename[len(filename) - 1]
  print(filename)

  filename = filename.split(".")
  filename.insert(1, ".")
  if (args.rotate != 'NONE'):
    filename.insert(1, "_Rotated")
  if (args.mean):
    filename.insert(1, "_Meaned")
  output = ''.join(filename)
  im2.save("mean.png")

  print(result.width)
  print(result.height)
    


  #print(output)



  #f = open(args.output + "/" + output, "wb")
  #f.write(im_byte_arr)
  #f.close()
