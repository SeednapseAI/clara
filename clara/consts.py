import os
from pathlib import Path


USER_HOME = Path.home()


BASE_PERSIST_PATH = os.path.join(
    os.environ.get("XDG_CACHE_HOME", Path.joinpath(USER_HOME, ".cache")), "clara"
)


# CONFIG_PATH = os.path.join(
#     os.environ.get("XDG_CONFIG_HOME", Path.joinpath(USER_HOME, ".config")), "clara",
# )


PROMPT_PREFIX = (
    # "Assistant name is CLARA: Code Language Assistant & Repository Analyzer "
    # "(or just Clara). "
    # "Assistant is a very enthusiastic AI-powered chatbot designed to assist "
    # "developers in navigating unfamiliar code repositories, helping "
    # "during the on-boarding process for new projects, or "
    # "deciphering legacy code. "
    # "In order to do that you're going to be provided by context extracted "
    # "from a code repository"
    # "Answer using markdown (including related code snippets if available using markdown "
    # "code blocks).",
    # "Hi, I'm Clara! 📜🔍🤖"
    # "",
)


WILDCARDS = (
    # Python
    "*.py",
    # Markdown
    "*.md",
    "*.mdx",
    # reStructuredText
    "*.rst",
    # C
    "*.c",
    "*.h",
    # C++
    "*.cpp",
    "*.hpp",
    "*.cc",
    "*.hh",
    # C#
    "*.cs",
    # Java
    "*.java",
    # JavaScript
    "*.js",
    # TypeScript
    "*.ts",
    # Ruby
    "*.rb",
    # PHP
    "*.php",
    # Swift
    "*.swift",
    # Objective-C
    "*.m",
    "*.mm",
    "*.h",
    # Kotlin
    "*.kt",
    # Scala
    "*.scala",
    # Lua
    "*.lua",
    # Go
    "*.go",
    # Rust
    "*.rs",
    # Dart
    "*.dart",
    # Haskell
    "*.hs",
    # Shell
    "*.sh",
    "*.bash",
    # Perl
    "*.pl",
    "*.pm",
    # R
    "*.r",
    # MATLAB
    "*.m",
    # Groovy
    "*.groovy",
    # Julia
    "*.jl",
    # Elixir
    "*.ex",
    "*.exs",
    # Elm
    "*.elm",
    # Erlang
    "*.erl",
    "*.hrl",
    # F#
    "*.fs",
    "*.fsx",
    # SQL
    "*.sql",
    # XML
    "*.xml",
    # HTML
    "*.html",
    "*.htm",
    # CSS
    "*.css",
    # SASS/SCSS
    "*.scss",
    "*.sass",
    # LESS
    "*.less",
    # JSON
    # "*.json",
    # YAML
    # "*.yml",
    # "*.yaml",
    # TOML
    # "*.toml",
    # INI
    # "*.ini",
    # Properties
    # "*.properties",
    # Dockerfile
    "Dockerfile",
    # Makefile
    # "Makefile",
    # Gradle
    # "*.gradle",
    # CMake
    # "CMakeLists.txt",
    # "*.cmake",
    # Vagrantfile
    # "Vagrantfile",
    # Gitignore
    # ".gitignore",
    # README
    "README",
)


HELP_MESSAGE = """
/context -- show the context for the last answer

/edit    -- open editor to edit the message

/quit
/exit    -- exit (you can use also CTRL-C or CTRL-D)

/help    -- show this message
"""
