import grpc
import image_pb2 as pb
import image_pb2_grpc as pb_grpc

from concurrent import futures


class NLImageServiceServicer(pb_grpc.NLImageServiceServicer):
  def RotateImage(self, request, context):
	# rotates images by 90
    width = request.image.width
    height = request.image.height
    vals = request.image.bytes
	color = request.image.color
    temp = [0] * len(vals)
    pos = 0

	if (request.rotation == pb_grpc.NLImageRotateRequest.Rotation.NONE):
		temp = vals
	elif (request.rotation == pb_grpc.NLImageRotateRequest.Rotation.NINETY_DEG):
		temp = RotateNinety(width, height, vals, pos, temp, color, 1)
	elif (request.rotation == pb_grpc.NLImageRotateRequest.Rotation.ONE_EIGHTY_DEG):
		temp = RotateNinety(width, height, vals, pos, temp, color, 2)
	elif (request.rotation == pb_grpc.NLImageRotateRequest.Rotation.TWO_SEVENTY_DEG):
		temp = RotateNinety(width, height, vals, pos, temp, color, 3)
	else:
		# TODO
		# THROW SOME SORT OF ERROR, INVALID REQUEST
	response = pb.NLImage(color=request.image.color,
							data=temp,
							width=request.image.width,
							height=request.image.height)
	return response

  def RotateNinety(self, width, height, vals, pos, temp, color, times):
    temp = [0] * len(vals)
	for k in range(times):
      if (color):
        # then color image, data is a 3 channel rgb with rgb triplets stored row-wise
        for i in range(width - 1, -1, -1):
            for j in range(height):
                temp[pos] = vals[i*3+j*width*3]
                pos += 1;
                temp[pos] = vals[i*3+j*width*3 + 1]
                pos += 1;
                temp[pos] = vals[i*3+j*width*3 + 2]
                pos += 1;
      else:
        # grayscale image, one byte per pixel
        for i in range(width - 1, -1, -1):
            for j in range(height):
                temp[pos] = vals[i+j*width]
                pos += 1;
    return temp
		

  def MeanFilter(self, request, context):
	color = request.color;
	data = request.data;
	width = request.width;
	height = request.height;

	temp = [0] * len(data)
	pos = 0
	count = 0
	if (color):
	# RGB, 3 channels
		res1 = meanRGB(data, width, height, 0)
		res2 = meanRGB(data, width, height, 1)
		res3 = meanRGB(data, width, height, 2)
		res = []
		# res1 represents the R mean matrix, res2 represents G mean matrix, res3 represents B mean matrix
		# here we interleave the R, G, B matrices to reconstruct the overall mean filtered matrix
		for i in range(len(res1)):
			res.append(res1[i])
			res.append(res2[i])
			res.append(res3[i])
	else:
	# Grayscale
		res = meanGrayScale(data, width, height)
	response = pb.NLImage(color=color, data=res, width=width, height=height)

    return response

  def meanRGB(l, width, height, offset):
    temp = [[0] * (width + 2) for i in range(height + 2)]
    temp2 = [[0] * (width) for i in range(height + 1)]
    for i in range(offset, len(l), 3):
        # convert 1d row major into 2d array for easier processing
        row = (i//3) // width
        col = (i//3) % width
        temp2[row + 1][col] = l[i]
        print(str(row) + "  " + str(col))
	return meanFilter(temp, temp2)

  def meanGrayScale(l, width, height):
    temp = [[0] * (width + 2) for i in range(height + 2)]
    temp2 = [[0] * (width) for i in range(height + 1)]
    for i in range(len(l)):
        # convert 1d row major into 2d array for easier processing
        row = i // width
        col = i % width
        temp2[row + 1][col] = l[i]
	return meanFilter(temp, temp2)

  def meanFilter(temp, temp2):
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
            temp[i][j] = mean/div
    del temp[0]
    del temp[len(temp) - 1]
    res = []
    for i in range(len(temp)):
        for j in range(1, len(temp[0]) - 1):
            res.append(temp[i][j])
	return res


    

def serve():
  server = grpc.server(future.ThreadPoolExecutor(max_workers=10))
  pb_grpc.add_NLImageServiceServicer_to_server(NLImageServiceServicer(), server)
  server.add_insecure_port('[::]:8080')
  server.start()
  server.wait_for_termination()

if __name__ == '__main__':
  serve()
