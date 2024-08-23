from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import urllib.parse



app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client['stream_dvr']
clientes_collection = db['clientes']
empresas_collection = db['empresas']
nvrs_collection = db['nvrs']

# index
@app.route("/")
def index():
    return render_template("index.html")



# Rota para o cadastro de um novo NVR
@app.route("/cadastros/nvr/novo", methods=["GET", "POST"])
def nvr_novo():
    if request.method == "POST":
        nome_nvr = request.form.get("nome_nvr")
        username = request.form.get("username")
        password = request.form.get("password")
        ip = request.form.get("ip")
        port = request.form.get("port")
        empresa_id = request.form.get("empresa")

        # Codificação da senha para URL
        password_encoded = urllib.parse.quote_plus(password)

        # Gerando a URL RTSP
        rtsp_url = f'rtsp://{username}:{password_encoded}@{ip}:{port}'

        # Salvamento no banco de dados MongoDB
        nvrs_collection.insert_one({
            "nome_nvr": nome_nvr,
            "username": username,
            "password": password,  # Armazena a senha original (cuidado com segurança)
            "ip": ip,
            "port": port,
            "rtsp_url": rtsp_url,
            "empresa_id": ObjectId(empresa_id)  # Referência à empresa
        })

        flash(f"NVR {nome_nvr} cadastrado com sucesso!", "success")
        return redirect(url_for("listar_nvrs"))

    # Buscar empresas do banco de dados
    empresas = empresas_collection.find()
    return render_template("nvr_novo.html", empresas=empresas)


# Rota para listar NVRs
@app.route("/cadastros/nvr/listar")
def listar_nvrs():
    nvrs = nvrs_collection.aggregate([
        {
            "$lookup": {
                "from": "empresas",  # Coleção de empresas
                "localField": "empresa_id",  # Campo na coleção de NVRs que referencia a empresa
                "foreignField": "_id",  # Campo na coleção de empresas
                "as": "empresa"
            }
        },
        {
            "$unwind": "$empresa"  # Garante que os dados da empresa sejam tratados como um objeto e não como uma lista
        },
        {
            "$project": {
                "nome_nvr": 1,  # Campo para exibir o nome do NVR
                "rtsp_url": 1,  # Campo para exibir a URL RTSP
                "username": 1,
                "ip": 1,
                "port": 1,
                "empresa_nome": "$empresa.nome"  # Nome da empresa
            }
        }
    ])
    return render_template("listar_nvrs.html", nvrs=nvrs)


# Rota para editar um NVR
@app.route("/cadastros/nvr/editar/<nvr_id>", methods=["GET", "POST"])
def editar_nvr(nvr_id):
    nvr = nvrs_collection.find_one({"_id": ObjectId(nvr_id)})
    if request.method == "POST":
        nome_nvr = request.form.get("nome_nvr")
        username = request.form.get("username")
        password = request.form.get("password")
        ip = request.form.get("ip")
        port = request.form.get("port")
        empresa_id = request.form.get("empresa")

        # Codificação da senha para URL
        password_encoded = urllib.parse.quote_plus(password)

        # Gerando a URL RTSP atualizada
        rtsp_url = f'rtsp://{username}:{password_encoded}@{ip}:{port}'

        # Atualização no banco de dados MongoDB
        nvrs_collection.update_one({"_id": ObjectId(nvr_id)}, {
            "$set": {
                "nome_nvr": nome_nvr,
                "username": username,
                "password": password,
                "ip": ip,
                "port": port,
                "rtsp_url": rtsp_url,
                "empresa_id": ObjectId(empresa_id)
            }
        })
        flash(f"NVR {nome_nvr} atualizado com sucesso!", "success")
        return redirect(url_for("listar_nvrs"))

    # Buscar empresas do banco de dados
    empresas = empresas_collection.find()
    return render_template("editar_nvr.html", nvr=nvr, empresas=empresas)


# Rota para excluir um NVR
@app.route("/cadastros/nvr/deletar/<nvr_id>")
def deletar_nvr(nvr_id):
    nvrs_collection.delete_one({"_id": ObjectId(nvr_id)})
    flash("NVR deletado com sucesso!", "success")
    return redirect(url_for("listar_nvrs"))





# Rota para listar clientes com nome da empresa
@app.route("/cadastros/cliente/listar")
def listar_clientes():
    clientes = clientes_collection.aggregate([
        {
            "$lookup": {
                "from": "empresas",
                "localField": "empresa_id",
                "foreignField": "_id",
                "as": "empresa"
            }
        },
        {
            "$unwind": "$empresa"
        },
        {
            "$project": {
                "nome": 1,
                "email": 1,
                "empresa_nome": "$empresa.nome"
            }
        }
    ])
    return render_template("listar_clientes.html", clientes=clientes)


# Rota para listar empresas
@app.route("/cadastros/empresa/listar")
def listar_empresas():
    empresas = empresas_collection.find()
    return render_template("listar_empresas.html", empresas=empresas)

# Rota para o cadastro de um novo cliente
@app.route("/cadastros/cliente/novo", methods=["GET", "POST"])
def cliente_novo():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        empresa_id = request.form.get("empresa")

        # Salvamento no banco de dados MongoDB
        clientes_collection.insert_one({
            "nome": nome,
            "email": email,
            "senha": senha,
            "empresa_id": ObjectId(empresa_id)  # Referência à empresa
        })
        flash(f"Cliente {nome} cadastrado com sucesso!", "success")
        return redirect(url_for("listar_clientes"))

    # Buscar empresas do banco de dados
    empresas = empresas_collection.find()
    return render_template("cliente_novo.html", empresas=empresas)

# Rota para o cadastro de uma nova empresa
@app.route("/cadastros/empresa/novo", methods=["GET", "POST"])
def empresa_novo():
    if request.method == "POST":
        nome = request.form.get("nome")
        cnpj = request.form.get("cnpj")
        endereco = request.form.get("endereco")

        # Salvamento no banco de dados MongoDB
        empresas_collection.insert_one({"nome": nome, "cnpj": cnpj, "endereco": endereco})
        flash(f"Empresa {nome} cadastrada com sucesso!", "success")
        return redirect(url_for("listar_empresas"))

    return render_template("empresa_novo.html")

# Rota para editar um cliente
# Rota para editar um cliente
@app.route("/cadastros/cliente/editar/<cliente_id>", methods=["GET", "POST"])
def editar_cliente(cliente_id):
    cliente = clientes_collection.find_one({"_id": ObjectId(cliente_id)})
    if not cliente:
        flash("Cliente não encontrado!", "danger")
        return redirect(url_for("listar_clientes"))

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        empresa_id = request.form.get("empresa_id")

        # Atualização no banco de dados MongoDB
        clientes_collection.update_one({"_id": ObjectId(cliente_id)}, {
            "$set": {
                "nome": nome,
                "email": email,
                "senha": senha,
                "empresa_id": ObjectId(empresa_id)
            }
        })
        flash(f"Cliente {nome} atualizado com sucesso!", "success")
        return redirect(url_for("listar_clientes"))

    empresas = empresas_collection.find()
    return render_template("editar_cliente.html", cliente=cliente, empresas=empresas)

# Rota para excluir um cliente
@app.route("/cadastros/cliente/deletar/<cliente_id>")
def deletar_cliente(cliente_id):
    clientes_collection.delete_one({"_id": ObjectId(cliente_id)})
    flash("Cliente deletado com sucesso!", "success")
    return redirect(url_for("listar_clientes"))

# Rota para editar uma empresa
@app.route("/cadastros/empresa/editar/<empresa_id>", methods=["GET", "POST"])
def editar_empresa(empresa_id):
    empresa = empresas_collection.find_one({"_id": ObjectId(empresa_id)})
    if request.method == "POST":
        nome = request.form.get("nome")
        cnpj = request.form.get("cnpj")
        endereco = request.form.get("endereco")

        # Atualização no banco de dados MongoDB
        empresas_collection.update_one({"_id": ObjectId(empresa_id)}, {
            "$set": {
                "nome": nome,
                "cnpj": cnpj,
                "endereco": endereco
            }
        })
        flash(f"Empresa {nome} atualizada com sucesso!", "success")
        return redirect(url_for("listar_empresas"))

    return render_template("editar_empresa.html", empresa=empresa)

# Rota para excluir uma empresa
@app.route("/cadastros/empresa/deletar/<empresa_id>")
def deletar_empresa(empresa_id):
    empresas_collection.delete_one({"_id": ObjectId(empresa_id)})
    flash("Empresa deletada com sucesso!", "success")
    return redirect(url_for("listar_empresas"))



# Executa o servidor Flask
if __name__ == "__main__":
    app.run(debug=True)
