from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Rota principal (index)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar os arquivos enviados
@app.route('/processar', methods=['POST'])
def processar():
    if 'files[]' not in request.files:
        return 'Nenhum arquivo enviado.'

    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return 'Nenhum arquivo selecionado.'

    lista_planilhas = []

    for file in files:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        extensao = file.filename.split('.')[-1].lower()

        try:
            if extensao == 'xls':
                planilha = pd.read_excel(filepath, engine='xlrd')
            elif extensao == 'xlsx':
                planilha = pd.read_excel(filepath, engine='openpyxl')
            else:
                print(f"Arquivo {file.filename} ignorado (extensão não suportada).")
                continue
        except Exception as e:
            print(f"Erro ao ler o arquivo {file.filename}: {e}")
            continue

        if 'Loja Destino' not in planilha.columns or 'Produto' not in planilha.columns or 'Quantidade' not in planilha.columns:
            print(f"Arquivo {file.filename} não possui as colunas necessárias. Ignorando.")
            continue

        planilha_amaralina = planilha[planilha['Loja Destino'].str.contains('amaralina', case=False, na=False)]

        if planilha_amaralina.empty:
            print(f"Arquivo {file.filename} não possui registros para Amaralina. Ignorando.")
            continue

        planilha_amaralina['numero_produto'] = planilha_amaralina['Produto'].astype(str)
        planilha_amaralina['ponto_e_virgula'] = ';'
        planilha_amaralina['quantidade_numero'] = planilha_amaralina['Quantidade'].astype(str)

        planilha_b = planilha_amaralina[['numero_produto', 'ponto_e_virgula', 'quantidade_numero']]
        lista_planilhas.append(planilha_b)

    if not lista_planilhas:
        return 'Nenhum dado válido encontrado nos arquivos enviados.'

    resultado_final = pd.concat(lista_planilhas, ignore_index=True)
    resultado_txt = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_unificado.txt')
    resultado_final.to_csv(resultado_txt, index=False, header=False, sep='\t')

    return send_file(resultado_txt, as_attachment=True)

# ✅ Adicione aqui a rota para sua página extra
    @app.route('/crossdockingpituba')
    def pagina2():
        return render_template('CrossdockingPituba.html')

    if __name__ == '__main__':
        app.run(debug=True)
