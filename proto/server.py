import grpc
import image_pb2 as pb
import image_pb2_grpc as pb_grpc

from concurrent import futures

class NLImageServiceServicer(pb_grpc.NLImageServiceServicer):
  def RotateImage(self, request, context):
	#rotates images by 90
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
		##TODO 
		## THROW SOME SORT OF ERROR, INVALID REQUEST

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
    return request

def serve():
  server = grpc.server(future.ThreadPoolExecutor(max_workers=10))
  pb_grpc.add_NLImageServiceServicer_to_server(NLImageServiceServicer(), server)
  server.add_insecure_port('[::]:8080')
  server.start()
  server.wait_for_termination()

if __name__ == '__main__':
  serve()
