# Begins with tensorflow python3 and GPU
FROM tensorflow/tensorflow:latest-gpu-py3

# Copy all files into the container
COPY ./ ./

RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y libsndfile1-dev

# Install dependencies
RUN cd home
RUN pip3 install -r requirements.txt
RUN pip3 install pip==19.3.1
RUN pip3 install --no-cache git+https://github.com/pedrolisboa/poseidon.git

RUN mkdir package
RUN mv src package/src
RUN mv setup.py package/setup.py
RUN pip3 install /package/
