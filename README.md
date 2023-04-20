# Bridget
[![CodeQL](https://github.com/palera1n/bot-rewrite/actions/workflows/codeql.yml/badge.svg)](https://github.com/palera1n/bot-rewrite/actions/workflows/codeql.yml)

If you want to help, join us at: [Discord](https://discord.gg/palera1n). We also have a testing server at: [Discord](https://discord.gg/55A4Xjc9RW)

# Running

1. Write an `.env` file from `.env.example`
2. `pdm install`
3. Fill in the ids in `setup.py`
4. `pdm run setup`
5. `pdm run bot`

# Goals

1. Tries to be 99% compatible with GIR
2. New codebase
3. Speed
4. Multi-Threading

# Testing

While in development stage, you do not need to do very extensive tests AND may do commits directly to `main`. Once the bot is released, only bug fixes should be directly pushed to `main`, otherwise to `development` (to be made once released)

# Contributing

Please follow [the contribution guidelines](https://github.com/palera1n/bot-rewrite/blob/main/CONTRIBUTING.md).

# Vulnerabilities

If you find a security vulnerability, please email `me@itsnebula.net`, and **sign your email** with [this key](https://static.itsnebula.net/gpgkey.asc) (`FB04F6C8EC56DA32F33008C53D1B28A5FACCB53B`).
