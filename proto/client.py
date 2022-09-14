import argparse
import cv2
import io
import grpc
import image_pb2 as pb
import image_pb2_grpc as pg_grpc
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
  #print(pix_val)

  # get width and height
  width = im.width
  height = im.height
	
  print(width)
  print(height)
  print(width * height)
  if (isgray):
    data = []
    for i in range(len(pix_val)):
        data.append((pix_val[i][0]).to_bytes(1, byteorder='big'))
    print(len(data))
    #print(grayVals)
    #TODO
    #confirm that casting back to int from byte array results in the same int arry
  else:
    print(len(pix_val))
    data = [x for sets in pix_val for x in sets]
    print(len(data))
    del data[4-1::4]
	# convert to bytes
	#for i in range(len(pix_val_flat)):
	#	pix_val_flat[i] = (pix_val_flat[i]).to_bytes(1, byteorder='big')
    print(len(data))
    #print(pix_val_flat)
	
  with grpc.insecure_channel("localhost:8080") as ch:
	stub = pg_grpc.NLImageServiceStub(ch)
    NLImg = pb.NLImage(color=isgray, data=data, width=width, height=height)
    request = pb.NLImageRotateRequest(
      rotation=args.rotate
      image=NLImg
    )
    if (args.rotate != 'NONE'):
      result = stub.RotateImage(request)
    if (args.mean):
      result = stub.MeanFilter(request)
    




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
  print(output)



  f = open(args.output + "/" + output, "wb")
  f.write(im_byte_arr)
  f.close()
