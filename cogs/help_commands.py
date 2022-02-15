from typing import Optional, Set
import nextcord
from nextcord import embeds
from nextcord.colour import Color
from nextcord.ext import commands
import sys


#parent directory import
sys.path.append('DatabaseRelated')
sys.path.append('cogs')

class MyHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"

    async def _help_embed(self, title: str, description: Optional[str] = None, 
    mapping:Optional[dict] = None, command_set: Optional[Set[commands.Command]] = None):
        # avatar = self.context.bot.user.avatar or self.context.bot.user.default_avatar
        embed= embeds.Embed(title= title, colour = nextcord.Colour.from_rgb(121,180,183))
        if description:
            embed.description = description
        if command_set:
            #show help for all commands in column
            filtered = await self.filter_commands(command_set, sort = True)
            for command in filtered:
                embed.add_field(name = self.get_command_signature(command),value = command.short_doc or "...", inline = False)
        elif mapping:
            #add short description of cogs
            for cog, command_set in mapping.items():
                filtered = await self.filter_commands(command_set, sort =True)
                if not filtered:
                    continue
                name = cog.qualified_name if cog else "Other"
                cmd_list = "\u2002".join(
                    f"`{self.context.clean_prefix}{cmd.name}`" for cmd in filtered
                )
                value = (
                    f"{cog.description}\n{cmd_list}"
                    if cog and cog.description
                    else cmd_list
                )
                # embed.set_author(name=self.context.bot.user.name, icon_url=avatar.url)
                embed.add_field(name=name, value=value)
        return embed 
    
    async def send_bot_help(self, mapping:dict):
        embed =await self._help_embed(
            title = "Help with Pew Pew",
            description=self.context.bot.description,
            mapping = mapping
        )      
        
       
        await self.get_destination().send(embed= embed)
        

    async def send_command_help(self, command: commands.Command):
        embed = await self._help_embed(
            title= command.qualified_name,
            description= command.help,
            command_set = commands.commands if isinstance(command,commands.Group) else None
        )
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog:commands.Cog):
        embed = await self._help_embed(
            title= cog.qualified_name,
            description= cog.description,
            command_set=cog.get_commands()
        )
        await self.get_destination().send(embed=embed)

            

    send_group_help = send_command_help

    

class Help(commands.Cog):
    """Help Command"""
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command
    

def setup(client):
    client.add_cog(Help(client))