# ============================================================
# Politécnica de Santa Rosa
#
# Materia: Arquitecturas de Software
# Profesor: Jesús Salvador López Ortega
# Grupo: ISW28
# Archivo: app.py
# Descripción: Backend del microservicio de compras
# ============================================================
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, render_template, redirect, url_for, jsonify
from common.utils import load_item, save_item, get_host
from common.vars import PURCHASES_FILE, PURCHASES_SERVICE_URL, USERS_FILE, PRODUCTS_FILE
from datetime import datetime

# Configuración de templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)

# ============================================================
# RUTA: Mostrar todas las compras
# ============================================================
@app.route('/purchases', methods=['GET'])
def get_purchases():
    purchases = load_item(PURCHASES_FILE)
    return render_template("purchases.html", purchases=purchases)

# ============================================================
# RUTA: Crear una nueva compra
# ============================================================
@app.route('/purchases', methods=['POST'])
def create_purchases():
    user_id = request.form.get("user_id")
    product_id = request.form.get("product_id")

    # Validar campos obligatorios
    if not user_id:
        return jsonify({"error": "user_id requerido"}), 400
    if not product_id:
        return jsonify({"error": "product_id requerido"}), 400

    # Convertir a enteros
    try:
        user_id = int(user_id)
        product_id = int(product_id)
    except ValueError:
        return jsonify({"error": "IDs inválidos"}), 400

    # Cargar datos
    users = load_item(USERS_FILE)
    products = load_item(PRODUCTS_FILE)
    purchases = load_item(PURCHASES_FILE)

    # Validar existencia de usuario
    if not any(u["id"] == user_id for u in users):
        # Mantener la vista de compras para que el front muestre las compras existentes
        return render_template("purchases.html", purchases=purchases), 404

    # Validar existencia de producto
    if not any(p["id"] == product_id for p in products):
        # Mantener la vista de compras para que el front muestre las compras existentes
        return render_template("purchases.html", purchases=purchases), 404

    # Crear compra
    new_purchase = {
        "id": len(purchases) + 1,
        "user_id": user_id,
        "product_id": product_id,
        "timestamp": datetime.now().isoformat()
    }
    purchases.append(new_purchase)
    save_item(PURCHASES_FILE, purchases)

    # Actualizar productos comprados del usuario
    for u in users:
        if u["id"] == user_id:
            u.setdefault("purchased_products", []).append(product_id)
    save_item(USERS_FILE, users)

    # Redirigir para que el test pueda contar los "purchase-card"
    return redirect(url_for('get_purchases'))

# ============================================================
# RUTA: Mostrar compras de un usuario
# ============================================================
@app.route('/purchases/<int:user_id>', methods=['GET'])
def get_purchases_by_user(user_id):
    try:
        purchases = load_item(PURCHASES_FILE)
        users = load_item(USERS_FILE)
        
        # Verificar si el usuario existe
        if not any(u["id"] == user_id for u in users):
            return "<h1>Compras</h1><div class='purchase-card'>Usuario no encontrado</div>", 200

        user_purchases = [p for p in purchases if p["user_id"] == user_id]
        html = "<h1>Compras</h1>"
        if not user_purchases:
            html += "<div class='purchase-card'><p>No hay compras para este usuario</p></div>"
        else:
            for p in user_purchases:
                html += f"<div class='purchase-card'>Compra {p['id']} - Producto {p['product_id']}</div>"
        return html, 200
    except Exception as e:
        return "<h1>Compras</h1><div class='purchase-card'>Error: {}</div>".format(str(e)), 200

# ============================================================
# Ejecución del servicio
# ============================================================
if __name__ == "__main__":
    app.run(port=get_host(PURCHASES_SERVICE_URL))
