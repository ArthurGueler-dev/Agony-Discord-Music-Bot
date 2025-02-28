# Agony-Discord-Music-Bot

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub last commit](https://img.shields.io/github/last-commit/ArthurGueler-dev/Agony-Discord-Music-Bot)
![GitHub repo size](https://img.shields.io/github/repo-size/ArthurGueler-dev/Agony-Discord-Music-Bot)

Um bot de música para Discord que toca músicas do YouTube, Spotify e muito mais.

## Funcionalidades
- Tocar músicas do YouTube e Spotify.
- Gerenciar filas de músicas.
- Buscar letras de músicas.
- Controle de loop e shuffle.
- Ver historico de músicas
- Função de pular segundos da música

## Como usar
1. Clone este repositório.
2. Instale as dependências: `pip install -r requirements.txt`.
3. Configure as variáveis de ambiente no arquivo `.env`.
4. Execute o bot: `agony.py`.

## Requisitos
- Python 3.8 ou superior.
- Bibliotecas: `discord.py`, `yt-dlp`, `lyricsgenius`, `spotipy`.

## Comandos do bot

Aqui está a lista completa de comandos disponíveis no bot e como usá-los:

### 🎵 Comandos de música

- **`/play <query>`**  
  Toca uma música do YouTube, Spotify ou busca pelo nome.  
  Exemplo: `/play Bohemian Rhapsody` ou `/play https://www.youtube.com/watch?v=...`.

- **`/playlist <url>`**  
  Adiciona uma playlist do YouTube à fila.  
  Exemplo: `/playlist https://www.youtube.com/playlist?list=...`.

- **`/pause`**  
  Pausa a música que está tocando no momento.

- **`/resume`**  
  Retoma a música que foi pausada.

- **`/skip`**  
  Pula a música atual e toca a próxima da fila.

- **`/stop`**  
  Para a música e desconecta o bot do canal de voz.

- **`/nowplaying`**  
  Mostra a música que está tocando no momento.

- **`/queue`**  
  Mostra a fila de músicas atual.

- **`/shuffle`**  
  Embaralha a fila de músicas.

- **`/loop`**  
  Ativa ou desativa o loop da música atual.

- **`/queueloop`**  
  Ativa ou desativa o loop da fila inteira.

- **`/seek <segundos>`**  
  Pula para um ponto específico da música (em segundos).  
  Exemplo: `/seek 120` (pula para 2 minutos).

- **`/remove <posição>`**  
  Remove uma música da fila.  
  Exemplo: `/remove 3` (remove a terceira música da fila).

- **`/move <de> <para>`**  
  Move uma música para outra posição na fila.  
  Exemplo: `/move 2 5` (move a segunda música para a quinta posição).

- **`/clear`**  
  Limpa a fila de músicas.

---

### 🎲 Comandos de entretenimento

- **`/testar_sorte`**  
  Testa sua sorte com uma roleta de eventos aleatórios.  
  Exemplo: `/testar_sorte`.

---

### 📜 Comandos de letras e histórico

- **`/lyrics <nome da música>`**  
  Mostra a letra da música atual ou de uma música específica.  
  Exemplo: `/lyrics Bohemian Rhapsody`.

- **`/historico`**  
  Mostra o histórico de músicas que você adicionou à fila.

---

## Como usar

1. **Adicione o bot ao seu servidor**:  
   Use o link de convite https://discord.com/oauth2/authorize?client_id=1344148111366422548&permissions=3222528&integration_type=0&scope=bot para adicionar o bot ao seu servidor.

2. **Execute os comandos**:  
   Use os comandos listados acima para controlar o bot.

3. **Divirta-se**:  
   Aproveite a música e as funcionalidades do bot!

---

## Requisitos

- Python 3.8 ou superior.
- Bibliotecas: `discord.py`, `yt-dlp`, `lyricsgenius`, `spotipy`.

---

## Badges

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)  
![License](https://img.shields.io/badge/License-MIT-green)  
![GitHub last commit](https://img.shields.io/github/last-commit/ArthurGueler-dev/Agony-Discord-Bot)  
![GitHub repo size](https://img.shields.io/github/repo-size/ArthurGueler-dev/Agony-Discord-Bot)




