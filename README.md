# Luminari

The open source alternative to Perplexity, built on top of Llama.Cpp, FastApi, Hermes2  Searxng

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About `<a name = "about"></a>`

This repository contains all the application

## Getting Started `<a name = "getting_started"></a>`

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

What things you need to install the software and how to install them.

[Llama CPP compatible server](https://llama-cpp-python.readthedocs.io/en/latest/server/ "Server")

[Hermes Model Link](https://huggingface.co/NousResearch/Hermes-2-Pro-Llama-3-8B-GGUF)

[Docker Engine/ Desktop](https://www.docker.com/products/docker-desktop/)

### Installing

A step by step series of examples that tell you how to get a development env running.

1. Running the Searxng stack

```
cd searxng-docker
# Compose the stack and run it in detach mode
docker compose up -d
```

2. Running the FastAPI server

```
cd luminari_server
# Build the image
docker build -t luminari_server .
# Run the Container
docker run -d --name luminari_server_ -p 4201:4201 luminari_server
```

3. Running the FastAPI server

```
cd luminari_app
# Build the image
docker build -t luminari_app .
# Run the Container
docker run -d --name luminari_app_ -p 3000:3000 luminari_app
```

4. Setup the llama.cpp server

```
# in the root run
python3 -m llama_cpp.server --config_file config_file
```


## Usage `<a name = "usage"></a>`

After building and running all images you should go to http://localhost:3000 and see the Luminari application running.
