About
=====

This is a PoC HTTP interface for tailing /var/log files. Supports
- line limiting (param `n`)
- basic string search (param `match`)
- async delegation to other, remote instances (param `delegate`)


Requirements
============

- python3
- python3-venv
- python3-pip
- libmagic

or docker


Installation and setup
======================

Clone the repo and run `./install` for installation on host.

Run `./docker-build` and `./docker-run` for dockerized run.

Fill `ansible/inventory` and run `ansible-playbook ansible/deploy.yml` to
remotely orchestrate multiple instances.


Interface
=========

There are two endpoints:

- /rest/files

    Lists all readable text files under /var/log

    Params:
    - `format`: 'json' (default) or 'text'

- /rest/files/<path>

    Tails `path`, returns lines in reversed order. Only supports regular text
    files you have permission to read (no binary, symlinks, etc.)

    Params:
    - `n`: limit number of lines, default 10, negative number means unlimited
    - `match`: only show lines containing `match`
    - `trim`: controls whether to include trailing newline or not, ignored in
    text format
    - `format`: 'json' (default) or 'text'
    - `delegate`: takes a list of HTTP addresses (including scheme and port),
    and instead of running given query itself, the server acts as a master node,
    querying all given addresses for that file


Testing
=======

Run `pip3 install -r t/requirements.txt` and then just `pytest`.


Author
======

https://github.com/bieron

Feedback welcomed.
