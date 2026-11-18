# DiscordBot — Working Custom Discord Bot Demo (Type C)

Built for the r/discordbots lead (u/Foreign_Dingo4859) who explicitly wants a bot that works, not ChatGPT output.

## Live Demo
https://slavh.github.io/discordbot-demo/

## Files
- `bot.py` — working Discord.py bot with 5 commands + framework-agnostic handlers
- `index.html` — public demo page with interactive command simulator
- `styles.css` — styling
- `README.md` — this file

## Commands
| Command | Description |
|---------|-------------|
| `!ping` | Latency check with round-trip timing |
| `!help` | Auto-generated command list |
| `!poll` | Poll with up to 10 numbered reaction options |
| `!welcome` | Welcome embed, fired on member-join event |
| `!stats` | Member/channel counts |

## Run it
```bash
python3 bot.py                 # MOCK mode — verifies all handlers, no token needed
DISCORD_BOT_TOKEN=xxx python3 bot.py   # LIVE mode (pip install discord.py)
```

## Design notes
Command logic lives in plain functions (`dispatch`, `cmd_*`) that are framework-agnostic and unit-testable. Mock mode validates every handler before any Discord credentials are involved. Live mode wires the same tested handlers into `discord.py` events (`on_message`, `on_member_join`). Extending with custom commands = add one function + one dispatch entry.

## Price note
Fair-market $40–$250 depending on command complexity and integrations.
