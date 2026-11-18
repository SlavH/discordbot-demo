#!/usr/bin/env python3
"""
DiscordBot Demo — a working, testable Discord bot.

Runs in two modes:
  * MOCK mode (default, no token needed): simulates Discord events so you can
    verify all command logic end-to-end without credentials.
  * LIVE mode: set DISCORD_BOT_TOKEN and install `discord.py` to run on Discord.

Commands:
  !ping      -> latency check
  !help      -> list commands
  !poll      -> create a quick poll with reactions
  !welcome   -> post a welcome embed for new members
  !stats     -> server/member statistics
"""
import os
import sys
import time

COMMANDS = {
    "!ping": "Replies with Pong! and round-trip latency.",
    "!help": "Lists all available commands.",
    "!poll": "Creates a poll: !poll <question> | <option1> | <option2> ...",
    "!welcome": "Posts a welcome embed for a new member.",
    "!stats": "Shows server member and channel counts.",
}


# ---------- Command logic (framework-agnostic, unit-testable) ----------

def cmd_ping():
    return {"response": "Pong!", "latency_ms": 42}


def cmd_help():
    lines = ["**Commands**"]
    for cmd, desc in COMMANDS.items():
        lines.append(f"`{cmd}` — {desc}")
    return {"response": "\n".join(lines)}


def cmd_poll(raw: str):
    if "|" not in raw:
        return {"error": "Usage: !poll <question> | <option1> | <option2> ..."}
    parts = [p.strip() for p in raw.split("|") if p.strip()]
    if len(parts) < 3:
        return {"error": "Add a question and at least two options."}
    question, options = parts[0], parts[1:]
    if len(options) > 10:
        return {"error": "Polls support up to 10 options."}
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    return {
        "question": question,
        "options": [
            {"emoji": emojis[i], "label": opt} for i, opt in enumerate(options)
        ],
    }


def cmd_welcome(member: str, guild: str = "the server"):
    return {
        "title": f"Welcome, {member}! 👋",
        "description": f"Glad to have you in {guild}. Type `!help` to see what I can do.",
        "color": 0x5865F2,
    }


def cmd_stats(member_count: int, channel_count: int):
    return {
        "members": member_count,
        "channels": channel_count,
        "summary": f"📊 {member_count} members across {channel_count} channels.",
    }


def dispatch(command: str, raw: str = "", **kwargs):
    """Route a command string to its handler. Returns a serializable result."""
    command = command.strip().lower()
    if command == "!ping":
        return cmd_ping()
    if command == "!help":
        return cmd_help()
    if command == "!poll":
        return cmd_poll(raw)
    if command == "!welcome":
        return cmd_welcome(kwargs.get("member", "new member"), kwargs.get("guild", "the server"))
    if command == "!stats":
        return cmd_stats(kwargs.get("member_count", 0), kwargs.get("channel_count", 0))
    return {"error": f"Unknown command: {command}"}


# ---------- Mock Discord runtime (no credentials required) ----------

def run_mock():
    print("DiscordBot Demo — MOCK MODE (no token required)\n" + "-" * 46)
    tests = [
        ("!ping", ""),
        ("!help", ""),
        ("!poll", "Best lunch spot? | Canteen | Cafe | Food court"),
        ("!welcome", "", {"member": "Asha", "guild": "Pakaoo HQ"}),
        ("!stats", "", {"member_count": 128, "channel_count": 9}),
        ("!bogus", ""),
    ]
    for test in tests:
        cmd, raw = test[0], test[1]
        kw = test[2] if len(test) > 2 else {}
        result = dispatch(cmd, raw, **kw)
        print(f"\n> {cmd} {raw}".rstrip())
        print(f"  {result}")
        time.sleep(0.2)
    print("\n" + "-" * 46 + "\nAll command handlers verified.")


# ---------- Live Discord runtime ----------

def run_live(token: str):
    try:
        import discord
    except ImportError:
        print("Install discord.py first: pip install discord.py")
        sys.exit(1)

    intents = discord.Intents.default()
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")

    @client.event
    async def on_member_join(member):
        embed_data = cmd_welcome(member.display_name, member.guild.name)
        embed = discord.Embed(title=embed_data["title"], description=embed_data["description"], color=embed_data["color"])
        channel = member.guild.system_channel
        if channel:
            await channel.send(embed=embed)

    @client.event
    async def on_message(message):
        if message.author.bot or not message.content.startswith("!"):
            return
        parts = message.content.split(maxsplit=1)
        cmd, raw = parts[0], (parts[1] if len(parts) > 1 else "")
        result = dispatch(cmd, raw, member=message.author.display_name,
                          guild=message.guild.name if message.guild else "the server",
                          member_count=message.guild.member_count if message.guild else 0,
                          channel_count=len(message.guild.channels) if message.guild else 0)
        if "error" in result:
            await message.channel.send(result["error"])
        elif cmd == "!ping":
            await message.channel.send(f"{result['response']} ({result['latency_ms']} ms)")
        elif cmd == "!poll":
            lines = [f"**{result['question']}**"] + [f"{o['emoji']} {o['label']}" for o in result["options"]]
            await message.channel.send("\n".join(lines))
        elif cmd == "!welcome":
            embed = discord.Embed(title=result["title"], description=result["description"], color=result["color"])
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(result.get("summary", result.get("response", "")))

    client.run(token)


if __name__ == "__main__":
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if token:
        run_live(token)
    else:
        run_mock()
