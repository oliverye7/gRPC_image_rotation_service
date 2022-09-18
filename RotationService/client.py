import argparse
import cv2
import io
import grpc
import numpy as np
import sys
from PIL import Image, ImageOps

import image_pb2 as pb
import image_pb2_grpc as pb_grpc


def isgray(imgpath):
    img = cv2.imread(imgpath)
    if len(img.shape) < 3:
        return True
    if img.shape[2] == 1:
        return True
    b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    if (b == g).all() and (b == r).all():
        return True
    return False


if __name__ == "__main__":
    # initialize
    parser = argparse.ArgumentParser(description="Parse Arguments for NLImage Service")

    # parameters (positional/optional ones)
    parser.add_argument(
        "-p", "--port", help="specify port. Default port is 8080", default="8080"
    )
    parser.add_argument(
        "-t",
        "--host",
        help="specify host. Default host will be localhost",
        default="localhost",
    )
    parser.add_argument(
        "-i", "--input", help="specify path to input file (jpeg or png)"
    )
    parser.add_argument("-o", "--output", help="specify path to output folder")
    parser.add_argument(
        "-r",
        "--rotate",
        help="specify degrees of rotation -- options are: NONE, NINETY_DEG, ONE_EIGHTY_DEG, TWO_SEVENTY_DEG. Default rotation if not provided is NONE",
        default="NONE",
    )
    parser.add_argument(
        "--mean",
        help="specify the mean filter operation on the input",
        action="store_true",
    )

    # parse
    args = parser.parse_args()
    print()

    rot = 0
    if args.rotate == "NONE":
        req = pb.NLImageRotateRequest.NONE
    elif args.rotate == "NINETY_DEG":
        req = pb.NLImageRotateRequest.NINETY_DEG
        rot = 90
    elif args.rotate == "ONE_EIGHTY_DEG":
        req = pb.NLImageRotateRequest.ONE_EIGHTY_DEG
        rot = 180
    elif args.rotate == "TWO_SEVENTY_DEG":
        req = pb.NLImageRotateRequest.TWO_SEVENTY_DEG
        rot = 270
    else:
        print("invalid rotation specification.")
        print(
            "Your rotation request needs to be one of: NONE, NINETY_DEG, ONE_EIGHTY_DEG, TWO_SEVENTY_DEG."
        )
        sys.exit("try running 'python3 client.py -h' for additional details")

    filename = args.input.split("/")
    filename = filename[len(filename) - 1]

    filename = filename.split(".")

    try:
        isgray = isgray(args.input)
        im = Image.open(args.input, mode="r")
        im = im.convert("RGB")
        pix_val = list(im.getdata())

        # get width and height
        width = im.width
        height = im.height
    except:
        print("incorrect input type, not parsable")
        sys.exit(
            f"the input must be of either the PNG or JPEG format type. Your input was an {filename[1]} type."
        )

    print("reading image...")

    # parse input image pixels into valid bytes object for server.py to parse (NLImage.data takes a bytes object)
    if isgray:
        data = []
        for i in range(len(pix_val)):
            data.append(pix_val[i][0])
    else:
        if type(pix_val[0]) != int:
            if len(pix_val[0]) == 4:
                # RGBA
                data = [x for sets in pix_val for x in sets]
                del data[4 - 1 :: 4]
            elif len(pix_val[0]) == 3:
                data = [x for sets in pix_val for x in sets]
        else:
            data = pix_val

    bytesArray = bytes(data)

    # send out/receive requests, set up messages
    with grpc.insecure_channel(
        args.host + ":" + args.port,
        options=[
            ("grpc.max_message_length", 100000000),
            ("grpc.max_receive_message_length", 100000000),
        ],
    ) as ch:
        stub = pb_grpc.NLImageServiceStub(ch)
        NLImg = pb.NLImage(
            color=(not isgray), data=bytesArray, width=width, height=height
        )
        request = pb.NLImageRotateRequest(rotation=req, image=NLImg)
        print("request sent...")
        if args.mean:
            result = stub.RotateImage(request)
            result = stub.MeanFilter(result)
        else:
            result = stub.RotateImage(request)

    if result.width == -2:
        print(
            "there was an error with the input type. unable to rotate or mean the file. please reconfirm your file type, or check to see if it is corrupted"
        )
        sys.exit()
    elif result.width == -1:
        print(
            "something went wrong while attempting to rotate or mean the input. there's probably a bug somewhere in the server.py file"
        )
        sys.exit()

    print("request processed...")

    # reconfigure the received bytes object into list of pixel values, so PIL can reconstruct the image
    processedData = list(result.data)
    out = []
    if isgray:
        for i in range(len(processedData)):
            out.append((processedData[i], processedData[i], processedData[i], 255))
    else:
        for i in range(0, len(processedData), 3):
            out.append(
                (processedData[i], processedData[i + 1], processedData[i + 2], 255)
            )

    # Saving the image to the output file. All images are saved as RGBs, including gray images.
    im2 = Image.new(mode="RGB", size=(result.width, result.height))
    im2.putdata(out)
    filename = args.input.split("/")
    filename = filename[len(filename) - 1]

    filename = filename.split(".")
    filename.insert(1, ".")
    if args.rotate != "NONE":
        filename.insert(1, "_rot" + str(rot))
    if args.mean:
        filename.insert(1, "_Meaned")
    output = "".join(filename)
    im2.save(args.output + "/" + output, filename[len(filename) - 1])
    print("finished!")
