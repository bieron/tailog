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

or docker


Installation and setup
============

Clone the repo and run `./install` for installation on host.

Run ./docker-build and ./docker-run for dockerized run.

Fill `ansible/inventory` and run `ansible-playbook ansible/deploy.yml` to
remotely orchestrate multiple instances.


Author
======

https://github.com/bieron
