import io
import os
import ast
import nextcord
import colorama
import traceback
import contextlib

from nextcord.ext import commands

whitelist_ids = []
colorama.init(convert=True)
bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all(), owner_ids=set(whitelist_ids))

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)
        
@bot.event
async def on_ready():
    print(colorama.Fore.GREEN + f"logged in as {bot.user.name}#{bot.user.discriminator}({str(bot.user.id)})" + colorama.Fore.RESET)
    
@bot.event
async def on_command_error(_error, error):
	if isinstance(error, commands.errors.NotOwner):
		await _error.reply("あなたはそのコマンドを実行出来ません。")
	else:
		raise error

@bot.command()
@commands.is_owner()
async def run(run):
    await run.reply("実行するpythonコードを送信して下さい。")
    def check_author(m):
        return m.author.id == run.author.id
    code = await bot.wait_for("message", check=check_author).content.strip("` ")
    code = "\n".join(f"    {i}" for i in code.splitlines())
    parsed_body = ast.parse(f"async def _eval_expr():\n{code}")
    body = parsed.body[0].body
    insert_returns(body)
    exec(compile(parsed_body, filename="<runcommand>", mode="exec"))
    stdout_result = io.StringIO("none") # 出力
    return_result = "none" # 返り値
    color_code = 0x00ff00
    try:
        with contextlib.redirect_stdout(stdout_result):
            _return_result = (await eval("_eval_expr()"))
        if _return_result != None:
            return_result = _return_result
    except:
        return_result = traceback.format_exc()
        color_code = 0xff0000
    embed = nextcord.Embed(title="Eval実行結果", description="run(eval)コマンドの実行結果です。\n**エラーは返り値に表示されます。**", color=color_code)
    embed.add_field(name="出力結果", value=f"```powershell\n{stdout_result.getvalue()}\n```", inline=False)
    embed.add_field(name="返り値", value=f"```powershell\n{return_result}\n```", inline=False)
    await run.reply(embed=embed)
    
bot.run(os.getenv("TOKEN"))
