import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys
from threading import Thread

# --- Funções do Backend (Lógica do Download) ---

class MyLogger(object):
    """
    Um logger personalizado para capturar a saída do yt-dlp e exibir na GUI.
    """
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.is_downloading = False

    def debug(self, msg):
        # Ignorar mensagens de debug muito específicas para não poluir
        if "ETA" in msg or "Downloading" in msg or "fragment" in msg or "progress" in msg:
            self.info(msg) # Trata certas mensagens de debug como info para exibir
        else:
            self._log_message(msg)

    def warning(self, msg):
        self._log_message(f"[AVISO] {msg}")

    def error(self, msg):
        self._log_message(f"[ERRO] {msg}")

    def info(self, msg):
        # Tenta capturar progresso de download e conversão
        if "Downloading" in msg and "ETA" in msg:
            if not self.is_downloading:
                self.is_downloading = True
                self._log_message("Iniciando download...")
            self._log_message(f"Baixando: {msg.split(' ')[1]} de {msg.split(' ')[3]} - ETA: {msg.split('ETA')[1].strip()}")
        elif "Destination" in msg:
            self.is_downloading = False
            self._log_message(f"Download concluído: {msg.replace('[download] Destination: ', '')}")
        elif "[ExtractAudio]" in msg and "Destination" in msg:
             self._log_message("Extração de áudio concluída.")
        elif "[ffmpeg]" in msg and "Destination" in msg:
            self._log_message("Conversão para MP3 concluída.")
        elif "Deleting original file" in msg:
            self._log_message("Limpando arquivos temporários...")
        else:
            self._log_message(msg)
    
    def _log_message(self, msg):
        """Adiciona a mensagem ao widget de texto e rola para o final."""
        # Limita o número de linhas para evitar uso excessivo de memória em downloads longos
        current_lines = int(self.text_widget.index('end-1c linestart').split('.')[0])
        if current_lines > 100: # Manter cerca de 100 linhas visíveis
            self.text_widget.delete('1.0', '2.0') # Deleta a primeira linha
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END) # Rola automaticamente para o final
        self.text_widget.update_idletasks() # Força a atualização da GUI

def baixar_audio_youtube(url_do_video, caminho_saida, text_widget, root_gui):
    """
    Baixa o áudio de um vídeo do YouTube e atualiza a GUI com o progresso.
    """
    if not os.path.isdir(caminho_saida):
        messagebox.showerror("Erro", "O diretório de saída não é válido. Por favor, selecione um diretório existente.")
        # Se o diretório for inválido, o programa deve fechar
        sys.exit() 

    my_logger = MyLogger(text_widget)

    opcoes_ydl = {
        'format': 'bestaudio/best',
        'cookiefile': 'youtubecookies.txt',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{caminho_saida}/%(title)s.%(ext)s',
        'extract_flat': 'True',
        'logger': my_logger,
        'progress_hooks': [lambda d: progress_hook(d, my_logger)],
    }


    try:
        my_logger.info(f"Preparando download para: {url_do_video}")
        my_logger.info(f"O áudio será salvo em: {caminho_saida}")
        
        with yt_dlp.YoutubeDL(opcoes_ydl) as ydl:
            ydl.download([url_do_video])
        
        my_logger.info("Processo concluído com sucesso!")
        messagebox.showinfo("Sucesso", f"Áudio baixado com sucesso em: {caminho_saida}")
        sys.exit() # **Finaliza o script Python completamente após o sucesso**
    except Exception as e:
        my_logger.error(f"Ocorreu um erro fatal durante o download: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro ao baixar o áudio:\n\n{e}")
        sys.exit() # **Finaliza o script Python completamente após o erro**

def progress_hook(d, logger):
    """
    Hook de progresso para yt-dlp.
    A maior parte do log é tratada pelo MyLogger, mas este hook garante que o logger
    receba informações de progresso estruturadas do yt-dlp.
    """
    if d['status'] == 'downloading':
        pass # MyLogger.info já pega isso
    elif d['status'] == 'finished':
        pass # MyLogger.info já pega isso
    elif d['status'] == 'error':
        logger.error(f"Erro no hook de progresso: {d['error']}")


# --- Funções da Interface Gráfica (Tkinter) ---

def abrir_dialogo_salvar():
    """
    Abre uma janela para o usuário selecionar o diretório onde salvar o arquivo MP3.
    Retorna o caminho selecionado ou uma string vazia se cancelado.
    """
    root_dialog = tk.Tk()
    root_dialog.withdraw() 
    
    caminho_selecionado = filedialog.askdirectory(
        title="Selecione o diretório para salvar o áudio MP3"
    )
    
    root_dialog.destroy()
    return caminho_selecionado

def iniciar_download_thread():
    """
    Função chamada quando o botão 'Baixar Áudio' é clicado.
    Inicia o download em uma thread separada para não travar a GUI.
    """
    url = url_entry.get().strip()
    
    if not url or url == "Cole a URL aqui...":
        messagebox.showwarning("Aviso", "Por favor, digite a URL do vídeo do YouTube.")
        return

    caminho_saida = abrir_dialogo_salvar()

    if caminho_saida:
        # Troca os frames visíveis na janela principal
        main_frame.pack_forget() 
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inicia o download em uma nova thread
        # root é passado para que o sys.exit() feche a GUI
        download_thread = Thread(target=baixar_audio_youtube, args=(url, caminho_saida, progress_text, root))
        download_thread.daemon = True 
        download_thread.start()
    else:
        messagebox.showwarning("Aviso", "Nenhum diretório selecionado. Download cancelado.")

# --- Configuração da Interface Gráfica (Tkinter) ---
root = tk.Tk()
root.title("Baixador de Áudio do YouTube")
root.geometry("600x400")
root.resizable(True, True)

# Frame principal para a entrada da URL
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

url_label = tk.Label(main_frame, text="URL do Vídeo do YouTube:")
url_label.pack(pady=5)

url_entry = tk.Entry(main_frame, width=60)
url_entry.pack(pady=5)
url_entry.insert(0, "Cole a URL aqui...") 
url_entry.bind("<FocusIn>", lambda event: url_entry.delete(0, "end") if url_entry.get() == "Cole a URL aqui..." else None)
url_entry.bind("<FocusOut>", lambda event: url_entry.insert(0, "Cole a URL aqui...") if not url_entry.get() else None)

download_button = tk.Button(main_frame, text="Baixar Áudio", command=iniciar_download_thread)
download_button.pack(pady=10)

# Frame para exibir o progresso
progress_frame = tk.Frame(root)

progress_label = tk.Label(progress_frame, text="Status do Download:")
progress_label.pack(pady=5)

progress_text = scrolledtext.ScrolledText(progress_frame, wrap=tk.WORD, width=70, height=15, font=("Consolas", 9))
progress_text.pack(pady=5, fill=tk.BOTH, expand=True)

# Oculta inicialmente o frame de progresso
progress_frame.pack_forget()

root.mainloop() # Inicia o loop principal da interface gráfica