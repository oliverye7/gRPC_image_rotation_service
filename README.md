# gRPC Image Rotation Serice

Hi! My name is Oliver Ye, a student at UC Berkeley dual majoring in Electrical Engineering & Computer Science + Business Administration. This was a technical challenge where I built an image processing API (rotations, and mean filters) using gRPC to build a server to process requests; the project was Dockerized to be able to run on a clean install of MacOS. The general goal was to build something with gRPC properly; I didn't go crazy on the API functions, but could have probably added more filters or functions if needed.

# Table of contents
1. [Setup](#setup)
2. [Usage](#usage)
    1. [Server](#server)
    3. [Client](#client)
3. [Docker](#docker)
4. [Discussion and Thoughts](#disc)

## Setup <a name="setup"></a>
Please run my solution on a clean install of **MacOS**

To test the Dockerized version, feel free to jump directly to _**[Docker](#docker)**_

First, run `bash setup.sh` which should take care of installing any dependencies (installs homebrew, python3, dependencies).

Alternatively, if python is already installed on your computer, running `python3 setup.py install` should take care of dependencies as well.

There are no build steps in my solution, so I have not included a build script.

Note: apparently on some Mac silicon Macbooks, grpcio might not be installed properly through pip. There's a small chance that you might have to run `pip uninstall grpcio` and then `conda install grpcio` to properly install it. I didn't have to do this, but this means that you would have to install conda through `bash Miniconda3-latest-MacOSX-x86_64.sh` and then following the entire set of instructions associated there :(

## Usage <a name="usage"></a>
The `RotationService` folder contains an `input` and `output` folder for testing purposes, but feel free to add your own photos or test differently. I've emptied the `output` folder, but the `input` folder consists of a number of
.pngs, .jpegs, and other miscellaneous irregular files.


#### **Server:** <a name="server"></a>

Run `python3 server.py --port <port> --host <host>` to start the server.

By default, _host_ will be set to _localhost_ and _port_ will be set to _8080_, if unspecified (the command run with `python3 server.py`, for instance will have _localhost:8080_).


#### **Client:** <a name="client"></a>
Run `python3 client.py --port <port> --host <host> --input <input path> --output <output path> --rotate <rotation amount> --mean` use the service. The `--mean` argument is optional: if it is not included, the mean filter will not be
applied to the image. Again, _host_ will be set to _localhost_ and _port_ will be set to _8080_, if unspecified on the client. `NONE, NINETY_DEG, ONE_EIGHTY_DEG, TWO_SEVENTY_DEG` are supported rotation amounts. If the --rotate flag is not included, it will default to "NONE


So `python3 client.py --input <...> --output <...> --rotate <...> --mean` is a valid command as well.

An example command would be:

`python3 client.py --input ./input/dog.png --output ./output --rotate ONE_EIGHTY_DEG --mean`

Most small to medium sized images will take a couple seconds (or less), but larger images (3000 x 4000 pixels) can take around 50 seconds to process.

## Dockerization <a name="docker"></a>
The `DockerFile` is included in the `RotationService` folder. 

To see the process in action, run 

`docker build -t my-server .` to build, followed by

`docker run -it -p 8080:8080 --rm --name rotation-service my-server` to run the docker container. 

While using the Dockerized version of the service, if you want to change the port you're connecting to, you need to change the two numbers following `-p` to `<from port>:<to port>`, but it's probably most convenient to just have them be the same port number to avoid confusion. You will also need to specify the port you want to use in the client.py --port parameter. 

If you want to change the host for this version, you need to just vim directly into Dockerfile, and update the host specified directly there. There's a way to get Docker to take CLI inputs, but I figured that this was a simple enough step, so I didn't include it.

## Discussion and Thoughts <a name="disc"></a>

This challenge was definitely really exciting and fun for me! I think I really felt stimulated by the challenge of rapidly learning a new skill and implementing it successfully. Some thoughts on my project:

#### Limitations/Issues
1) For the sake of keeping my submission timely and rapidly debuggable, a lot of my image processing "logic" in my `server.py` file is very rudimentary. For example, rotating the image could have been done in constant space by doing a transpose then a mirror operation, but I chose to just create a second list and insert items into the right positions accordingly. 
Similarly, there are a lot of optimizations to be found in my `MeanFilter` function, where I first cast the entire 1D array into a 2D array for easier processing and code readability. There's a solution which avoids casting the input into a 2D array and the recasting the output back into 1D, but it uses some math and my goal was primarily to get a functional model working in 2 days first.
2) Time permitting, I would have also looked into potential issues with security and bandwidth of the solution that I build. For example, I would try to resolve the usage of `insecureport()` as one of my priorities if this were an actual production. 
3) I'm not too sure how the default gRPC messaging system handles this, but I'd also look into implementing some sort of queue or "multitasking" system on the server end for requests. I noticed that when multiple large requests are sent in close succession (e.g. multiple rotate + mean commands on the `temp.png` file), the server takes a significantly longer time to respond. I sent in maybe 6-7 requests, and instead of coming back 1 by 1 in a staggered order, it took a total of 4 minutes and all requests finished at around the same time. I know this has to do with the number of workers being active (setting maxWorkers = 1) on ThreadPoolExecutor results in requests being processed 1 by 1, but even so, I wonder if there's some way to deal with a very large number of inputs at once.


