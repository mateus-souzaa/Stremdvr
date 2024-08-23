from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client['stream_dvr']
users_collection = db['users']
groups_collection = db['groups']
companies_collection = db['companies']

@app.route("/cadastros", methods=["GET", "POST"])
def cadastros():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        company_id = request.form.get("company_id")
        
        if not email or not senha:
            flash("E-mail e senha são obrigatórios!", "danger")
            return redirect(url_for("cadastros"))
        
        # Verifica se company_id é um ObjectId válido antes de usar
        if company_id:
            try:
                company_id = ObjectId(company_id)
            except Exception as e:
                flash("ID da empresa inválido!", "danger")
                return redirect(url_for("cadastros"))
        
        hashed_senha = generate_password_hash(senha)
        users_collection.insert_one({"email": email, "senha": hashed_senha, "company_id": company_id})
        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("cadastros"))
    
    users = list(users_collection.find())
    for user in users:
        company = companies_collection.find_one({"_id": user.get("company_id")})
        user["company_name"] = company["name"] if company else "Não Associado"
    
    return render_template("cadastros.html", users=users)

@app.route("/grupo/novo", methods=["GET", "POST"])
def novo_grupo():
    if request.method == "POST":
        nome_grupo = request.form.get("nome_grupo")
        if not nome_grupo:
            flash("Nome do grupo é obrigatório!", "danger")
            return redirect(url_for("novo_grupo"))
        
        groups_collection.insert_one({"nome_grupo": nome_grupo})
        flash("Grupo criado com sucesso!", "success")
        return redirect(url_for("cadastros"))
    
    return render_template("novo_grupo.html")

@app.route("/empresa/novo", methods=["GET", "POST"])
def nova_empresa():
    if request.method == "POST":
        nome_empresa = request.form.get("nome_empresa")
        if not nome_empresa:
            flash("Nome da empresa é obrigatório!", "danger")
            return redirect(url_for("nova_empresa"))
        
        companies_collection.insert_one({"name": nome_empresa})
        flash("Empresa criada com sucesso!", "success")
        return redirect(url_for("cadastros"))
    
    return render_template("nova_empresa.html")

@app.route("/usuario/editar/<user_id>", methods=["GET", "POST"])
def editar_usuario(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        flash("Usuário não encontrado!", "danger")
        return redirect(url_for("cadastros"))
    
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        company_id = request.form.get("company_id")
        
        update_fields = {}
        
        if email:
            update_fields["email"] = email
        if senha:
            hashed_senha = generate_password_hash(senha)
            update_fields["senha"] = hashed_senha
        if company_id:
            try:
                update_fields["company_id"] = ObjectId(company_id)
            except Exception as e:
                flash("ID da empresa inválido!", "danger")
                return redirect(url_for("editar_usuario", user_id=user_id))
        
        if update_fields:
            users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
            flash("Usuário atualizado com sucesso!", "success")
            return redirect(url_for("cadastros"))
    
    companies = list(companies_collection.find())
    return render_template("editar_usuario.html", user=user, companies=companies)

@app.route("/usuario/deletar/<user_id>")
def deletar_usuario(user_id):
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        flash("Usuário não encontrado!", "danger")
    else:
        flash("Usuário deletado com sucesso!", "success")
    
    return redirect(url_for("cadastros"))

if __name__ == "__main__":
    app.run(debug=True)
