# palera1n Bot Rewrite (maybe: Bridget)

If you want to help, join us at: [Discord](https://discord.gg/palera1n)

## Running:
Write an .env file (should be similar enough to GIR's .env, however the mongodb server is hardcoded to localhost:27017, need to change)
`pdm install`
`pdm run bot`

## Goals:
1. Tries to be 99% compatible with GIR
2. New codebase
3. Speed
4. Multi-Threading

## Testing:
While in development stage, you do not need to do very extensive tests AND may do commits directly to `main`. Once the bot is released, only bug fixes should be directly pushed to `main`, otherwise to `development` (to be made once released)
