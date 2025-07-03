"""
Enhanced reaction handler for interactive Jewish learning features
Following discord.py best practices for event handling
"""
import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class ReactionHandler(commands.Cog):
    """Handles reaction-based interactions for enhanced user experience"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle reaction additions for interactive features"""
        # Ignore bot reactions
        if user.bot:
            return
        
        # Ignore reactions not on our messages
        if reaction.message.author != self.bot.user:
            return
        
        try:
            await self._handle_interactive_reaction(reaction, user)
        except Exception as e:
            logger.error(f"Error handling reaction: {e}")
    
    async def _handle_interactive_reaction(self, reaction, user):
        """Process specific reaction interactions"""
        message = reaction.message
        embeds = message.embeds
        
        if not embeds:
            return
        
        embed = embeds[0]
        title = embed.title or ""
        
        # Handle gematria calculator reactions
        if "Gematria Calculator" in title:
            await self._handle_gematria_reactions(reaction, user, embed)
        
        # Handle zmanim (halachic times) reactions
        elif "Halachic Times" in title:
            await self._handle_zmanim_reactions(reaction, user, embed)
        
        # Handle parsha study reactions
        elif "Parashat" in title:
            await self._handle_parsha_reactions(reaction, user, embed)
        
        # Handle halacha question reactions
        elif "Halacha Question" in title:
            await self._handle_halacha_reactions(reaction, user, embed)
        
        # Handle Daf Yomi reactions
        elif "Daf Yomi" in title:
            await self._handle_dafyomi_reactions(reaction, user, embed)
        
        # Handle learning path reactions
        elif "Learning Path" in title:
            await self._handle_learning_reactions(reaction, user, embed)
    
    async def _handle_gematria_reactions(self, reaction, user, embed):
        """Handle gematria calculator interactive reactions"""
        emoji = str(reaction.emoji)
        
        if emoji == "🔄":
            # Show additional gematria calculation methods
            new_embed = discord.Embed(
                title="🔢 Extended Gematria Methods",
                description="Additional calculation methods for deeper analysis",
                color=discord.Color.purple()
            )
            new_embed.add_field(
                name="📊 Available Methods",
                value="• **At-bash** - Reverse alphabet cipher\n• **Albam** - Alphabet substitution\n• **Ayik Bekar** - Special permutation\n• **Mispar Gadol** - Final letter values",
                inline=False
            )
            new_embed.set_footer(text="Contact administrator for advanced calculations")
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
        
        elif emoji == "📖":
            # Search for texts with same gematria value
            new_embed = discord.Embed(
                title="📚 Related Gematria Texts",
                description="Searching for texts with matching numerical values...",
                color=discord.Color.blue()
            )
            new_embed.add_field(
                name="🔍 Search Tips",
                value="Use `/search` command to find specific texts\nUse `/text` command to retrieve full passages",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
    
    async def _handle_zmanim_reactions(self, reaction, user, embed):
        """Handle zmanim (halachic times) interactive reactions"""
        emoji = str(reaction.emoji)
        
        if emoji == "📅":
            # Show tomorrow's times
            new_embed = discord.Embed(
                title="📅 Tomorrow's Zmanim",
                description="Use `/zmanim` command with tomorrow's date for precise times",
                color=discord.Color.blue()
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
        
        elif emoji == "🕯️":
            # Show candle lighting information
            new_embed = discord.Embed(
                title="🕯️ Candle Lighting Guide",
                description="Shabbat and Holiday Candle Lighting Times",
                color=discord.Color.gold()
            )
            new_embed.add_field(
                name="📏 Standard Times",
                value="• **Shabbat:** 18 minutes before sunset\n• **Holidays:** Usually same as Shabbat\n• **Location matters:** Check local customs",
                inline=False
            )
            new_embed.add_field(
                name="🔍 Get Exact Times",
                value="Use `/shabbat [location]` for precise candle lighting times",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
        
        elif emoji == "ℹ️":
            # Show zmanim explanations
            new_embed = discord.Embed(
                title="ℹ️ Zmanim Explanations",
                description="Understanding Halachic Times",
                color=discord.Color.dark_blue()
            )
            new_embed.add_field(
                name="🌅 Morning Times",
                value="• **Alot HaShachar:** Dawn - first light\n• **Misheyakir:** When you can distinguish\n• **Sunrise:** Sun becomes visible",
                inline=False
            )
            new_embed.add_field(
                name="🙏 Prayer Times",
                value="• **Latest Shma:** Deadline for morning Shma\n• **Latest Tfilla:** Deadline for morning prayers\n• **Chatzot:** Halachic noon",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
    
    async def _handle_parsha_reactions(self, reaction, user, embed):
        """Handle Torah portion study interactive reactions"""
        emoji = str(reaction.emoji)
        
        if emoji == "📝":
            # Show commentary options
            new_embed = discord.Embed(
                title="📝 Torah Commentary Guide",
                description="Classical commentaries for Torah study",
                color=discord.Color.gold()
            )
            new_embed.add_field(
                name="👨‍🏫 Classical Commentators",
                value="• **Rashi** - Basic understanding\n• **Ibn Ezra** - Grammar and context\n• **Ramban** - Mystical insights\n• **Sforno** - Philosophical approach",
                inline=False
            )
            new_embed.add_field(
                name="🔍 Access Commentaries",
                value="Use `/commentary [verse] [commentator]` for specific insights",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
        
        elif emoji == "🔍":
            # Show theme exploration
            new_embed = discord.Embed(
                title="🔍 Torah Themes & Lessons",
                description="Explore deeper meanings in the weekly portion",
                color=discord.Color.green()
            )
            new_embed.add_field(
                name="🎯 Study Approaches",
                value="• Look for recurring patterns\n• Connect to personal growth\n• Find contemporary relevance\n• Explore character development",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
    
    async def _handle_halacha_reactions(self, reaction, user, embed):
        """Handle halacha question interactive reactions"""
        emoji = str(reaction.emoji)
        
        if emoji == "📖":
            # Show halachic sources
            new_embed = discord.Embed(
                title="📖 Halachic Source Materials",
                description="Primary sources for Jewish law study",
                color=discord.Color.blue()
            )
            new_embed.add_field(
                name="📚 Essential Sources",
                value="• **Shulchan Aruch** - Code of Jewish Law\n• **Mishnah Berurah** - Modern commentary\n• **Responsa Literature** - Rabbinic decisions\n• **Contemporary Poskim** - Modern authorities",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
        
        elif emoji == "👨‍🏫":
            # Provide rabbi referral guidance
            new_embed = discord.Embed(
                title="👨‍🏫 Finding Rabbinic Guidance",
                description="How to find qualified halachic authorities",
                color=discord.Color.purple()
            )
            new_embed.add_field(
                name="🔍 Finding a Rabbi",
                value="• Contact local synagogues\n• Ask community members for recommendations\n• Look for Orthodox authorities for halachic questions\n• Consider online halachic resources",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
    
    async def _handle_dafyomi_reactions(self, reaction, user, embed):
        """Handle Daf Yomi study interactive reactions"""
        emoji = str(reaction.emoji)
        
        if emoji == "📝":
            # Show note-taking tips
            new_embed = discord.Embed(
                title="📝 Daf Yomi Study Notes",
                description="Effective note-taking for Talmud study",
                color=discord.Color.dark_blue()
            )
            new_embed.add_field(
                name="✍️ Note-Taking Tips",
                value="• Track key concepts and terms\n• Note questions for further study\n• Connect to previously learned material\n• Record practical halachic applications",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
        
        elif emoji == "👥":
            # Show study group information
            new_embed = discord.Embed(
                title="👥 Daf Yomi Study Groups",
                description="Benefits of collaborative Talmud study",
                color=discord.Color.green()
            )
            new_embed.add_field(
                name="🤝 Study Partnership Benefits",
                value="• **Chavruta** - Traditional paired study\n• Different perspectives on difficult passages\n• Motivation and accountability\n• Enhanced understanding through discussion",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass
    
    async def _handle_learning_reactions(self, reaction, user, embed):
        """Handle learning path interactive reactions"""
        emoji = str(reaction.emoji)
        
        if emoji == "📅":
            # Show study schedule recommendations
            new_embed = discord.Embed(
                title="📅 Jewish Learning Schedule",
                description="Structured approach to Torah study",
                color=discord.Color.green()
            )
            new_embed.add_field(
                name="🗓️ Daily Learning Cycles",
                value="• **Daf Yomi** - Daily Talmud page\n• **Parsha** - Weekly Torah portion\n• **Mishnah Yomi** - Daily Mishnah\n• **Rambam Yomi** - Daily Maimonides",
                inline=False
            )
            
            try:
                await user.send(embed=new_embed)
            except discord.Forbidden:
                pass

async def setup(bot):
    """Setup function for loading the cog"""
    await bot.add_cog(ReactionHandler(bot))