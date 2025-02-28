import discord
from discord import app_commands, Activity, ActivityType, Embed
import random
import yt_dlp
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import lyricsgenius

# configuração do Spotify
SPOTIFY_CLIENT_ID = "****************"
SPOTIFY_CLIENT_SECRET = "**********************"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# Configuração do Genius
GENIUS_API_KEY = "*******************************"
genius = lyricsgenius.Genius(GENIUS_API_KEY)

# Configurações do yt-dlp
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': 'True',
    'extract_flat': True,  
}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class AgonyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.queues = {}  # Dicionário para armazenar filas por servidor
        self.last_song = {}  # Dicionário para armazenar a última música adicionada à fila
        self.current_song = {}  # Dicionário para armazenar a música atual que está tocando
        self.user_history = {}  # Dicionário para armazenar o histórico de músicas por usuário
        self.skip_votes = {}  # Dicionário para armazenar votos de skip por servidor
        self.loop_states = {}  # Dicionário para armazenar o estado de loop por servidor
        self.queue_loop_states = {}  # Dicionário para armazenar o estado de loop da fila por servidor

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        # Define o status personalizado
        activity = Activity(name="Romantize Sua Agonia", type=ActivityType.listening)
        await self.change_presence(activity=activity)
        print(f"{self.user} está online!")

    def get_queue(self, guild_id):
        #retorna a fila de músicas de um servidor
        if guild_id not in self.queues:
            self.queues[guild_id] = []  # cria uma nova fila se não existir
        return self.queues[guild_id]

    def get_last_song(self, guild_id):
        #retorna a ultima musica tocada ou adicionada a fila"
        return self.last_song.get(guild_id, None)

    async def play_next(self, interaction):
        queue = self.get_queue(interaction.guild.id)
        if not queue:
            await interaction.followup.send("🎵 Fila de músicas vazia.", ephemeral=True)
            return

        url, song_name = queue.pop(0)  # pega a primeira musica da fila
        self.last_song[interaction.guild.id] = song_name  # armazena a última música adicionada a fila
        self.current_song[interaction.guild.id] = song_name  # armazena a musica atual que está tocando
        vc = interaction.guild.voice_client

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                vc.play(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS),
                    after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.loop))
                await interaction.followup.send(f"🎵 Tocando agora: **{song_name}**")

                if interaction.guild.id in bot.loop_states and bot.loop_states[interaction.guild.id]:
                    queue.append((url, song_name))
            except Exception as e:
                await interaction.followup.send(f"Erro ao tocar a música: {e}", ephemeral=True)
                await self.play_next(interaction)  

bot = AgonyBot()

# comando pra testar a sorte
@bot.tree.command(name="testar_sorte", description="Testa sua sorte")
async def testarSorte(interaction: discord.Interaction):
    eventos = ["Sorte pra carai 🍀", "Boa Sorte 😊", "Neutro 🤔", "Azar 😕", "Azarado pra porra 😵"]
    pesos = [5, 15, 30, 35, 15]  
    resultado = random.choices(eventos, weights=pesos, k=1)[0]

    await interaction.response.send_message(f"🎰 {interaction.user.mention} girou a roleta e tirou: **{resultado}**")

# 🎵 Comandos de música
@bot.tree.command(name="play", description="Toca uma música do YouTube, Spotify ou busca pelo nome")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()  

    voice_state = interaction.user.voice
    if not voice_state:
        await interaction.followup.send("Você precisa estar em um canal de voz para tocar música!", ephemeral=True)
        return

    channel = voice_state.channel
    vc = interaction.guild.voice_client

    if not vc or not vc.is_connected():
        vc = await channel.connect()

    # verifica se a query é um link do Spotify
    if "spotify.com/track" in query:
        url, song_name = get_youtube_link_from_spotify(query)
        if not url:
            await interaction.followup.send("Não consegui encontrar essa música no YouTube.", ephemeral=True)
            return
    # Vvrifica se a query é um link do YouTube
    elif query.startswith(("http://", "https://")):
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                song_name = info['title']
                url = query  # Usa o link diretamente
            except Exception as e:
                await interaction.followup.send(f"Erro ao extrair informações do vídeo: {e}", ephemeral=True)
                return
    # se não for um link faz uma busca no YouTube
    else:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                # busca no YouTube usando a query do usuário
                info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                if not info['entries']:
                    await interaction.followup.send("Não encontrei nenhum resultado no YouTube.", ephemeral=True)
                    return

                # cria um Embed para exibir as opções
                embed = discord.Embed(
                    title="🎵 Escolha uma música",
                    description="Digite o número correspondente à música que deseja tocar:",
                    color=discord.Color.blue()
                )

                # adiciona as opções ao Embed
                entries = info['entries']
                for i, entry in enumerate(entries):
                    embed.add_field(
                        name=f"{i + 1}. {entry['title']}",
                        value=f"Duração: {entry.get('duration', 'N/A')}s",
                        inline=False
                    )

                # envia o Embed com as opções
                await interaction.followup.send(embed=embed)

                # aguarda a resposta do usuário
                def check(m):
                    return m.author == interaction.user and m.channel == interaction.channel and m.content.isdigit()

                try:
                    msg = await bot.wait_for('message', timeout=30.0, check=check)
                    choice = int(msg.content) - 1
                    if 0 <= choice < len(entries):
                        video_url = entries[choice]['url']
                        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl_detail:
                            video_info = ydl_detail.extract_info(video_url, download=False)
                            url = video_info['url']
                            song_name = video_info['title']
                    else:
                        await interaction.followup.send("Escolha inválida.", ephemeral=True)
                        return
                except asyncio.TimeoutError:
                    await interaction.followup.send("Tempo esgotado. Tente novamente.", ephemeral=True)
                    return

            except Exception as e:
                await interaction.followup.send(f"Erro ao buscar a música: {e}", ephemeral=True)
                return

    # Adiciona a música à fila
    queue = bot.get_queue(interaction.guild.id)
    queue.append((url, song_name))
    bot.last_song[interaction.guild.id] = song_name  # armazena a última música

    user_id = interaction.user.id
    if user_id not in bot.user_history:
        bot.user_history[user_id] = []  # cria uma lista vazia se não existir
        bot.user_history[user_id].append(song_name)  # adiciona a música ao histórico

    # Se não estiver tocando nada, começa a tocar
    if not vc.is_playing():
        await bot.play_next(interaction)
    else:
        await interaction.followup.send(f"🎵 **{song_name}** adicionada à fila.")

@bot.tree.command(name="stop", description="Para a música e desconecta")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        await vc.disconnect()
        bot.get_queue(interaction.guild.id).clear()  # Limpa a fila
        bot.current_song[interaction.guild.id] = None  # Limpa a música atual
        await interaction.response.send_message("⏹️ Música parada e bot desconectado!")
    else:
        await interaction.response.send_message("O bot não está em um canal de voz.")

@bot.tree.command(name="pause", description="Pausa a música")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸️ Música pausada.")
    else:
        await interaction.response.send_message("Não há música tocando.")

@bot.tree.command(name="resume", description="Continua a música pausada")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Música retomada.")
    else:
        await interaction.response.send_message("A música não está pausada.")

# Comando para votar em skip
@bot.tree.command(name="skip", description="Vote para pular a música atual")
async def voteskip(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    vc = interaction.guild.voice_client

    # Verifica se o bot está tocando música
    if not vc or not vc.is_connected() or not vc.is_playing():
        await interaction.response.send_message("Não estou tocando música no momento.", ephemeral=True)
        return

    # Verifica se o usuário está no mesmo canal de voz que o bot
    if interaction.user.voice.channel != vc.channel:
        await interaction.response.send_message("Você precisa estar no mesmo canal de voz que o bot para votar.", ephemeral=True)
        return

    # Inicializa a contagem de votos para o servidor
    if guild_id not in bot.skip_votes:
        bot.skip_votes[guild_id] = set()

    # Adiciona o voto do usuário
    bot.skip_votes[guild_id].add(interaction.user.id)
    total_votes = len(bot.skip_votes[guild_id])

    # Calcula o número de usuários no canal de voz
    total_members = len(vc.channel.members) - 1  

    # Verifica se a maioria votou para pular
    if total_votes >= (total_members // 2) + 1:  
        await interaction.response.send_message("✅ Voto para pular a música aceito. Pulando...")
        vc.stop()
        bot.skip_votes[guild_id].clear()  # Limpa os votos após o skip
    else:
        await interaction.response.send_message(f"🎵 Voto para pular registrado. {total_votes}/{total_members} votos necessários.")
async def play_next(self, interaction):
    guild_id = interaction.guild.id
    if guild_id in bot.skip_votes:
        bot.skip_votes[guild_id].clear()  # Limpa os votos ao trocar de música
    

@bot.tree.command(name="queue", description="Mostra a fila de músicas")
async def show_queue(interaction: discord.Interaction):
    queue = bot.get_queue(interaction.guild.id)
    if not queue:
        await interaction.response.send_message("🎵 A fila de músicas está vazia.")
        return

    queue_list = "\n".join([f"{i + 1}. {song_name}" for i, (_, song_name) in enumerate(queue)])
    await interaction.response.send_message(f"🎵 Fila de músicas:\n{queue_list}")

@bot.tree.command(name="clear", description="Limpa a fila de músicas")
async def clear_queue(interaction: discord.Interaction):
    queue = bot.get_queue(interaction.guild.id)
    queue.clear()
    await interaction.response.send_message("🗑️ Fila de músicas limpa.")

# Comando de letras
@bot.tree.command(name="lyrics", description="Mostra a letra da música atual ou de uma música específica")
async def lyrics(interaction: discord.Interaction, song_name: str = None):
    await interaction.response.defer()  # Evita timeout da interação

    # Se nenhum nome de música for fornecido, tenta pegar a música atual
    if not song_name:
        song_name = bot.get_last_song(interaction.guild.id)
        if not song_name:
            await interaction.followup.send("Não há música tocando e nenhum nome foi fornecido.", ephemeral=True)
            return

    # Função para extrair o artista e o nome da música do título
    def extract_artist_and_song(title):
        if " - " in title:
            artist, song = title.split(" - ", 1)
            song = song.split(" (")[0]  # Remove informações adicionais como "(Official Video)"
            return artist.strip(), song.strip()
        return None, title  # Se não houver separador, retorna o título completo

    # Limpa o nome da música (remove termos desnecessários)
    def clean_song_name(name):
        # Remove termos comuns que não fazem parte do nome da música
        terms_to_remove = ["Official Video", "Official Music Video", "MV", "HD", "Lyrics", "Official"]
        for term in terms_to_remove:
            name = name.replace(term, "").strip()
        return name

    # Limpa o nome da música e extrai artista e nome da música
    cleaned_song_name = clean_song_name(song_name)
    artist, song = extract_artist_and_song(cleaned_song_name)

    try:
        # Busca a letra da música no Genius
        if artist:
            # Se o artista foi extraído, busca com artista e nome da música
            song_result = genius.search_song(song, artist)
        else:
            # Caso contrário, busca apenas com o nome da música
            song_result = genius.search_song(song)

        if song_result:
            # Cria um embed para exibir a letra
            embed = discord.Embed(
                title=f"🎵 Letra de {song_result.title}",
                description=song_result.lyrics[:4096],  # Limita o tamanho da letra para caber no Embed
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"Não consegui encontrar a letra de **{cleaned_song_name}**.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Erro ao buscar a letra: {e}", ephemeral=True)

@bot.tree.command(name="historico", description="Mostra o histórico de músicas que você adicionou")
async def historico(interaction: discord.Interaction):
    user_id = interaction.user.id

    # Verifica se o usuário tem histórico
    if user_id not in bot.user_history or not bot.user_history[user_id]:
        await interaction.response.send_message("Você ainda não adicionou nenhuma música.", ephemeral=True)
        return

    # Obtém o histórico do usuário
    history = bot.user_history[user_id]

    # Limita o histórico aos últimos 10 itens (ou outro número desejado)
    history = history[-10:]  # Mostra apenas as últimas 10 músicas

    # Cria um Embed para exibir o histórico
    embed = discord.Embed(
        title=f"🎵 Histórico de {interaction.user.name}",
        description="Aqui estão as músicas que você adicionou recentemente:",
        color=discord.Color.blue()
    )

    # Adiciona as músicas ao Embed
    for i, song in enumerate(history, start=1):
        embed.add_field(name=f"{i}. {song}", value="\u200b", inline=False)  # \u200b é um espaço invisível

    await interaction.response.send_message(embed=embed)

# Comando para ativar/desativar o loop
@bot.tree.command(name="loop", description="Ativa ou desativa o loop da música atual")
async def loop(interaction: discord.Interaction):
    guild_id = interaction.guild.id

    # Inicializa o estado de loop para o servidor
    if guild_id not in bot.loop_states:
        bot.loop_states[guild_id] = False

    # Alterna o estado de loop
    bot.loop_states[guild_id] = not bot.loop_states[guild_id]
    state = "ativado" if bot.loop_states[guild_id] else "desativado"

    await interaction.response.send_message(f"🔁 Loop {state}.")

# Modificar a função play_next para suportar loop
async def play_next(self, interaction):
    queue = self.get_queue(interaction.guild.id)
    if not queue:
        await interaction.followup.send("🎵 Fila de músicas vazia.", ephemeral=True)
        return

    url, song_name = queue.pop(0)  # Pega a primeira música da fila
    self.last_song[interaction.guild.id] = song_name  # Armazena a última música
    vc = interaction.guild.voice_client

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
            vc.play(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS),
                    after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.loop))
            await interaction.followup.send(f"🎵 Tocando agora: **{song_name}**")

            # Se o loop da fila estiver ativado, readiciona a música ao final da fila
            if interaction.guild.id in bot.queue_loop_states and bot.queue_loop_states[interaction.guild.id]:
                queue.append((url, song_name))
        except Exception as e:
            await interaction.followup.send(f"Erro ao tocar a música: {e}", ephemeral=True)
            await self.play_next(interaction)  # Toca a próxima música em caso de erro

@bot.tree.command(name="shuffle", description="Embaralha a fila de músicas")
async def shuffle(interaction: discord.Interaction):
    queue = bot.get_queue(interaction.guild.id)
    if not queue:
        await interaction.response.send_message("🎵 A fila de músicas está vazia.", ephemeral=True)
        return

    random.shuffle(queue)  # Embaralha a fila
    await interaction.response.send_message("🎵 Fila de músicas embaralhada.")

@bot.tree.command(name="nowplaying", description="Mostra a música que está tocando no momento")
async def nowplaying(interaction: discord.Interaction):
    guild_id = interaction.guild.id

    # Verifica se há uma música tocando no momento
    if guild_id not in bot.current_song or not bot.current_song[guild_id]:
        await interaction.response.send_message("Nenhuma música está tocando no momento.", ephemeral=True)
        return

    # Obtém a música atual que está tocando
    current_song = bot.current_song[guild_id]
    await interaction.response.send_message(f"🎵 Tocando agora: **{current_song}**")

@bot.tree.command(name="seek", description="Pula para um ponto específico da música (em segundos)")
async def seek(interaction: discord.Interaction, seconds: int):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_playing():
        await interaction.response.send_message("Não estou tocando música no momento.", ephemeral=True)
        return

    # Verifica se a música suporta seek (depende da biblioteca de áudio)
    if not hasattr(vc.source, 'seek'):
        await interaction.response.send_message("Essa música não suporta seek.", ephemeral=True)
        return

    # Pula para o ponto especificado
    vc.source.seek(seconds)
    await interaction.response.send_message(f"⏩ Pulando para {seconds} segundos.")

async def auto_disconnect(self, guild_id):
    await asyncio.sleep(300) 
    vc = self.get_guild(guild_id).voice_client
    if vc and not vc.is_playing() and not self.get_queue(guild_id):
        await vc.disconnect()

@bot.tree.command(name="playlist", description="Adiciona uma playlist do YouTube à fila")
async def playlist(interaction: discord.Interaction, url: str):
    await interaction.response.defer()  

    voice_state = interaction.user.voice
    if not voice_state:
        await interaction.followup.send("Você precisa estar em um canal de voz para tocar música!", ephemeral=True)
        return

    channel = voice_state.channel
    vc = interaction.guild.voice_client

    if not vc or not vc.is_connected():
        vc = await channel.connect()

    # Configurações do yt-dlp para playlists
    YDL_PLAYLIST_OPTIONS = {
        'format': 'bestaudio/best',
        'extract_flat': 'in_playlist', 
        'quiet': True,  
    }

    with yt_dlp.YoutubeDL(YDL_PLAYLIST_OPTIONS) as ydl:
        try:
            # Extrai informações da playlist
            info = ydl.extract_info(url, download=False)
            if not info or 'entries' not in info:
                await interaction.followup.send("Não consegui encontrar a playlist. Certifique-se de que o link é válido.", ephemeral=True)
                return

            # Adiciona cada música da playlist à fila
            queue = bot.get_queue(interaction.guild.id)
            for entry in info['entries']:
                if entry:  # Verifica se a entrada é válida
                    queue.append((entry['url'], entry['title']))

            # Envia uma mensagem confirmando a adição da playlist
            await interaction.followup.send(
                f"🎵 Playlist adicionada à fila: **{info['title']}** ({len(info['entries'])} músicas)."
            )

            # Se não estiver tocando nada, começa a tocar
            if not vc.is_playing():
                await bot.play_next(interaction)
        except Exception as e:
            await interaction.followup.send(f"Erro ao processar a playlist: {e}", ephemeral=True)

@bot.tree.command(name="queueloop", description="Ativa ou desativa o loop da fila inteira")
async def queueloop(interaction: discord.Interaction):
    guild_id = interaction.guild.id

    # Inicializa o estado de loop da fila para o servidor
    if guild_id not in bot.queue_loop_states:
        bot.queue_loop_states[guild_id] = False

    # Alterna o estado de loop da fila
    bot.queue_loop_states[guild_id] = not bot.queue_loop_states[guild_id]
    state = "ativado" if bot.queue_loop_states[guild_id] else "desativado"

    await interaction.response.send_message(f"🔁 Loop da fila {state}.")

@bot.tree.command(name="remove", description="Remove uma música da fila")
async def remove(interaction: discord.Interaction, position: int):
    queue = bot.get_queue(interaction.guild.id)
    if not queue:
        await interaction.response.send_message("🎵 A fila de músicas está vazia.", ephemeral=True)
        return

    if position < 1 or position > len(queue):
        await interaction.response.send_message("Posição inválida.", ephemeral=True)
        return

    # Remove a música da fila
    removed_song = queue.pop(position - 1)
    await interaction.response.send_message(f"🗑️ Música removida: **{removed_song[1]}**.")

@bot.tree.command(name="move", description="Move uma música para outra posição na fila")
async def move(interaction: discord.Interaction, from_position: int, to_position: int):
    queue = bot.get_queue(interaction.guild.id)
    if not queue:
        await interaction.response.send_message("🎵 A fila de músicas está vazia.", ephemeral=True)
        return

    if from_position < 1 or from_position > len(queue) or to_position < 1 or to_position > len(queue):
        await interaction.response.send_message("Posição inválida.", ephemeral=True)
        return

    # Move a música para a nova posição
    moved_song = queue.pop(from_position - 1)
    queue.insert(to_position - 1, moved_song)
    await interaction.response.send_message(f"🎵 Música movida: **{moved_song[1]}** para a posição {to_position}.")


bot.run('**********')