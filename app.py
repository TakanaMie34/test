from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

DB = 'site.db' # Название базы данных

app = Flask(__name__) # Создаём экземпляр класса
app.secret_key = 'dasfap;sdofaposdvposdfbpoaesrfpgoqawpefasjdvldksvasd' # секретный ключ подключения сессии

# Записи
@app.route('/') # Создаём декоратор функции
def root():
    if 'user' in session: # Если пользователь в сессии
        db = sqlite3.connect(DB) # Подцепляемся к базе данных
        cur = db.cursor() # Имитируем консоль?

        cur.execute('select title, ts, content from messages where author=? order by ts desc', [session['user']]) # Исполянем команду как в базе данных
        
        return render_template('index.html', user=session['user'], messages=cur.fetchall()) # Вызываем шаблон индекс, и посылаем в него имя пользователя и ?? 
    else:
        return redirect(url_for('login'), code=303) # Иначе возращаем пользователя на страницу ввода логина/пароля

# Вход
@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('root'), code=303) # Если пользователь уже в сессии, то возвращает на главную
    else:
        return render_template('login.html') # Иначе приглашает ввести логин/пароль

# Регистрация
@app.route('/register')
def register():
    return render_template('reg.html') # Отобразить регистрацию

@app.route('/new') # Страница с созданием нового поста
def newmsg():
    return render_template('new.html')

@app.route('/do_register', methods=['POST']) # Получение через метод ПОСТ логина, пароля и повторения пароля
def do_register():
    login = request.form['login']
    password = request.form['pass']
    repeat = request.form['repeat']

    if password != repeat: # Если пароль не совпадает
        return redirect(url_for('register'), code=303) # перенаправить на страницу регистрации

    db = sqlite3.connect(DB) # Подключаемся к базе данных
    cur = db.cursor()
    cur.execute('select login from users where login=?', [login]) # Обращаемся к базе данных за логином 
    if not cur.fetchone():
        # Записать новые пароль и логин в базу данных пользователей, если венулось пустое поле
        cur.execute('insert into users values (?, ?)', [login, password]) 
        db.commit() # Записать в базу данных
        return redirect(url_for('login'), code=303) # Если всё хорошо, перенаправить на страницу логина
    else:
        return redirect(url_for('register'), code=303) # Если нет, перенаправить обратно на регистрацию      

@app.route('/do_login', methods = ['POST']) 
def do_login():
    login = request.form['login'] # Получение логина
    password = request.form['pass'] # Получение пароля

    db = sqlite3.connect(DB)
    cur = db.cursor()
    cur.execute('select login from users where login=? and password=?', [login, password]) # Получение логина от определённого логина и пароля
    if not cur.fetchone(): # Если пустое поле, то перенаправить на страницу логина
        return redirect(url_for('login'), code=303)
    else:
        session['user'] = login # Выставить значения пользователя сессии равной логину по которой человек заходил
        return redirect(url_for('root'), code=303)

@app.route('/do_logout', methods = ['POST']) # Сервер получает данные какой пользователь выходит
def do_logout():
    session.pop('user') # Уничтожает имя юзера из сессии и перенаправлет на страницу логина
    return redirect(url_for('login'), code=303)

@app.route('/do_new', methods = ['POST']) # Сервер получает имя поста и контент
def do_new(): 
    title = request.form['title']
    content = request.form['content']

    if 'user' in session: # Если пользователь находится в сессии, то 
        db = sqlite3.connect(DB) 
        cur = db.cursor()
        # Записывает название поста, время, контент и автора в таблицу месседж, всё корме время идёт от автора
        cur.execute('insert into messages (title, ts, content, author) values (?, current_timestamp, ?, ?)', [title, content, session['user']]) 
        db.commit() 

        return redirect(url_for('root'), code=303) # Вернуть на главную, где уже есть новый пост

    else:
        return redirect(url_for('newmsg'), code=303) # Если что-то пошло не так, вернуть обратно писать пост

app.run()

