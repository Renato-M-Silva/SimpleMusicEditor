from pydub import AudioSegment
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

def selecionar_arquivo_audio():
    """Abre uma caixa de diálogo para o usuário selecionar um arquivo de áudio."""
    root_dialog = tk.Tk()
    root_dialog.withdraw()
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione um arquivo de áudio",
        filetypes=(("Arquivos de Áudio", "*.mp3 *.wav *.flac *.aac"), ("Todos os arquivos", "*.*"))
    )
    root_dialog.destroy()
    return caminho_arquivo

def selecionar_diretorio_saida():
    """Abre uma caixa de diálogo para o usuário selecionar o diretório de saída."""
    root_dialog = tk.Tk()
    root_dialog.withdraw()
    caminho_diretorio = filedialog.askdirectory(
        title="Selecione o diretório para salvar o áudio combinado"
    )
    root_dialog.destroy()
    return caminho_diretorio

def juntar_trechos_musicas():
    """
    Pega trechos de duas músicas e as une.
    """
    messagebox.showinfo("Passo 1", "Selecione a PRIMEIRA música.")
    caminho_musica1 = selecionar_arquivo_audio()
    if not caminho_musica1:
        messagebox.showwarning("Aviso", "Primeira música não selecionada. Operação cancelada.")
        return

    try:
        inicio1_ms = int(entrada_inicio1.get()) * 1000 # Converter segundos para milissegundos
        fim1_ms = int(entrada_fim1.get()) * 1000
    except ValueError:
        messagebox.showerror("Erro", "Valores de início/fim da Música 1 inválidos. Use números inteiros.")
        return

    messagebox.showinfo("Passo 2", "Selecione a SEGUNDA música.")
    caminho_musica2 = selecionar_arquivo_audio()
    if not caminho_musica2:
        messagebox.showwarning("Aviso", "Segunda música não selecionada. Operação cancelada.")
        return

    try:
        inicio2_ms = int(entrada_inicio2.get()) * 1000 # Converter segundos para milissegundos
        fim2_ms = int(entrada_fim2.get()) * 1000
    except ValueError:
        messagebox.showerror("Erro", "Valores de início/fim da Música 2 inválidos. Use números inteiros.")
        return

    caminho_saida_dir = selecionar_diretorio_saida()
    if not caminho_saida_dir:
        messagebox.showwarning("Aviso", "Diretório de saída não selecionado. Operação cancelada.")
        return

    nome_arquivo_saida = entrada_nome_saida.get()
    if not nome_arquivo_saida:
        messagebox.showwarning("Aviso", "Nome do arquivo de saída não pode estar vazio.")
        return
    
    caminho_completo_saida = os.path.join(caminho_saida_dir, f"{nome_arquivo_saida}.mp3")

    try:
        messagebox.showinfo("Processando", "Carregando músicas e processando trechos. Aguarde...")

        # Carregar as músicas
        musica1 = AudioSegment.from_file(caminho_musica1)
        musica2 = AudioSegment.from_file(caminho_musica2)

        # Extrair os trechos (pydub usa milissegundos)
        trecho1 = musica1[inicio1_ms:fim1_ms]
        trecho2 = musica2[inicio2_ms:fim2_ms]

        # Juntar os trechos
        musica_combinada = trecho1 + trecho2

        # Exportar a música combinada
        musica_combinada.export(caminho_completo_saida, format="mp3")

        messagebox.showinfo("Sucesso", f"Músicas combinadas salvas em:\n{caminho_completo_saida}")
        sys.exit() # Encerra o script após o sucesso

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao processar o áudio: {e}\nVerifique se o FFmpeg está instalado e no PATH.")
        sys.exit() # Encerra o script após o erro

# --- Interface Gráfica (Tkinter) ---
app = tk.Tk()
app.title("Combinador de Trechos de Músicas")

# Frame para Música 1
frame1 = tk.LabelFrame(app, text="Música 1")
frame1.pack(padx=10, pady=5, fill="x")

tk.Label(frame1, text="Início (segundos):").pack(side="left", padx=5)
entrada_inicio1 = tk.Entry(frame1, width=10)
entrada_inicio1.pack(side="left", padx=5)

tk.Label(frame1, text="Fim (segundos):").pack(side="left", padx=5)
entrada_fim1 = tk.Entry(frame1, width=10)
entrada_fim1.pack(side="left", padx=5)

# Frame para Música 2
frame2 = tk.LabelFrame(app, text="Música 2")
frame2.pack(padx=10, pady=5, fill="x")

tk.Label(frame2, text="Início (segundos):").pack(side="left", padx=5)
entrada_inicio2 = tk.Entry(frame2, width=10)
entrada_inicio2.pack(side="left", padx=5)

tk.Label(frame2, text="Fim (segundos):").pack(side="left", padx=5)
entrada_fim2 = tk.Entry(frame2, width=10)
entrada_fim2.pack(side="left", padx=5)

# Nome do arquivo de saída
frame_saida = tk.LabelFrame(app, text="Arquivo de Saída")
frame_saida.pack(padx=10, pady=5, fill="x")

tk.Label(frame_saida, text="Nome do arquivo final (sem extensão):").pack(side="left", padx=5)
entrada_nome_saida = tk.Entry(frame_saida, width=30)
entrada_nome_saida.pack(side="left", padx=5)

# Botão para combinar
btn_combinar = tk.Button(app, text="Combinar Trechos", command=juntar_trechos_musicas)
btn_combinar.pack(pady=15)

app.mainloop()