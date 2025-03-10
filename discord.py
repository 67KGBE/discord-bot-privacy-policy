import discord
from discord.ext import commands
import asyncio

TOKEN = "1348787517746315487"  # Replace with your bot token
GUILD_ID = 1333604414929240105  # Replace with your Discord server ID
LOG_CHANNEL_ID = 1348792944211136615  # Replace with the log channel ID
CATEGORY_ID = 1333606291435815072  # Replace with the ticket category ID

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@client.event
async def on_ready():
    print(f"Triple Tickets Bot is online as {client.user}")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.id}")
        
        if existing_channel:
            await interaction.response.send_message(f"You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(f"ticket-{interaction.user.id}", category=category, overwrites=overwrites)
        await ticket_channel.send(f"Welcome {interaction.user.mention}! A staff member will assist you shortly.", view=CloseTicketView())
        await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

    @discord.ui.button(label="📜 View All Tickets", style=discord.ButtonStyle.blurple, custom_id="view_tickets")
    async def view_tickets(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        tickets = [channel.mention for channel in guild.text_channels if channel.name.startswith("ticket-")]
        
        if not tickets:
            await interaction.response.send_message("No open tickets found.", ephemeral=True)
        else:
            await interaction.response.send_message("Open Tickets:\n" + "\n".join(tickets), ephemeral=True)
    
    @discord.ui.button(label="📂 My Tickets", style=discord.ButtonStyle.blurple, custom_id="my_tickets")
    async def my_tickets(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user_tickets = [channel.mention for channel in guild.text_channels if channel.name == f"ticket-{interaction.user.id}"]
        
        if not user_tickets:
            await interaction.response.send_message("You have no open tickets.", ephemeral=True)
        else:
            await interaction.response.send_message("Your Tickets:\n" + "\n".join(user_tickets), ephemeral=True)
    
    @discord.ui.button(label="📁 Previous Tickets", style=discord.ButtonStyle.gray, custom_id="previous_tickets")
    async def previous_tickets(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_channel = client.get_channel(LOG_CHANNEL_ID)
        history = [message async for message in log_channel.history(limit=100) if f"ticket-{interaction.user.id}" in message.content]
        
        if not history:
            await interaction.response.send_message("You have no previous tickets logged.", ephemeral=True)
        else:
            logs = "\n".join([f"{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}: {msg.content}" for msg in history])
            await interaction.response.send_message(f"Your Previous Tickets:\n```{logs[:2000]}```", ephemeral=True)

    @discord.ui.button(label="⚙️ Support Info", style=discord.ButtonStyle.gray, custom_id="support_info")
    async def support_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Support Information", description="For urgent issues, contact staff directly.", color=discord.Color.orange())
        embed.add_field(name="📩 Open a Ticket", value="Use the button to create a new support ticket.", inline=False)
        embed.add_field(name="📜 View Tickets", value="Check active tickets.", inline=False)
        embed.add_field(name="📂 My Tickets", value="View your tickets.", inline=False)
        embed.add_field(name="📁 Previous Tickets", value="View your closed ticket history.", inline=False)
        embed.add_field(name="❌ Close Ticket", value="Only staff can close tickets when resolved.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.command()
async def setup(ctx):
    view = TicketView()
    embed = discord.Embed(title="Triple Tickets Support", description="Click a button below for ticket options!", color=discord.Color.blue())
    await ctx.send(embed=embed, view=view)

@client.command()
async def help(ctx):
    embed = discord.Embed(title="Triple Tickets Help", color=discord.Color.green())
    embed.add_field(name="!setup", value="Creates the ticket system.", inline=False)
    embed.add_field(name="!help", value="Displays this help message.", inline=False)
    await ctx.send(embed=embed)

async def main():
    async with client:
        client.add_view(TicketView())
        client.add_view(CloseTicketView())
        await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
