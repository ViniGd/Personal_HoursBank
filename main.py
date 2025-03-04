import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os

# Caminho para a pasta "storage" no mesmo diretório que o main.py
storage_dir = os.path.join(os.path.dirname(__file__), 'storage')

# Criar a pasta "storage" se ela não existir
if not os.path.exists(storage_dir):
    os.makedirs(storage_dir)

# Caminho completo para o arquivo do banco de dados dentro da pasta "storage"
db_file = os.path.join(storage_dir, 'meu_banco_de_dados.db')

# Função para criar a tabela se não existir
def criar_tabela():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Data TEXT NOT NULL,  -- Alterado para TEXT para armazenar a data no formato DD/MM/YYYY
            Horas FLOAT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Função para converter horas decimais para o formato HH:MM
def decimal_para_horas_minutos(horas_decimais):
    horas = int(horas_decimais)
    minutos = int((horas_decimais - horas) * 60)
    return f"{horas:02d}:{minutos:02d}"

# Função para converter o formato HH:MM para horas decimais
def horas_minutos_para_decimal(horas_minutos):
    horas, minutos = map(int, horas_minutos.split(':'))
    return horas + minutos / 60

# Função para formatar a data no padrão DD/MM/YYYY
def formatar_data(data):
    return datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')

# Função para inserir dados na tabela
def inserir_dados(data, horas):
    data_formatada = formatar_data(data)  # Formata a data para DD/MM/YYYY
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO registros (Data, Horas) VALUES (?, ?)', (data_formatada, horas))
    conn.commit()
    conn.close()
    atualizar_interface()

# Função para atualizar dados na tabela
def atualizar_dados(id, data, horas):
    data_formatada = formatar_data(data)  # Formata a data para DD/MM/YYYY
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('UPDATE registros SET Data = ?, Horas = ? WHERE id = ?', (data_formatada, horas, id))
    conn.commit()
    conn.close()
    atualizar_interface()

# Função para verificar se já existe um registro no dia de hoje
def existe_registro_hoje():
    hoje = datetime.now().strftime('%d/%m/%Y')  # Formata a data atual para DD/MM/YYYY
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM registros WHERE Data = ?', (hoje,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

# Função para parar o timer e salvar os dados
def parar_timer():
    if existe_registro_hoje():
        messagebox.showwarning("Aviso", "Já existe um registro no dia de hoje!")
        return

    tempo_decorrido = timer_label['text']
    horas, minutos, segundos = map(int, tempo_decorrido.split(':'))
    horas_totais = horas + minutos / 60 + segundos / 3600  # Converte para horas decimais

    # Se o tempo for menor que 9 horas, gera um valor negativo
    if horas_totais < 9:
        horas_totais = horas_totais - 9  # Gera um valor negativo

    data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    inserir_dados(data, horas_totais)
    messagebox.showinfo("Sucesso", f"Dados salvos: {formatar_data(data)}, Horas: {decimal_para_horas_minutos(horas_totais)}")
    timer_label['text'] = "00:00:00"
    running[0] = False

# Função para inserção manual de horas
def insercao_manual():
    if existe_registro_hoje():
        messagebox.showwarning("Aviso", "Já existe um registro para hoje!")
        return
    horas_minutos = simpledialog.askstring("Inserção Manual", "Digite a quantidade de horas no formato HH:MM:")
    if horas_minutos:
        try:
            horas_decimais = horas_minutos_para_decimal(horas_minutos)
            data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            inserir_dados(data, horas_decimais)
            messagebox.showinfo("Sucesso", f"Dados salvos: {formatar_data(data)}, Horas: {horas_minutos}")
        except ValueError:
            messagebox.showerror("Erro", "Formato inválido! Use o formato HH:MM.")

# Função para editar um registro
def editar_registro():
    selecionado = tabela.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Nenhum registro selecionado!")
        return

    # Obtém os dados do registro selecionado
    item = tabela.item(selecionado)
    id_registro = item['values'][0]
    data_registro = item['values'][1]
    horas_registro = item['values'][2]

    # Janela de edição
    janela_edicao = tk.Toplevel(root)
    janela_edicao.title("Editar Registro")

    # Campos de edição
    tk.Label(janela_edicao, text="Data (DD/MM/YYYY):").grid(row=0, column=0, padx=10, pady=10)
    entry_data = tk.Entry(janela_edicao)
    entry_data.insert(0, data_registro)
    entry_data.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(janela_edicao, text="Horas (HH:MM):").grid(row=1, column=0, padx=10, pady=10)
    entry_horas = tk.Entry(janela_edicao)
    entry_horas.insert(0, horas_registro)
    entry_horas.grid(row=1, column=1, padx=10, pady=10)

    # Função para salvar as alterações
    def salvar_edicao():
        nova_data = entry_data.get()
        novas_horas = entry_horas.get()

        try:
            # Verifica se a data está no formato correto
            datetime.strptime(nova_data, '%d/%m/%Y')
            horas_decimais = horas_minutos_para_decimal(novas_horas)
            atualizar_dados(id_registro, nova_data + " 00:00:00", horas_decimais)  # Adiciona um horário fictício
            messagebox.showinfo("Sucesso", "Registro atualizado com sucesso!")
            janela_edicao.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Formato inválido! Use o formato DD/MM/YYYY para a data e HH:MM para as horas.")

    # Botão para salvar
    tk.Button(janela_edicao, text="Salvar", command=salvar_edicao).grid(row=2, column=0, columnspan=2, pady=10)

# Função para atualizar a interface gráfica
def atualizar_interface():
    if 'tabela' in globals():
        atualizar_dados_tabela()

# Função para atualizar os dados na tabela
def atualizar_dados_tabela():
    if 'tabela' not in globals():
        return

    # Limpa a tabela
    for row in tabela.get_children():
        tabela.delete(row)

    # Busca os registros no banco de dados
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM registros')
    registros = cursor.fetchall()
    conn.close()

    # Insere os dados na tabela
    for registro in registros:
        horas_formatadas = decimal_para_horas_minutos(registro[2])
        tabela.insert("", tk.END, values=(registro[0], registro[1], horas_formatadas))

    # Calcula a soma das horas
    soma_horas = sum(registro[2] for registro in registros)
    soma_horas_formatada = decimal_para_horas_minutos(soma_horas)
    label_soma_horas.config(text=f"Soma das Horas: {soma_horas_formatada}")

# Função para visualizar os dados da base
def visualizar_dados():
    # Cria uma nova janela para exibir os dados
    janela_dados = tk.Toplevel(root)
    janela_dados.title("Dados da Base")
    janela_dados.geometry("600x400")

    # Frame para a tabela
    frame_tabela = ttk.Frame(janela_dados)
    frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Treeview para exibir os dados
    global tabela
    colunas = ("ID", "Data", "Horas")
    tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
    tabela.heading("ID", text="ID")
    tabela.heading("Data", text="Data")
    tabela.heading("Horas", text="Horas (HH:MM)")
    tabela.pack(fill=tk.BOTH, expand=True)

    # Barra de rolagem
    scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tabela.yview)
    tabela.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Botão para inserir horas negativas
    def inserir_horas_negativas():
        horas_minutos = simpledialog.askstring("Inserir Horas Negativas", "Digite a quantidade de horas no formato HH:MM:")
        if horas_minutos:
            try:
                horas_decimais = horas_minutos_para_decimal(horas_minutos)
                data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                inserir_dados(data, horas_decimais * -1)
                messagebox.showinfo("Sucesso", f"Dados salvos: {formatar_data(data)}, Horas: -{horas_minutos}")
            except ValueError:
                messagebox.showerror("Erro", "Formato inválido! Use o formato HH:MM.")

    # Frame para os botões
    frame_botoes = ttk.Frame(janela_dados)
    frame_botoes.pack(fill=tk.X, padx=10, pady=10)

    # Botões
    ttk.Button(frame_botoes, text="Inserir Horas Negativas", command=inserir_horas_negativas).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame_botoes, text="Editar Registro", command=editar_registro).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame_botoes, text="Refresh", command=atualizar_dados_tabela).pack(side=tk.LEFT, padx=5)

    # Label para a soma das horas
    global label_soma_horas
    label_soma_horas = ttk.Label(janela_dados, text="Soma das Horas: 00:00", font=("Arial", 12))
    label_soma_horas.pack(pady=10)

    # Carrega os dados pela primeira vez
    atualizar_dados_tabela()

# Função para atualizar o timer
def atualizar_timer():
    if running[0]:
        tempo_atual = timer_label['text']
        horas, minutos, segundos = map(int, tempo_atual.split(':'))
        segundos += 1
        if segundos == 60:
            segundos = 0
            minutos += 1
        if minutos == 60:
            minutos = 0
            horas += 1
        timer_label['text'] = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    root.after(1000, atualizar_timer)

# Cria a interface gráfica
root = tk.Tk()
root.title("Controle de Horas")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# Timer
timer_label = tk.Label(root, text="00:00:00", font=("Arial", 36), bg="#f0f0f0", fg="#333333")
timer_label.pack(pady=20)

# Frame para os botões
frame_botoes = ttk.Frame(root)
frame_botoes.pack(pady=10)

# Botões
ttk.Button(frame_botoes, text="Parar", command=parar_timer).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_botoes, text="Inserção Manual", command=insercao_manual).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_botoes, text="Visualizar Dados", command=visualizar_dados).pack(side=tk.LEFT, padx=5)

# Variável para controlar o timer
running = [True]

# Inicia o timer
atualizar_timer()

# Cria a tabela se não existir
criar_tabela()

# Inicia a interface gráfica
root.mainloop()