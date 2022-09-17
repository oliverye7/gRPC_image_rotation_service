import grpc
import argparse
import image_pb2 as pb
import image_pb2_grpc as pb_grpc

from concurrent import futures

class NLImageServiceServicer(pb_grpc.NLImageServiceServicer):

  def checkInput(self, width, height, vals, color):
    """ 
    Checks of the message passed into a RotateImage or MeanFilter function call is well formed.
   	Parameters:
    width (int): width of image passed in (from NLImage.width)
    height (int): height of image passed in (from NLImage.height)
    vals (bytes): bytes of image pixel values, as a flattened 1D list (from NLImage.data)
    color (boolean): determines if the bytes in vals correspond to pixels 3 by 1 or 1 by 1

    Returns:
    0: means success
	NLImage with width = -2: poorly formed protobuf message request was received
    """
    # error handling
    if (color):
      if (width * height * 3 != len(vals)) or (len(vals) % 9 != 0):
        width = -2
        response = pb.NLImage(color=color, data=vals, width=width, height=height)
        return response
    else:
      if (width * height != len(vals)) or (len(vals) % 3 != 0):
        width = -2
        response = pb.NLImage(color=color, data=vals, width=width, height=height)
        return response
    return 0

  def RotateImage(self, request, context):
    """ 
	Rotates the image either 0, 90, 180, or 270 degrees counter clockwise. RotateImage works by calling RotateNinety
	the right number of times. Image width and height are swapped accordingly for 90 and 270 degree rotations.
   	Parameters:
	request: NLImageRotateRequest message, which contains the picture data in 'image', and the number of
			 rotations in 'rotation'

    Returns:
	NLImage: NLImage message with the rotated input
    """
    width = request.image.width
    height = request.image.height
    vals = request.image.data
    color = request.image.color

    err = self.checkInput(width, height, vals, color)
    if (err != 0):
      return err
    
    if (request.rotation == pb.NLImageRotateRequest.NONE):
      temp = vals
    elif (request.rotation == pb.NLImageRotateRequest.NINETY_DEG):
      temp = self.RotateNinety(width, height, vals, color)
      width, height = height, width
    elif (request.rotation == pb.NLImageRotateRequest.ONE_EIGHTY_DEG):
      temp = self.RotateNinety(width, height, vals, color)
      temp = self.RotateNinety(height, width, temp, color)
    elif (request.rotation == pb.NLImageRotateRequest.TWO_SEVENTY_DEG):
      temp = self.RotateNinety(width, height, vals, color)
      temp = self.RotateNinety(height, width, temp, color)
      temp = self.RotateNinety(width, height, temp, color)
      width, height = height, width
    else:
      width = -1

    response = pb.NLImage(color=color, data=bytes(temp), width=width, height=height)
    return response

  def RotateNinety(self, width, height, vals, color):
    """ 
	Takes a 1D array of vals representing the pixels of an image in row major order, and rotates it by 90 degrees.

   	Parameters:
	width (int): width of specified image
	height (int): height of specified image
	vals (int): array of bytes corresponding to pixels of an image. If the 'color' parameter is true (RGB), then every
	three bytes will correspond to one pixel. If the 'color' parameter is false (gray), then each byte corresponds to
	one pixel.
	color (boolean): whether or not the image is in color (three channel) or grayscale (one channel)

    Returns:
	list[int]: list of pixel values that have been rotated counterclockwise 90 degrees
    """
    temp = [0] * len(vals)
    pos = 0
    if (color):
      for i in range(width - 1, -1, -1):
          for j in range(height):
              temp[pos] = vals[i*3+j*width*3]
              pos += 1;
              temp[pos] = vals[i*3+j*width*3 + 1]
              pos += 1;
              temp[pos] = vals[i*3+j*width*3 + 2]
              pos += 1;
    else:
      for i in range(width - 1, -1, -1):
          for j in range(height):
              temp[pos] = vals[i+j*width]
              pos += 1;
    return temp
        

  def MeanFilter(self, request, context):
    """ 
	Takes the mean of each pixel, applying a mean filter on the entire image. 
	If we have an image with 9 pixels as follows:
    A B C
    D E F
    G H I

    Then a few examples of pixels from the mean filter of this image are:
       A_mean_filter = (A + B + E + D) / 4
       D_mean_filter = (D + A + B + E + G + H) / 6
       E_mean_filter = (E + A + B + C + D + F + G + H + I) / 9

    For color images, the mean filter is the image with this filter run on each of the 3 channels independently.

   	Parameters:
	request: NLImage message carrying the data in an image

    Returns:
	NLImage: NLImage message with the the data list with a mean filter applied
    """

    width = request.width;
    height = request.height;
    data = request.data;
    color = request.color;

    err = self.checkInput(width, height, data, color)
    if (err != 0):
      return err

    temp = [0] * len(data)
    count = 0
    if (color):
    # RGB, 3 channels
        res1 = self.meanRGB(data, width, height, 0)
        res2 = self.meanRGB(data, width, height, 1)
        res3 = self.meanRGB(data, width, height, 2)
        res = []
        # res1 represents the R mean matrix, res2 represents G mean matrix, res3 represents B mean matrix
        # here we interleave the R, G, B matrices to reconstruct the overall mean filtered matrix
        for i in range(len(res1)):
            res.append(res1[i])
            res.append(res2[i])
            res.append(res3[i])
    else:
    # Grayscale
        res = self.meanGrayScale(data, width, height)

    response = pb.NLImage(color=color, data=bytes(res), width=width, height=height)

    return response

  def meanRGB(self, data, width, height, offset):
    """ 
	Takes the mean filter of an RGB image by taking the meanFilter of each other pixel, with an offset of 'offset'
	in the byte list. meanRGB does some additional processing to account for the fact that a meanRGB has 3 color channels.

   	Parameters:
	data (list): list of pixel values corresponding to an RGB color
	width (int): width of the image
	height (int): height of the image
	offset (int): specifies which mean filter we are taking (e.g. mean filter of red pixels, mean filter of green pixels, o
				  mean filter of blue pixels)

    Returns:
	list[int]: list of pixels that have been mean filtered
    """
    temp = [[0] * (width + 2) for i in range(height + 2)]
    temp2 = [[0] * (width) for i in range(height + 1)]
    for i in range(offset, len(data), 3):
        # convert 1d row major into 2d array for easier processing
        row = (i//3) // width
        col = (i//3) % width
        temp2[row + 1][col] = data[i]
    return self.meanFilter(temp, temp2, height, width)

  def meanGrayScale(self, data, width, height):
    """ 
	Takes the mean filter of a grayscale image, by directly calling the meanFilter function after converting the 1d array
	into a 2D array for easier readability

   	Parameters:
	data (list): list of pixel values corresponding to an RGB color
	width (int): width of the image
	height (int): height of the image

    Returns:
	list[int]: list of pixels that have been mean filtered
    """
    temp = [[0] * (width + 2) for i in range(height + 2)]
    temp2 = [[0] * (width) for i in range(height + 1)]
    for i in range(len(data)):
        # convert 1d row major into 2d array for easier processing
        row = i // width
        col = i % width
        temp2[row + 1][col] = data[i]
    return self.meanFilter(temp, temp2, height, width)

  def meanFilter(self, temp, temp2, height, width):
    """ 
	Executes the mean filter operation on an arbitrary 2D set of arrays, returning a meaned 2D array. This function is
	called three times for an RGB image (once for R, once for G, once for B), and once for a grayscale image.

   	Parameters:
	temp (list[int]): "output" 2d array, to contain the means of values in the temp2 input array
	temp2 (list[int]): "input" 2d array, to be padded with a layer of zeros around the edges to make arithmetic easier
	height (int): height of our image
	width (int): width of an image

    Returns:
	list[int]: list of pixels that have been mean filtered, as a 1d array -- the values of 'temp' but laid out in row
			   major order
    """
    # pad with 0s
    for i in range(height + 1):
        temp2[i].insert(0,0)
        temp2[i].insert(width + 1,0)
    temp2.append([0] * (width + 2))

    for i in range(1, len(temp2) - 1):
        for j in range(1, len(temp2[0]) - 1):
            mean = 0
            div = 9
            if (((i - 1 <= 0) and (j - 1 <= 0)) or
                ((i - 1 <= 0) and (j + 1 >= len(temp[0]) - 1)) or
                ((i + 1 >= len(temp) - 1) and (j - 1 <= 0)) or
                ((i + 1 >= len(temp) - 1) and (j + 1 >= len(temp[0]) - 1))):
                div = 4
            elif ((i - 1 <= 0) or (j - 1 <= 0) or (i + 1 >= len(temp) - 1) or
                  (j + 1 >= len(temp[0]) - 1)):
                div = 6
            # index in the center
            mean += temp2[i - 1][j - 1] + temp2[i - 1][j] + temp2[i - 1][j + 1]
            mean += temp2[i][j - 1] + temp2[i][j] + temp2[i][j + 1]
            mean += temp2[i + 1][j - 1] + temp2[i + 1][j] + temp2[i + 1][j + 1]
            temp[i][j] = int(mean/div)
    del temp[0]
    del temp[len(temp) - 1]
    res = []
    for i in range(len(temp)):
        for j in range(1, len(temp[0]) - 1):
            res.append(temp[i][j])
    return res


def serve(port, host):
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options = [
            ('grpc.max_send_message_length', 100000000),
            ('grpc.max_receive_message_length', 100000000)
        ])
  pb_grpc.add_NLImageServiceServicer_to_server(NLImageServiceServicer(), server)
  server.add_insecure_port(host + ":" + port)
  server.start()
  server.wait_for_termination()

if __name__ == '__main__':
  # initialize
  parser = argparse.ArgumentParser(
    description = "Parse Arguments for NLImage Service"
  )

  # parameters (positional/optional ones)
  parser.add_argument('-p', '--port', help="specify port. Default port is 8080")
  #parser.add_argument('-p', '--port', help="specify port. Default port is 8080", default="8080")
  parser.add_argument('-t', '--host', help="specify host. Default host will be localhost", default="localhost")
  
  args = parser.parse_args()

  serve(port, args.host)
