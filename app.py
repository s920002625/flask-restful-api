from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import yaml
from flask import jsonify
from flask import flash, request
from flask_bcrypt import Bcrypt
from flask_bcrypt import check_password_hash
from flask import Flask, jsonify, request
from flask_jwt_extended import (JWTManager, jwt_optional, create_access_token,get_jwt_identity,jwt_required,get_jwt_claims)



app = Flask(__name__)
bcrypt = Bcrypt(app)
# Configure db
db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)
@app.route('/', methods=['GET', 'POST'])
def index():
    result = [{'msg': 'success'}, {'stat': '200 ok'}]
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        name = userDetails['name']
        email = userDetails['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email) VALUES(%s, %s)",(name, email))
        mysql.connection.commit()
        resp=jsonify(userDetails)
        resp.status_code=200
        return jsonify({'result': result})
        cur.close()
        return redirect('/users')

    return render_template('index.html')
    

@app.route('/users', methods=['GET'])
@jwt_optional
def users():
    result = [{'msg': 'success'}, {'stat': '200 ok'}]
    current_user = get_jwt_identity()
    if current_user:
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM users")
        if request.method == 'GET':
            if resultValue > 0:
                userDetails = cur.fetchall()
                resp=jsonify(userDetails)
                resp.status_code=200
                return resp
                return jsonify({'result': result})
                cur.close()
            return jsonify(logged_in_as=current_user), 200
    else:
        return jsonify(logged_in_as='anonymous user'), 200

@app.route('/add', methods=['POST'])
@jwt_optional
def add():
    result = [{'msg': 'success'}, {'stat': '200 ok'}]
    current_user = get_jwt_identity()
    if current_user:
        if request.method == 'POST':
            # Fetch form data
            input_body = request.get_json()
            name = input_body['name']
            email = input_body['email']
            password = input_body['password']
            pw_hash = bcrypt.generate_password_hash(password)
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE name=%s" , [name])
            mysql.connection.commit()
            results = cur.fetchall()
            print (results)
            if results == ():
                print ("empty")
                cur.execute("INSERT INTO users(name, email, password) VALUES(%s, %s, %s)",(name, email,pw_hash))
                mysql.connection.commit()
                resp=jsonify({'result': result})
                resp.status_code=200
                return resp
                return jsonify({'result': result})
                cur2.close()
            else:
                for row in results:
                    name = row[1]
                    name2 = name
                    print (name)
                    print (name2)
                    print (name == name2)
                    return jsonify({"msg": "username exist"}), 400
            if not name:
                return jsonify({"msg": "Missing username parameter"}), 400
            if not email:
                return jsonify({"msg": "Missing email parameter"}), 400
            if not password:
                return jsonify({"msg": "Missing password parameter"}), 400
        return jsonify(logged_in_as=current_user), 200
    else:
        return jsonify(logged_in_as='anonymous user'), 200

@app.route('/delete/<int:id>', methods=['DELETE'])
@jwt_optional
def delete_user(id):
    result = [{'msg': 'User deleted successfully!'}, {'stat': '200 ok'}]
    current_user = get_jwt_identity()
    if current_user:
        if request.method == 'DELETE':
           cur = mysql.connection.cursor()
           cur.execute("DELETE FROM users WHERE users.id = %s", (id,))
           mysql.connection.commit()
           resp = jsonify({'result': result})
           resp.status_code=200
           return resp
           cur.close()
        return jsonify(logged_in_as=current_user), 200
    else:
        return jsonify(logged_in_as='anonymous user'), 200
@app.route('/update', methods=['PUT'])
@jwt_optional
def update_user():
    result = [{'msg': 'All data updated successfully!'}, {'stat': '200 ok'}]
    current_user = get_jwt_identity()
    if current_user:
        if request.method == 'PUT':
            input_body = request.get_json()
            id = input_body['id']
            name = input_body['name']
            email = input_body['email']
            password = input_body['password']
            pw_hash = bcrypt.generate_password_hash(password)
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET name=%s, email=%s, password=%s WHERE users.id=%s", (name,email,pw_hash,id))
            mysql.connection.commit()
            resp = jsonify({'result': result})
            resp.status_code=200
            return resp
            return jsonify({'result': result})
            cur.close()
        return jsonify(logged_in_as=current_user), 200
    else:
        return jsonify(logged_in_as='anonymous user'), 200

@app.route('/patch', methods=['PATCH'])
@jwt_optional
def update_user_data():
    result = [{'msg': 'Data updated successfully!'}, {'stat': '200 ok'}]
    current_user = get_jwt_identity()
    if current_user:
        if request.method == 'PATCH':
            input_body = request.get_json()
            id = input_body['id']
            name = input_body['name']
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET name=%s WHERE users.id=%s", (name,id))
            mysql.connection.commit()
            resp = jsonify({'result': result})
            resp.status_code=200
            return resp
            #return jsonify({'result': result})
            cur.close()
        return jsonify(logged_in_as=current_user), 200
    else:
        return jsonify(logged_in_as='anonymous user'), 200

        
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp
@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return {
        'hello': identity,
        'foo': ['bar', 'baz']
    }
@app.route('/login', methods=['POST'])
def login():
    bcrypt = Bcrypt(app)
    result = [{'msg': 'success'}, {'stat': '200 ok'}]
    if request.method == 'POST':
        name = request.json.get('name', None)
        print (name)
        passworda = request.json.get('password', None)
        print ('password='+str(passworda))
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE name=%s" , [name])
        results = cur.fetchall()
        for row in results:
            password = row[3]
            pw_hash = password
        print ("pw_hash=%s" % (pw_hash))
        ps = bcrypt.check_password_hash(pw_hash, passworda)
        #return print (ps)
        
        if ps != True:
            return jsonify({"msg": "error password"}), 401
        if not name:
           return jsonify({"msg": "Missing username parameter"}), 400
        if not password:
           return jsonify({"msg": "Missing password parameter"}), 400
        resp=jsonify(results)
        cur.close()
    access_token = create_access_token(identity=name),{'result': result}
    return jsonify(access_token=access_token)


@app.route('/partially-protected', methods=['GET'])
@jwt_optional
def partially_protected():
    # If no JWT is sent in with the request, get_jwt_identity()
    # will return None
    current_user = get_jwt_identity()
    if current_user:
        return jsonify(logged_in_as=current_user), 200
    else:
        return jsonify(logged_in_as='anonymous user'), 200
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    claims = get_jwt_claims()
    return jsonify({
        'hello_is': claims['hello'],
        'foo_is': claims['foo']
    }), 200


if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=5000, ssl_context='adhoc')
    app.run(host='0.0.0.0',port=5000)
    
