CLARA: Code Language Assistant & Repository Analyzer 📜🔍🤖
========================================================

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Clara is a tool to help developers understand and work with a code repository.

![Features](https://github.com/SeednapseAI/clara/raw/master/images/screenshot.png)

***This project is currently in its early stages of development and is considered a work in progress. You may encounter some issues, or incomplete features. We appreciate your understanding and patience as we continue to refine and enhance the project. Your feedback will help us improve and shape this project.***

## Introduction

Clara is an AI-powered tool designed to assist developers in navigating unfamiliar code repositories, making it highly valuable during the on-boarding process for new projects, or when deciphering legacy code.

In the future, Clara will also provide support for tasks such as documentation, auditing, and developing new features, among others.

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

Run `poetry run clara config` to know from where the program is going to read the configuration. Usually this path is going to be `/.config/clara/clara.yaml`.

For now, there is only one parameter to change. This is a sample configuration:

```
llm:
  model: gpt-3.5-turbo
```

Change the model for `gpt-4` if you have access to it.

## Cache

Vector DB and chat history are stored in a cache directory, per code directory. Use `poetry run clara config` to know the path to this directory.

You can remove manually this directory, if you want to refresh the data stored, or simply use the command `poetry run clara clean`.

If you want to chat with the code without reading/storing the vector DB (using the DB in memory), use the command `poetry run clara [PATH] --memory-storage`.

## Roadmap

- [x] Short-term history
- [x] Configurable LLM
- [ ] Tools
  - [ ] Document code with docstrings
  - [ ] Test creation
  - [ ] Audit code
  - [ ] Refactoring
