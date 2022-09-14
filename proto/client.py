import argparse
import io
#import grpc
#import image_pb2 as pb
#import image_pb2_grpc as pg_grpc
#
from PIL import Image
#with grpc.insecure_channel("localhost:8080") as ch:
#  stub = pb_grpc.NLImageServiceStub(ch)


if __name__ == '__main__':
  # initialize
  parser = argparse.ArgumentParser(
    description = "Parse Arguments for NLImage Service"
  )

  # parameters (positional/optional ones)
  #parser.add_argument('num1', help="Some sample help message here for n1", type=float)
  #parser.add_argument('num2', help="Some sample help message here for n2", type=float)
  #parser.add_argument('--operation', help="provide operator", default = '+')

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
  result = None
  #if (args.operation == '+'):
  #    result = args.num1 + args.num2
  #if (args.operation == '-'):
  #    result = args.num1 - args.num2
  #if (args.operation == '/'):
  #    result = args.num1 / args.num2
  #if (args.operation == '*'):
  #    result = args.num1 * args.num2
  #if (args.operation == 'pow'):
  #    result = pow(args.num1, args.num2)
  #print("Result: "  + str(result))

  im = Image.open(args.input, mode='r')
  im_byte_arr = io.BytesIO()
  im.save(im_byte_arr, format="PNG")
  im_byte_arr = im_byte_arr.getvalue()
  print(type(im_byte_arr))

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
  f = open(output, "wb")
  f.write(im_byte_arr)
  f.close()
