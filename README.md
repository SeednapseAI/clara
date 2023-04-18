CLARA: Code Language Assistant & Repository Analyzer 📜🔍🤖
========================================================

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Clara is a tool to help developers understand and work with a code repository.

***Note that the code for creating the vector database is loaded the first time you open the chat in the code repository. Subsequent chats will use the preloaded database, ensuring faster response times."***

https://user-images.githubusercontent.com/538203/232823179-586ef7be-370c-4e65-8cf7-913d066ad2c3.mp4

***This project is currently in its early stages of development and is considered a work in progress. You may encounter some issues, or incomplete features. We appreciate your understanding and patience as we continue to refine and enhance the project. Your feedback will help us improve and shape this project.***

## Overview

Clara is an AI-driven solution created to help developers effortlessly explore new or unfamiliar code repositories. It proves especially beneficial during the onboarding phase for new projects or when decoding legacy code.

Moving forward, Clara aims to offer assistance in various tasks, including documentation, auditing, and feature development, among others.

## Features

- Intelligent code and documentation analysis.
- Integrated Database
    - Utilizes local storage through [ChromaDB](https://www.trychroma.com/).
    - Maintains data persistence for individual code repositories.
    - Offers optional in-memory storage without persistence.
- Context-aware short-term memory: Gathers information from ongoing conversations.

## Install

With:

```
pipx install clara-ai
```

Or:

```
pip3 install clara-ai
```

## Usage

Firstly, set an environment variable with your OpenAI API key:

```
export OPENAI_API_KEY="XXXXXX"
```

Then, use the command:

```
$ clara chat [PATH]
```

If the path is omitted then '.' will be used.

To exit use `CTRL-C` or `CTRL-D`, or commands `/quit` or `/exit`.

All commands:

```
     ask
       Ask a question about the code from the command-line.

     chat
       Chat about the code.

     clean
       Delete vector DB for a given path.

     config
       Show config for a given path.
```

## Chat commands

During chat you can also use this commands:

```
/context -- show the context for the last answer

/edit    -- open editor to edit the message

/quit
/exit    -- exit (you can use also CTRL-C or CTRL-D)

/help    -- show this message
```

## Configuration

Run `clara config` to know from where the program is going to read the configuration. Usually this path is going to be `/.config/clara/clara.yaml`.

For now, there is only a couple of parameters. This is a sample configuration with the default values:

```
llm:
  model: gpt-3.5-turbo
index:
  # similarity or mmr
  search: similarity
  k: 5
```

Change the model for `gpt-4` if you have access to it.

## Cache

Vector DB and chat history are stored in a cache directory, per code analyzed. Use `clara config` to know the path to this directory.

You can remove manually this directory, if you want to refresh the data stored, or simply use the command `clara clean`.

If you want to chat with the code without reading/storing the vector DB (using the DB in memory), use the command `clara [PATH] --memory-storage`.

## Roadmap

- [x] Short-term history
- [x] Configurable LLM
- [ ] Agent
  - [ ] Access to filesystem
- [ ] Features
  - [ ] Work with remote Git repositories
  - [ ] Document code with docstrings
  - [ ] Test creation
  - [ ] Audit code
  - [ ] Refactoring
