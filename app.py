from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client['stream_dvr']
users_collection = db['users']

# Página de Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        user = users_collection.find_one({"email": email})

        if user and user["senha"] == senha:
            return redirect(url_for("index"))
        else:
            flash("Credenciais inválidas", "danger")

    return render_template("login.html")

# Página Principal
@app.route("/index")
def index():
    return render_template("index.html")

# Página de Cadastros
@app.route("/cadastros", methods=["GET", "POST"])
def cadastros():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        users_collection.insert_one({"email": email, "senha": senha})
        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("cadastros"))
    
    users = users_collection.find()
    return render_template("cadastros.html", users=users)

# Rota para editar um usuário
@app.route("/edit/<user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"email": email, "senha": senha}})
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("cadastros"))
    
    return render_template("edit_user.html", user=user)

# Rota para deletar um usuário
@app.route("/delete/<user_id>")
def delete_user(user_id):
    users_collection.delete_one({"_id": ObjectId(user_id)})
    flash("Usuário deletado com sucesso!", "success")
    return redirect(url_for("cadastros"))

# Página de Visualização de Câmeras
@app.route("/visualizacao")
def visualizacao():
    return render_template("visualizacao.html")

if __name__ == "__main__":
    app.run(debug=True)
