import sqlite3
from datetime import datetime, timedelta
def create_shujuku() :
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    # 启用外键约束（SQLite默认不启用）
    cursor.execute("PRAGMA foreign_keys = ON;")
    # 创建图书表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_name TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT NOT NULL UNIQUE,
        publisher TEXT,
        book_status TEXT NOT NULL DEFAULT '可借阅',
        current_borrower_id INTEGER,
        publish_year INTEGER,
        book_intro TEXT,
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone_number TEXT NOT NULL UNIQUE,
        email TEXT,
        age INTEGER CHECK (age > 0 AND age < 150),
        borrow_quota INTEGER NOT NULL DEFAULT 3,
        borrow_period INTEGER NOT NULL DEFAULT 30,
        current_borrow_count INTEGER DEFAULT 0,
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    # 创建借阅记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS borrow_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL REFERENCES books(book_id),
        user_id INTEGER NOT NULL REFERENCES users(user_id),
        borrow_date DATE NOT NULL,
        due_date DATE NOT NULL,
        return_date DATE,
        renew_count INTEGER DEFAULT 0,
        逾期_status BOOLEAN DEFAULT FALSE,
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
# 图书管理功能
#添加图书
def add_book(name, author, isbn, publisher):# 添加图书的函数
    conn = sqlite3.connect('library.db')# 链接数据库
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO books (book_name, author, isbn, publisher) VALUES (?, ?, ?, ?)",
            (name, author, isbn, publisher)
        )
        conn.commit()
        print("图书添加成功")
    except sqlite3.IntegrityError as e:
        print(f"ISBN已存在: {e}")
    finally:
        conn.close()

def create_book():# 运用add_book函数
    print("添加新书")
    # 校验书名（非空）
    while True:
        name = input("请输入书名: ").strip()
        if not name:
            print("错误：书名不能为空，请重新输入！")
        else:
            break
    # 校验作者（非空）
    while True:
        author = input("请输入作者: ").strip()
        if not author:
            print("错误：作者不能为空，请重新输入！")
        else:
            break
    # 校验ISBN（非空）
    while True:
        isbn = input("请输入ISBN: ").strip()
        if not isbn:
            print("错误：ISBN不能为空，请重新输入！")
        else:
            break
    publisher = input("请输入出版社（可选）: ").strip()
    add_book(name, author, isbn, publisher)

# 搜索图书
def search_book(keyword: str) -> None:
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE book_name LIKE? OR isbn LIKE? OR author LIKE?",
                   ('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'))
    books = cursor.fetchall()
    if not books:
        print("未找到匹配的图书")
    else:
        print("找到以下图书：")
        for book in books:
            print(f"ID: {book[0]}, 书名: {book[1]}, 作者: {book[2]}, ISBN: {book[3]}, 出版社: {book[4]}")
    conn.close()

def seek_book():
    book = input("请输入书籍信息: ")
    search_book(book)

# 更新图书信息
def update_book(book_id=None, isbn=None, **kwargs):
    if not book_id and not isbn:
        print("错误: 必须提供book_id或ISBN以指定要更新的图书")
        return False
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 构建SQL更新语句
        set_clauses = []
        params = []
        # 收集要更新的字段
        valid_fields = ['book_name', 'author', 'isbn', 'publisher']
        for field, value in kwargs.items():
            if field in valid_fields:
                set_clauses.append(f"{field} = ?")
                params.append(value)
            else:
                print(f"警告: 忽略未知字段 '{field}'")
        if not set_clauses:
            print("错误: 未指定要更新的有效字段")
            return False
        # 添加WHERE条件
        if book_id:
            where_clause = "book_id = ?"
            params.append(book_id)
        else:
            where_clause = "isbn = ?"
            params.append(isbn)

        sql = f"UPDATE books SET {', '.join(set_clauses)} WHERE {where_clause}"
        # 执行更新
        cursor.execute(sql, params)
        conn.commit()
        if cursor.rowcount == 0:
            print("未找到匹配的图书，更新失败")
            return False

        print("图书信息更新成功")
        return True
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def gengxin_book():
    print("更新图书信息")
    # 选择查找方式
    while True:
        search_type = input("请选择查找方式 (1. 图书ID / 2. ISBN): ")
        if search_type == "1":
            tushuxinxi = input("请输入图书ID: ")
            search_field = "book_id"
            break
        elif search_type == "2":
            tushuxinxi = input("请输入图书ISBN: ")
            search_field = "isbn"
            break
        else:
            print("无效选择，请重新输入")
    # 连接数据库查找图书
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 查询图书信息
        cursor.execute(f"SELECT * FROM books WHERE {search_field} = ?", (tushuxinxi,))
        book = cursor.fetchone()
        if not book:
            print("未找到匹配的图书")
            return False
        # 显示当前图书信息
        print("当前图书信息:")
        print(f"ID: {book[0]}")
        print(f"书名: {book[1]}")
        print(f"作者: {book[2]}")
        print(f"ISBN: {book[3]}")
        print(f"出版社: {book[4]}")
        # 收集要更新的字段
        update_fields = {}
        new_name = input("请输入新书名 (留空保持不变): ")
        if new_name:
            update_fields["book_name"] = new_name
        new_author = input("请输入新作者 (留空保持不变): ")
        if new_author:
            update_fields["author"] = new_author
        new_isbn = input("请输入新ISBN (留空保持不变): ")
        if new_isbn:
            update_fields["isbn"] = new_isbn
        new_publisher = input("请输入新出版社 (留空保持不变): ")
        if new_publisher:
            update_fields["publisher"] = new_publisher
        if not update_fields:
            print("未进行任何修改")
            return False
        # 执行更新
        if search_field == "book_id":
            update_book(book_id=int(tushuxinxi), **update_fields)
        else:
            update_book(isbn=tushuxinxi, **update_fields)
        return True
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return False
    finally:
        conn.close()

# 删除图书
def delete_book(field, value):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    # 验证字段名是否合法
    valid_fields = ['book_id', 'book_name', 'isbn']
    if field not in valid_fields:
        print(f"错误：不支持的字段 '{field}'")
        return
    try:
        # 构建SQL语句
        sql = f"DELETE FROM books WHERE {field} = ?"
        # 执行删除
        cursor.execute(sql, (value,))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"未找到{field}为 '{value}' 的图书")
        else:
            print(f"成功删除{cursor.rowcount}本图书")
    except sqlite3.Error as e:
        print(f"删除失败: {e}")
    finally:
        conn.close()

def shanchu_book():
    print("删除书籍")
    while True:
        search_type = input("请选择删除方式 (1. 图书ID / 2. 图书name / 3. 图书ISBN): ")
        if search_type == "1":
            tushuxinxi = input("请输入图书ID: ")
            delete_field = "book_id"
            break
        elif search_type == "2":
            tushuxinxi = input("请输入图书name: ")
            delete_field = "book_name"
            break
        elif search_type == "3":
            tushuxinxi = input("请输入图书ISBN: ")
            delete_field = "isbn"
            break
        else:
            print("无效选择，请重新输入")
    confirm = input(f"确认要删除{delete_field}为{tushuxinxi} 的图书吗？(y/n): ").lower()
    if confirm == 'y':
        delete_book(delete_field, tushuxinxi)
    else:
        print("操作已取消")

# 显示图书列表
def display_books():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 查询所有图书
        cursor.execute("SELECT * FROM books ORDER BY book_id ASC")
        books = cursor.fetchall()
        if not books:
            print("图书馆中暂无图书记录")
            return
        # 打印表头
        print("\n=== 图书馆所有图书 ===")
        print(f"{'ID':<5} | {'书名':<30} | {'作者':<20} | {'ISBN':<15} | {'出版社':<20}")
        print("-" * 90)
        # 打印每本图书信息
        for book in books:
            book_id, name, author, isbn, publisher = book[:5]
            print(f"{book_id:<5} | {name[:30]:<30} | {author[:20]:<20} | {isbn:<15} | {publisher[:20]:<20}")
        print(f"\n共 {len(books)} 本图书")
    except sqlite3.Error as e:
        print(f"查询失败: {e}")
    finally:
        conn.close()

# 图书借阅状态管理
def manage_borrow_status():
    """图书借阅状态管理主菜单"""
    while True:
        print("\n=== 图书借阅状态管理 ===")
        print("1. 查询图书借阅状态")
        print("2. 查询用户借阅记录")
        print("3. 显示所有借阅记录")
        print("4. 返回上级菜单")
        choice = input("请选择操作 (1-4): ").strip()
        if choice == "1":
            check_book_status()
        elif choice == "2":
            check_user_borrow_records()
        elif choice == "3":
            display_all_borrow_records()
        elif choice == "4":
            break
        else:
            print("无效选择，请重新输入")

def check_book_status():
    print("\n查询图书借阅状态")
    # 获取图书ID
    while True:
        book_id = input("请输入要查询的图书ID (输入0返回): ").strip()
        if book_id == "0":
            return
        if not book_id.isdigit():
            print("错误：图书ID必须是数字")
            continue
        break
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 查询图书信息
        cursor.execute(
            """SELECT b.book_id, b.book_name, b.book_status, b.current_borrower_id, 
                      u.name AS borrower_name, br.borrow_date, br.due_date, br.return_date 
               FROM books b 
               LEFT JOIN borrow_records br ON b.book_id = br.book_id AND br.return_date IS NULL 
               LEFT JOIN users u ON b.current_borrower_id = u.user_id 
               WHERE b.book_id = ?""",
            (book_id,)
        )
        book = cursor.fetchone()
        if not book:
            print(f"错误：图书ID {book_id} 不存在")
            return
        book_id, book_name, book_status, borrower_id, borrower_name, borrow_date, due_date, return_date = book
        print(f"\n图书《{book_name}》 (ID:{book_id}) 的借阅状态：")
        print(f"状态：{book_status}")
        if book_status == "已借出":
            print(f"借阅人：{borrower_name} (ID:{borrower_id})")
            print(f"借阅日期：{borrow_date}")
            print(f"应还日期：{due_date}")
            # 检查是否逾期
            today = datetime.now().strftime("%Y-%m-%d")
            if today > due_date and not return_date:
                days_overdue = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(due_date, "%Y-%m-%d")).days
                print(f"已逾期 {days_overdue} 天")
            else:
                days_left = (datetime.strptime(due_date, "%Y-%m-%d") - datetime.strptime(today, "%Y-%m-%d")).days
                print(f"剩余天数：{days_left} 天")
        else:
            print("当前可借阅")
    except sqlite3.Error as e:
        print(f"查询失败: {e}")
    finally:
        conn.close()

def check_user_borrow_records():
    print("\n查询用户借阅记录")
    # 获取用户ID
    while True:
        user_id = input("请输入要查询的用户ID (输入0返回): ").strip()
        if user_id == "0":
            return
        if not user_id.isdigit():
            print("错误：用户ID必须是数字")
            continue
        break
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 查询用户信息
        cursor.execute("SELECT name, borrow_quota, current_borrow_count FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            print(f"错误：用户ID {user_id} 不存在")
            return
        user_name, borrow_quota, current_borrow_count = user
        # 查询借阅记录
        cursor.execute(
            """SELECT b.book_name, br.borrow_date, br.due_date, br.return_date, br.逾期_status 
               FROM borrow_records br 
               JOIN books b ON br.book_id = b.book_id 
               WHERE br.user_id = ? 
               ORDER BY br.borrow_date DESC""",
            (user_id,))
        records = cursor.fetchall()
        if not records:
            print(f"用户 {user_name} (ID:{user_id}) 没有借阅记录")
            return
        print(f"\n用户 {user_name} (ID:{user_id}) 的借阅记录：")
        print(f"当前可借阅数量：{borrow_quota - current_borrow_count}/{borrow_quota}")
        print(f"{'序号':<5} | {'书名':<30} | {'借阅日期':<12} | {'应还日期':<12} | {'归还日期':<12} | {'状态'}")
        print("-" * 85)
        for i, (book_name, borrow_date, due_date, return_date, is_overdue) in enumerate(records, 1):
            status = "已归还" if return_date else "未归还"
            if not return_date and is_overdue:
                status = "逾期未还"
            print(
                f"{i:<5} | {book_name[:30]:<30} | {borrow_date:<12} | {due_date:<12} | {return_date or '未归还':<12} | {status}")
    except sqlite3.Error as e:
        print(f"查询失败: {e}")
    finally:
        conn.close()

def display_all_borrow_records():
    print("\n所有借阅记录")
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 查询所有借阅记录
        cursor.execute(
            """SELECT br.record_id, b.book_name, u.name, br.borrow_date, br.due_date, br.return_date, br.逾期_status 
               FROM borrow_records br 
               JOIN books b ON br.book_id = b.book_id 
               JOIN users u ON br.user_id = u.user_id 
               ORDER BY br.borrow_date DESC""")
        records = cursor.fetchall()
        if not records:
            print("暂无借阅记录")
            return
        print(
            f"{'序号':<5} | {'记录ID':<8} | {'书名':<30} | {'借阅人':<15} | {'借阅日期':<12} | {'应还日期':<12} | {'归还日期':<12} | {'状态'}")
        print("-" * 110)
        for i, (record_id, book_name, user_name, borrow_date, due_date, return_date, is_overdue) in enumerate(records,                                                                                                  1):
            status = "已归还" if return_date else "未归还"
            if not return_date and is_overdue:
                status = "逾期未还"
            print(
                f"{i:<5} | {record_id:<8} | {book_name[:30]:<30} | {user_name[:15]:<15} | {borrow_date:<12} | {due_date:<12} | {return_date or '未归还':<12} | {status}")
    except sqlite3.Error as e:
        print(f"查询失败: {e}")
    finally:
        conn.close()

def book_management_menu():
    while True:
        print("\n图书管理系统")
        print("1. 添加图书")
        print("2. 搜索图书")
        print("3. 更新图书信息")
        print("4. 删除图书")
        print("5. 显示所有图书")
        print("6. 图书借阅状态管理")
        print("7. 返回上级菜单")
        choice = input("请选择操作 (1-7): ")
        if choice == "1":
            create_book()
        elif choice == "2":
            seek_book()
        elif choice == "3":
            gengxin_book()
        elif choice == "4":
            shanchu_book()
        elif choice == "5":
            display_books()
        elif choice == "6":
            manage_borrow_status()
        elif choice == "7":
            break
        else:
            print("无效的选择，请重新输入。")

# 借阅管理功能
# 借阅图书
def borrow_book():
    print("借阅图书")
    while True:
        print("请选择查询方式：")
        print("1. 通过图书ID查询")
        print("2. 通过书名查询")
        print("3. 通过作者查询")
        print("4. 通过ISBN查询")
        print("0. 返回上级菜单")
        search_type = input("请选择 (0-4): ").strip()
        if search_type == "0":
            return
        if search_type not in ["1", "2", "3", "4"]:
            print("无效选择，请重新输入")
            continue
        break
    # 获取查询关键词
    query_keyword = input("请输入查询关键词: ").strip()
    if not query_keyword:
        print("错误：查询关键词不能为空")
        return
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 根据查询方式构建SQL查询
        if search_type == "1":  # 通过ID查询
            if not query_keyword.isdigit(): # 验证ID是否为数字
                print("错误：图书ID必须是数字")
                return
            cursor.execute("SELECT book_id, book_name, author, isbn, book_status FROM books WHERE book_id = ?",
                           (query_keyword,))
        elif search_type == "2":  # 通过书名查询
            cursor.execute("SELECT book_id, book_name, author, isbn, book_status FROM books WHERE book_name LIKE ?",
                           ('%' + query_keyword + '%',))
        elif search_type == "3":  # 通过作者查询
            cursor.execute("SELECT book_id, book_name, author, isbn, book_status FROM books WHERE author LIKE ?",
                           ('%' + query_keyword + '%',))
        else:  # 通过ISBN查询
            cursor.execute("SELECT book_id, book_name, author, isbn, book_status FROM books WHERE isbn LIKE ?",
                           ('%' + query_keyword + '%',))
        # 获取查询结果
        books = cursor.fetchall()
        if not books:
            print(
                f"未找到匹配的图书（查询方式：{'ID' if search_type == '1' else '书名' if search_type == '2' else '作者' if search_type == '3' else 'ISBN'}，关键词：{query_keyword}）")
            return
        # 显示查询结果
        print(f"\n找到 {len(books)} 本匹配的图书：")
        print(f"{'序号':<5} | {'图书ID':<8} | {'书名':<30} | {'作者':<20} | {'ISBN':<15} | {'状态'}")
        print("-" * 90)
        for i, (book_id, book_name, author, isbn, status) in enumerate(books, 1):
            print(f"{i:<5} | {book_id:<8} | {book_name[:30]:<30} | {author[:20]:<20} | {isbn[:15]:<15} | {status}")
        # 选择要借阅的图书
        while True:
            selection = input("\n请选择要借阅的图书序号 (输入0返回): ").strip()
            if selection == "0":
                return
            if not selection.isdigit() or int(selection) < 1 or int(selection) > len(books):
                print(f"无效选择，请输入1-{len(books)}之间的数字")
                continue
            break
        selected_book = books[int(selection) - 1]
        book_id, book_name, _, _, book_status = selected_book
        if book_status != "可借阅": # 检查图书是否可借阅
            print(f"错误：图书《{book_name}》当前状态为 '{book_status}'，不可借阅")
            return
        while True: # 获取用户ID
            user_id = input("请输入借阅用户ID (输入0返回): ").strip()
            if user_id == "0":
                return
            if not user_id.isdigit():
                print("错误：用户ID必须是数字")
                continue
            break
        borrow_date = input("请输入借阅日期 (YYYY-MM-DD，留空默认为今天): ").strip()# 获取借阅日期（默认为今天）
        if not borrow_date:
            borrow_date = datetime.now().strftime("%Y-%m-%d")
        else:# 验证日期格式
            try:
                datetime.strptime(borrow_date, "%Y-%m-%d")
            except ValueError:
                print("错误：日期格式不正确，应为YYYY-MM-DD")
                return
        cursor.execute("SELECT user_id, name, borrow_quota, current_borrow_count FROM users WHERE user_id = ?",
                       (user_id,))# 检查用户是否存在
        user = cursor.fetchone()
        if not user:
            print(f"错误：用户ID {user_id} 不存在")
            return
        user_id, user_name, borrow_quota, current_borrow_count = user
        # 检查用户借阅配额
        if current_borrow_count >= borrow_quota:
            print(f"错误：用户 {user_name} (ID:{user_id}) 已达到最大借阅数量 ({borrow_quota}本)")
            return
        # 获取用户的借阅期限
        cursor.execute("SELECT borrow_period FROM users WHERE user_id = ?", (user_id,))
        borrow_period = cursor.fetchone()[0]
        # 计算应还日期
        due_date = (datetime.strptime(borrow_date, "%Y-%m-%d") + timedelta(days=borrow_period)).strftime("%Y-%m-%d")
        # 开始事务
        conn.execute("BEGIN")
        try:
            # 插入借阅记录
            cursor.execute(
                """INSERT INTO borrow_records (book_id, user_id, borrow_date, due_date)
                   VALUES (?, ?, ?, ?)""",
                (book_id, user_id, borrow_date, due_date))
            # 更新图书状态
            cursor.execute(
                "UPDATE books SET book_status = '已借出', current_borrower_id = ? WHERE book_id = ?",
                (user_id, book_id))
            # 更新用户借阅数量
            cursor.execute(
                "UPDATE users SET current_borrow_count = current_borrow_count + 1 WHERE user_id = ?",
                (user_id,))
            conn.commit()
            print(f"借阅成功：用户 {user_name} (ID:{user_id}) 已借阅《{book_name}》")
            print(f"借阅日期：{borrow_date}")
            print(f"应还日期：{due_date}")
        except sqlite3.Error as e:
            conn.rollback()
            print(f"数据库操作失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()

# 归还图书
def return_book():
    # 获取用户ID
    while True:
        user_id = input("请输入借阅用户ID (输入0返回): ").strip()
        if user_id == "0":
            return
        if not user_id.isdigit():
            print("错误：用户ID必须是数字")
            continue
        break
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 检查用户是否存在
        cursor.execute("SELECT user_id, name FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"错误：用户ID {user_id} 不存在")
            return
        user_id, user_name = user
        # 查询用户未归还的图书
        cursor.execute("""
            SELECT b.book_id, b.book_name, b.author, b.isbn, 
                   br.borrow_date, br.due_date, br.record_id
            FROM borrow_records br
            JOIN books b ON br.book_id = b.book_id
            WHERE br.user_id = ? AND br.return_date IS NULL
            ORDER BY br.due_date ASC
        """, (user_id,))
        books = cursor.fetchall()
        if not books:
            print(f"用户 {user_name} (ID:{user_id}) 没有未归还的图书")
            return
        # 显示待归还图书
        print(f"\n用户 {user_name} (ID:{user_id}) 待归还的图书：")
        print(
            f"{'序号':<5} | {'图书ID':<8} | {'书名':<30} | {'作者':<20} | {'ISBN':<15} | {'借阅日期':<12} | {'应还日期':<12} | {'状态'}")
        print("-" * 110)
        today = datetime.now().strftime("%Y-%m-%d")
        for i, (book_id, book_name, author, isbn, borrow_date, due_date, record_id) in enumerate(books, 1):
            status = "正常"
            if due_date < today:
                days_overdue = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(due_date, "%Y-%m-%d")).days
                status = f"逾期 {days_overdue} 天"
            print(
                f"{i:<5} | {book_id:<8} | {book_name[:30]:<30} | {author[:20]:<20} | {isbn[:15]:<15} | {borrow_date:<12} | {due_date:<12} | {status}")
        # 选择要归还的图书
        while True:
            selection = input("\n请选择要归还的图书序号 (输入0返回): ").strip()
            if selection == "0":
                return
            if not selection.isdigit() or int(selection) < 1 or int(selection) > len(books):
                print(f"无效选择，请输入1-{len(books)}之间的数字")
                continue
            break
        selected_book = books[int(selection) - 1]
        book_id, book_name, _, _, _, due_date, record_id = selected_book
        # 获取归还日期（默认为今天）
        return_date = input("请输入归还日期 (YYYY-MM-DD，留空默认为今天): ").strip()
        if not return_date:
            return_date = today
        else:
            # 验证日期格式
            try:
                datetime.strptime(return_date, "%Y-%m-%d")
            except ValueError:
                print("错误：日期格式不正确，应为YYYY-MM-DD")
                return
        # 开始事务
        conn.execute("BEGIN")
        try:
            # 更新借阅记录
            cursor.execute(
                """UPDATE borrow_records 
                   SET return_date = ?, 
                       逾期_status = ? 
                   WHERE record_id = ?""",
                (return_date, return_date > due_date, record_id)
            )
            # 更新图书状态
            cursor.execute(
                "UPDATE books SET book_status = '可借阅', current_borrower_id = NULL WHERE book_id = ?",
                (book_id,)
            )
            # 更新用户借阅数量
            cursor.execute(
                "UPDATE users SET current_borrow_count = current_borrow_count - 1 WHERE user_id = ?",
                (user_id,)
            )
            # 提交事务
            conn.commit()
            print(f"归还成功：图书《{book_name}》已归还")
            print(f"借阅用户：{user_name} (ID:{user_id})")
            print(f"借阅日期：{borrow_date}")
            print(f"应还日期：{due_date}")
            print(f"实际归还日期：{return_date}")
            if return_date > due_date:
                days_overdue = (
                            datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(due_date, "%Y-%m-%d")).days
                print(f"警告：该书已逾期 {days_overdue} 天")
        except sqlite3.Error as e:
            # 回滚事务
            conn.rollback()
            print(f"数据库操作失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()
# 续借图书
def renew_book():
    print("\n=== 续借图书 ===")
    # 获取用户ID
    while True:
        user_id = input("请输入借阅用户ID (输入0返回): ").strip()
        if user_id == "0":
            return
        if not user_id.isdigit():
            print("错误：用户ID必须是数字")
            continue
        break
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 检查用户是否存在
        cursor.execute("SELECT user_id, name FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"错误：用户ID {user_id} 不存在")
            return
        user_id, user_name = user
        # 查询用户可续借的图书（未归还且未逾期）
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT b.book_id, b.book_name, b.author, b.isbn, 
                   br.borrow_date, br.due_date, br.record_id, br.renew_count
            FROM borrow_records br
            JOIN books b ON br.book_id = b.book_id
            WHERE br.user_id = ? 
              AND br.return_date IS NULL 
              AND br.due_date >= ?
            ORDER BY br.due_date ASC
        """, (user_id, today))
        books = cursor.fetchall()
        if not books:
            print(f"用户 {user_name} (ID:{user_id}) 没有可续借的图书")
            return
        # 获取用户的续借权限
        cursor.execute(
            "SELECT borrow_period, MAX(renew_count) FROM users u JOIN borrow_records br ON u.user_id = br.user_id WHERE u.user_id = ? AND br.return_date IS NULL GROUP BY u.user_id",
            (user_id,))
        user_borrow_period = cursor.fetchone()
        if user_borrow_period:
            borrow_period, max_renew_count = user_borrow_period
        else:
            # 如果用户没有借阅记录，使用默认借阅期限
            cursor.execute("SELECT borrow_period FROM users WHERE user_id = ?", (user_id,))
            borrow_period = cursor.fetchone()[0]
            max_renew_count = 0
        # 显示可续借图书
        print(f"\n用户 {user_name} (ID:{user_id}) 可续借的图书：")
        print(
            f"{'序号':<5} | {'图书ID':<8} | {'书名':<30} | {'作者':<20} | {'ISBN':<15} | {'借阅日期':<12} | {'应还日期':<12} | {'已续借次数'}")
        print("-" * 110)
        for i, (book_id, book_name, author, isbn, borrow_date, due_date, record_id, renew_count) in enumerate(books, 1):
            print(
                f"{i:<5} | {book_id:<8} | {book_name[:30]:<30} | {author[:20]:<20} | {isbn[:15]:<15} | {borrow_date:<12} | {due_date:<12} | {renew_count} 次")

        print(f"\n续借规则：每次续借可延长 {borrow_period} 天，最多可续借 {max_renew_count} 次")
        # 选择要续借的图书
        while True:
            selection = input("\n请选择要续借的图书序号 (输入0返回): ").strip()
            if selection == "0":
                return
            if not selection.isdigit() or int(selection) < 1 or int(selection) > len(books):
                print(f"无效选择，请输入1-{len(books)}之间的数字")
                continue
            break
        selected_book = books[int(selection) - 1]
        book_id, book_name, _, _, _, due_date, record_id, renew_count = selected_book
        # 检查是否达到最大续借次数
        if renew_count >= max_renew_count:
            print(f"错误：图书《{book_name}》已达到最大续借次数 ({max_renew_count}次)")
            return
        # 计算新的应还日期
        new_due_date = (datetime.strptime(due_date, "%Y-%m-%d") + timedelta(days=borrow_period)).strftime("%Y-%m-%d")
        # 确认续借
        print(f"\n确认续借《{book_name}》:")
        print(f"当前应还日期: {due_date}")
        print(f"续借后应还日期: {new_due_date}")
        confirm = input("是否确认续借？(y/n): ").strip().lower()
        if confirm != "y":
            print("已取消续借")
            return
        # 开始事务
        conn.execute("BEGIN")
        try:
            # 更新借阅记录
            cursor.execute(
                """UPDATE borrow_records 
                   SET due_date = ?, 
                       renew_count = renew_count + 1 
                   WHERE record_id = ?""",
                (new_due_date, record_id)
            )
            # 提交事务
            conn.commit()
            print(f"续借成功：图书《{book_name}》的应还日期已延长至 {new_due_date}")
            print(f"本次为第 {renew_count + 1} 次续借，最多可续借 {max_renew_count} 次")
        except sqlite3.Error as e:
            # 回滚事务
            conn.rollback()
            print(f"数据库操作失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()

# 逾期处理
def Late_process():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 查询所有逾期图书
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT 
                b.book_id, 
                b.book_name, 
                u.user_id, 
                u.name, 
                u.phone_number,
                br.borrow_date,
                br.due_date,
                (julianday(?) - julianday(br.due_date)) AS days_overdue
            FROM borrow_records br
            JOIN books b ON br.book_id = b.book_id
            JOIN users u ON br.user_id = u.user_id
            WHERE br.return_date IS NULL 
              AND br.due_date < ?
            ORDER BY days_overdue DESC
        """, (today, today))
        overdue_books = cursor.fetchall()
        if not overdue_books:
            print("当前没有逾期未还的图书")
            return
        # 显示逾期图书统计
        total_overdue = len(overdue_books)
        total_days = sum([int(row[7]) for row in overdue_books])
        avg_days = total_days / total_overdue
        print(f"\n共发现 {total_overdue} 本逾期图书，累计逾期 {total_days} 天，平均逾期 {avg_days:.1f} 天")
        print(
            f"{'序号':<5} | {'图书ID':<8} | {'书名':<30} | {'用户ID':<8} | {'用户名':<15} | {'电话':<15} | {'逾期天数'}")
        print("-" * 100)
        for i, (book_id, book_name, user_id, user_name, phone, borrow_date, due_date, days_overdue) in enumerate(
                overdue_books, 1):
            print(
                f"{i:<5} | {book_id:<8} | {book_name[:30]:<30} | {user_id:<8} | {user_name[:15]:<15} | {phone[:15]:<15} | {int(days_overdue)} 天")
        # 逾期处理菜单
        while True:
            print("\n请选择操作：")
            print("1. 发送逾期提醒")
            print("2. 按用户统计逾期")
            print("3. 查看逾期详情")
            print("4. 返回")
            choice = input("请选择 (1-4): ").strip()
            if choice == "1":# 发送逾期提醒
                send_overdue_notifications(overdue_books)
            elif choice == "2":# 按用户统计逾期
                total_by_user(overdue_books)
            elif choice == "3":# 查看逾期详情
                view_overdue_details(overdue_books)
            elif choice == "4":
                break
            else:
                print("无效选择，请重新输入")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()
def send_overdue_notifications(overdue_books):
    # 按用户分组逾期图书
    user_books = {}
    for book in overdue_books:
        user_id, user_name, phone = book[2], book[3], book[4]
        if user_id not in user_books:
            user_books[user_id] = {
                'name': user_name,
                'phone': phone,
                'books': []}
        user_books[user_id]['books'].append(book)
    # 发送提醒
    total_notifications = 0
    for user_id, data in user_books.items():
        user_name = data['name']
        phone = data['phone']
        books = data['books']
        # 构建提醒消息
        message = f"尊敬的 {user_name} (ID:{user_id})，您有 {len(books)} 本图书已逾期：\n"
        for book in books:
            book_name = book[1]
            days_overdue = int(book[7])
            message += f"- 《{book_name}》逾期 {days_overdue} 天\n"
        message += "请尽快归还，以免影响您的借阅权限。"
        # 模拟发送消息
        print(f"\n已向 {user_name} (电话: {phone}) 发送逾期提醒：")
        print(message)
        total_notifications += 1
    print(f"\n共发送 {total_notifications} 条逾期提醒")
def total_by_user(overdue_books):
    # 按用户分组并统计
    user_stats = {}
    for book in overdue_books:
        user_id, user_name, days_overdue = book[2], book[3], int(book[7])
        if user_id not in user_stats:
            user_stats[user_id] = {
                'name': user_name,
                'book_count': 0,
                'total_days': 0,
                'max_days': 0 }
        user_stats[user_id]['book_count'] += 1
        user_stats[user_id]['total_days'] += days_overdue
        user_stats[user_id]['max_days'] = max(user_stats[user_id]['max_days'], days_overdue)
    sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['total_days'], reverse=True)
    print(f"{'序号':<5} | {'用户ID':<8} | {'用户名':<15} | {'逾期图书数':<8} | {'累计逾期天数':<8} | {'最长逾期'}")
    print("-" * 70)
    for i, (user_id, stats) in enumerate(sorted_users, 1):
        print(
            f"{i:<5} | {user_id:<8} | {stats['name'][:15]:<15} | {stats['book_count']:<8} | {stats['total_days']:<8} | {stats['max_days']} 天")
def view_overdue_details(overdue_books):
    while True:
        book_index = input("请输入要查看的图书序号 (0返回): ").strip()
        if book_index == "0":
            break
        if not book_index.isdigit() or int(book_index) < 1 or int(book_index) > len(overdue_books):
            print(f"无效序号，请输入1-{len(overdue_books)}之间的数字")
            continue
        book = overdue_books[int(book_index) - 1]
        book_id, book_name, user_id, user_name, phone, borrow_date, due_date, days_overdue = book
        print(f"\n图书《{book_name}》 (ID:{book_id}) 逾期详情：")
        print(f"借阅用户：{user_name} (ID:{user_id})")
        print(f"联系电话：{phone}")
        print(f"借阅日期：{borrow_date}")
        print(f"应还日期：{due_date}")
        print(f"逾期天数：{int(days_overdue)} 天")
        # 计算可能的罚款（示例）
        fine_per_day = 0.5  # 假设每天罚款0.5元
        total_fine = int(days_overdue) * fine_per_day
        print(f"预计罚款：{total_fine:.2f} 元 (假设每天罚款 {fine_per_day} 元)")

# 借阅历史记录
def borrow_history():
    while True:
        user_id = input("请输入要查询的用户ID (输入0返回): ").strip()
        if user_id == "0":
            return
        if not user_id.isdigit():
            print("错误：用户ID必须是数字")
            continue
        break
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 检查用户是否存在
        cursor.execute("SELECT user_id, name FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"错误：用户ID {user_id} 不存在")
            return
        user_id, user_name = user
        # 查询用户借阅记录
        cursor.execute("""
            SELECT 
                b.book_id, 
                b.book_name,
                br.borrow_date,
                br.due_date,
                br.return_date,
                br.renew_count,
                br.逾期_status
            FROM borrow_records br
            JOIN books b ON br.book_id = b.book_id
            WHERE br.user_id = ?
            ORDER BY br.borrow_date DESC
        """, (user_id,))
        records = cursor.fetchall()
        if not records:
            print(f"用户 {user_name} (ID:{user_id}) 没有借阅记录")
            return
        # 显示借阅记录
        print(f"\n用户 {user_name} (ID:{user_id}) 的借阅历史记录：")
        print(
            f"{'序号':<5} | {'图书ID':<8} | {'书名':<30} | {'借阅日期':<12} | {'应还日期':<12} | {'归还日期':<12} | {'续借次数'} | {'状态'}")
        print("-" * 120)
        for i, (book_id, book_name, borrow_date, due_date, return_date, renew_count, is_overdue) in enumerate(
                records, 1):
            status = "已归还" if return_date else "未归还"
            if status == "已归还" and is_overdue:
                status = "已归还（逾期）"
            return_date = return_date if return_date else "未归还"
            print(
                f"{i:<5} | {book_id:<8} | {book_name[:30]:<30} | {borrow_date:<12} | {due_date:<12} | {return_date:<12} | {renew_count:^9} | {status}")
        # 统计信息
        total_records = len(records)
        returned_count = sum(1 for r in records if r[4])
        overdue_count = sum(1 for r in records if r[4] and r[6])
        current_borrow_count = total_records - returned_count
        print(f"\n统计信息：")
        print(f"• 总借阅次数：{total_records}")
        print(f"• 已归还图书：{returned_count} ({overdue_count} 本逾期)")
        print(f"• 当前借阅中：{current_borrow_count}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()

def borrow_management_menu():
    while True:
        print("\n借阅管理")
        print("1. 借阅图书")
        print("2. 归还图书")
        print("3. 续借图书")
        print("4. 逾期处理")
        print("5. 借阅历史记录")
        print("6. 返回上级菜单")
        choice = input("请选择操作 (1-6): ").strip()
        if choice == "1":
            borrow_book()
        elif choice == "2":
            return_book()
        elif choice == "3":
            renew_book()
        elif choice == "4":
            if verify_admin_password():
                Late_process()
            else:
                print("密码错误，返回上级菜单")
        elif choice == "5":
            borrow_history()
        elif choice == "6":
            break
        else:
            print("无效选择，请重新输入")
# 读者管理功能
# 添加用户
def add_user():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        while True:
            # 获取用户信息
            name = input("请输入用户姓名 (输入0返回): ").strip()
            if name == "0":
                return
            phone = input("请输入联系电话: ").strip()
            email = input("请输入电子邮箱: ").strip()
            # 验证邮箱（简单验证）
            if email and "@" not in email:
                print("警告：邮箱格式可能不正确")
            # 显示用户信息预览
            print("\n用户信息预览：")
            print(f"姓名: {name}")
            print(f"电话: {phone}")
            print(f"邮箱: {email}")
            # 确认添加
            confirm = input("\n是否确认添加此用户？(y/n): ").strip().lower()
            if confirm == "y":
                # 生成新用户ID（取当前最大ID加1）
                cursor.execute("SELECT MAX(user_id) FROM users")
                max_id = cursor.fetchone()[0]
                new_id = (max_id or 0) + 1
                # 插入新用户（默认借阅权限）
                cursor.execute(
                    """INSERT INTO users (user_id, name, phone_number, email, 
                                          borrow_period, max_borrow_count, max_renew_count, 
                                          current_borrow_count, registration_date)
                       VALUES (?, ?, ?, ?, 30, 5, 1, 0, ?)""",
                    (new_id, name, phone, email, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                print(f"用户添加成功！")
                print(f"用户ID: {new_id}")
                print(f"请牢记此用户ID，用于后续操作")
                print(f"默认借阅权限：期限30天，最多借阅5本，最多续借1次")
                print(f"如需修改借阅权限，请使用'设置用户借阅权限'功能")
                # 是否继续添加
                another = input("\n是否继续添加其他用户？(y/n): ").strip().lower()
                if another != "y":
                    break
            else:
                print("已取消添加")
                # 是否重新输入
                retry = input("是否重新输入？(y/n): ").strip().lower()
                if retry != "y":
                    break
    except Exception as e:
        print(f"发生错误: {e}")
        conn.rollback()
    finally:
        conn.close()

# 搜索用户
def search_user():
    while True:
        print("\n请选择搜索方式：")
        print("1. 通过用户ID搜索")
        print("2. 通过用户名搜索")
        print("3. 通过电话搜索")
        print("0. 返回")
        search_type = input("请选择 (0-3): ").strip()
        if search_type == "0":
            return
        if search_type not in ["1", "2", "3"]:
            print("无效选择，请重新输入")
            continue
        break
    keyword = input("请输入搜索关键词: ").strip()
    if not keyword:
        print("错误：搜索关键词不能为空")
        return
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        if search_type == "1":  # 通过ID搜索
            if not keyword.isdigit():
                print("错误：用户ID必须是数字")
                return
            cursor.execute("""
                SELECT user_id, name, phone_number, email, 
                       borrow_period, max_borrow_count, current_borrow_count,
                       registration_date
                FROM users
                WHERE user_id = ?
            """, (keyword,))
        elif search_type == "2":  # 通过用户名搜索
            cursor.execute("""
                SELECT user_id, name, phone_number, email, 
                       borrow_period, max_borrow_count, current_borrow_count,
                       registration_date
                FROM users
                WHERE name LIKE ?
            """, ('%' + keyword + '%',))
        else:  # 通过电话搜索
            cursor.execute("""
                SELECT user_id, name, phone_number, email, 
                       borrow_period, max_borrow_count, current_borrow_count,
                       registration_date
                FROM users
                WHERE phone_number LIKE ?
            """, ('%' + keyword + '%',))
        # 获取查询结果
        users = cursor.fetchall()
        if not users:
            print(f"未找到匹配的用户（搜索方式：{['ID', '用户名', '电话'][int(search_type) - 1]}，关键词：{keyword}）")
            return
        # 显示查询结果
        print(f"\n找到 {len(users)} 个匹配的用户：")
        print(
            f"{'序号':<5} | {'用户ID':<8} | {'姓名':<15} | {'电话':<15} | {'邮箱':<30} | {'当前借阅数':<8} | {'注册日期'}")
        print("-" * 110)
        for i, (user_id, name, phone, email, period, max_borrow, current_borrow, reg_date) in enumerate(users, 1):
            print(
                f"{i:<5} | {user_id:<8} | {name[:15]:<15} | {phone[:15]:<15} | {email[:30]:<30} | {current_borrow:<8} | {reg_date}")
        # 查看用户详情
        while True:
            choice = input("\n请选择要查看详情的用户序号 (输入0返回): ").strip()
            if choice == "0":
                break
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(users):
                print(f"无效选择，请输入1-{len(users)}之间的数字")
                continue
            # 显示用户详情
            user = users[int(choice) - 1]
            user_id, name, phone, email, period, max_borrow, current_borrow, reg_date = user
            print(f"\n用户详情：{name} (ID:{user_id})")
            print(f"电话: {phone}")
            print(f"邮箱: {email}")
            print(f"注册日期: {reg_date}")
            print(f"借阅权限：")
            print(f"借阅期限: {period} 天")
            print(f"最大借阅数量: {max_borrow} 本")
            print(f"当前借阅数量: {current_borrow} 本")
            # 显示用户当前借阅的图书
            cursor.execute("""
                SELECT b.book_id, b.book_name, b.author, br.borrow_date, br.due_date
                FROM borrow_records br
                JOIN books b ON br.book_id = b.book_id
                WHERE br.user_id = ? AND br.return_date IS NULL
                ORDER BY br.due_date ASC
            """, (user_id,))
            current_books = cursor.fetchall()
            if current_books:
                print(f"\n当前借阅的图书 ({len(current_books)} 本)：")
                print(f"{'序号':<5} | {'图书ID':<8} | {'书名':<30} | {'作者':<20} | {'借阅日期':<12} | {'应还日期'}")
                print("-" * 100)
                for i, (book_id, book_name, author, borrow_date, due_date) in enumerate(current_books, 1):
                    print(
                        f"{i:<5} | {book_id:<8} | {book_name[:30]:<30} | {author[:20]:<20} | {borrow_date:<12} | {due_date}")
            else:
                print("\n当前没有借阅的图书")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()

# 更新用户信息
def update_user():
    # 获取用户ID
    while True:
        user_id = input("请输入要更新的用户ID (输入0返回): ").strip()
        if user_id == "0":
            return
        if not user_id.isdigit():
            print("错误：用户ID必须是数字")
            continue
        break
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 检查用户是否存在
        cursor.execute("SELECT user_id, name, phone_number, email FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"错误：用户ID {user_id} 不存在")
            return
        user_id, name, phone, email = user
        print(f"\n当前用户信息：{name} (ID:{user_id})")
        print(f"• 电话: {phone}")
        print(f"• 邮箱: {email}")
        print("\n请输入新的信息（留空保持不变）：")
        new_name = input(f"姓名 (当前: {name}): ").strip()
        if not new_name:
            new_name = name
        new_phone = input(f"电话 (当前: {phone}): ").strip()
        if not new_phone:
            new_phone = phone
        new_email = input(f"邮箱 (当前: {email}): ").strip()
        if not new_email:
            new_email = email
        elif new_email and "@" not in new_email:
            print("警告：邮箱格式可能不正确")
        print("\n更新预览：")
        print(f"姓名: {name} → {new_name}")
        print(f"电话: {phone} → {new_phone}")
        print(f"邮箱: {email} → {new_email}")
        confirm = input("\n是否确认更新？(y/n): ").strip().lower()
        if confirm == "y":
            cursor.execute(
                """UPDATE users 
                   SET name = ?, 
                       phone_number = ?, 
                       email = ? 
                   WHERE user_id = ?""",
                (new_name, new_phone, new_email, user_id)
            )
            conn.commit()
            print(f"\n用户 {name} (ID:{user_id}) 的信息已更新！")
            print(f"新信息：")
            print(f"• 姓名: {new_name}")
            print(f"• 电话: {new_phone}")
            print(f"• 邮箱: {new_email}")
        else:
            print("已取消更新")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()

# 删除用户
def delete_user():
    while True:
        user_id = input("请输入要删除的用户ID (输入0返回): ").strip()
        if user_id == "0":
            return
        if not user_id.isdigit():
            print("错误：用户ID必须是数字")
            continue
        break
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 检查用户是否存在
        cursor.execute("""
            SELECT u.user_id, u.name, COUNT(br.record_id) AS borrow_count
            FROM users u
            LEFT JOIN borrow_records br ON u.user_id = br.user_id AND br.return_date IS NULL
            WHERE u.user_id = ?
            GROUP BY u.user_id
        """, (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"错误：用户ID {user_id} 不存在")
            return
        user_id, name, borrow_count = user
        print(f"\n即将删除用户：{name} (ID:{user_id})")
        if borrow_count > 0:
            print(f"警告：该用户有 {borrow_count} 本图书未归还，无法删除！")
            print("请先处理完所有借阅记录后再尝试删除。")
            return
        print("警告：此操作将永久删除用户账户及其所有历史记录！")
        confirm = input(f"是否确认删除用户 {name} (ID:{user_id})？(输入用户ID确认，其他取消): ").strip()
        if confirm != user_id:
            print("已取消删除操作")
            return
        conn.execute("BEGIN")
        try:
            # 删除用户的借阅记录
            cursor.execute("DELETE FROM borrow_records WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            print(f"\n用户 {name} (ID:{user_id}) 已成功删除！")
        except sqlite3.Error as e:
            # 回滚事务
            conn.rollback()
            print(f"删除失败: {e}")
            print("请联系系统管理员处理")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()

# 显示用户列表
def display_user_list():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 查询所有用户
        cursor.execute("""
            SELECT user_id, name, phone_number, email, 
                   borrow_period, max_borrow_count, current_borrow_count,
                   registration_date
            FROM users
            ORDER BY user_id ASC
        """)
        users = cursor.fetchall()
        if not users:
            print("当前没有注册用户")
            return
        # 计算分页信息
        total_users = len(users)
        users_per_page = 10
        total_pages = (total_users + users_per_page - 1) // users_per_page
        current_page = 1
        while True:
            # 计算当前页的用户范围
            start_idx = (current_page - 1) * users_per_page
            end_idx = min(start_idx + users_per_page, total_users)
            # 显示当前页用户
            print(f"\n第 {current_page}/{total_pages} 页，共 {total_users} 个用户：")
            print(
                f"{'序号':<5} | {'用户ID':<8} | {'姓名':<15} | {'电话':<15} | {'邮箱':<30} | {'当前借阅数':<8} | {'注册日期'}")
            print("-" * 110)
            for i, (user_id, name, phone, email, period, max_borrow, current_borrow, reg_date) in enumerate(
                    users[start_idx:end_idx], start_idx + 1):
                print(
                    f"{i:<5} | {user_id:<8} | {name[:15]:<15} | {phone[:15]:<15} | {email[:30]:<30} | {current_borrow:<8} | {reg_date}")
            # 分页控制
            print("\n操作选项：")
            if current_page > 1:
                print("1. 上一页")
            if current_page < total_pages:
                print("2. 下一页")
            print("3. 查看用户详情")
            print("0. 返回")
            while True:
                choice = input("请选择操作 (0-3): ").strip()
                if choice == "0":
                    return
                if choice == "1" and current_page > 1:
                    current_page -= 1
                    break
                if choice == "2" and current_page < total_pages:
                    current_page += 1
                    break
                if choice == "3":
                    # 查看用户详情
                    user_idx = input("请输入要查看的用户序号: ").strip()
                    if not user_idx.isdigit() or int(user_idx) < 1 or int(user_idx) > total_users:
                        print(f"无效序号，请输入1-{total_users}之间的数字")
                        continue
                    user = users[int(user_idx) - 1]
                    user_id, name, phone, email, period, max_borrow, current_borrow, reg_date = user
                    print(f"\n用户详情：{name} (ID:{user_id})")
                    print(f"• 电话: {phone}")
                    print(f"• 邮箱: {email}")
                    print(f"• 注册日期: {reg_date}")
                    print(f"\n借阅权限：")
                    print(f"• 借阅期限: {period} 天")
                    print(f"• 最大借阅数量: {max_borrow} 本")
                    print(f"• 当前借阅数量: {current_borrow} 本")
                    # 显示用户当前借阅的图书
                    cursor.execute("""
                        SELECT b.book_id, b.book_name, b.author, br.borrow_date, br.due_date
                        FROM borrow_records br
                        JOIN books b ON br.book_id = b.book_id
                        WHERE br.user_id = ? AND br.return_date IS NULL
                        ORDER BY br.due_date ASC
                    """, (user_id,))
                    current_books = cursor.fetchall()
                    if current_books:
                        print(f"\n当前借阅的图书 ({len(current_books)} 本)：")
                        print(
                            f"{'序号':<5} | {'图书ID':<8} | {'书名':<30} | {'作者':<20} | {'借阅日期':<12} | {'应还日期'}")
                        print("-" * 100)
                        for i, (book_id, book_name, author, borrow_date, due_date) in enumerate(current_books, 1):
                            print(
                                f"{i:<5} | {book_id:<8} | {book_name[:30]:<30} | {author[:20]:<20} | {borrow_date:<12} | {due_date}")
                    else:
                        print("\n当前没有借阅的图书")
                    break
                print("无效选择，请重新输入")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()

# 用户借阅权限管理
def mana_user_borrow():
    while True:
        user_id = input("请输入用户ID (输入0返回): ").strip()
        if user_id == "0":
            return
        if not user_id.isdigit():
            print("错误：用户ID必须是数字")
            continue
        break
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    try:
        # 检查用户是否存在
        cursor.execute(
            "SELECT user_id, name, borrow_period, max_borrow_count, max_renew_count FROM users WHERE user_id = ?",
            (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"错误：用户ID {user_id} 不存在")
            return
        user_id, name, current_period, current_max_borrow, current_max_renew = user
        print(f"\n当前用户：{name} (ID:{user_id})")
        print(f"当前借阅权限：")
        print(f"• 借阅期限: {current_period} 天")
        print(f"• 最大借阅数量: {current_max_borrow} 本")
        print(f"• 最大续借次数: {current_max_renew} 次")
        print("\n请输入新的借阅权限（留空保持不变）：")
        new_period = input(f"借阅期限 (当前: {current_period} 天): ").strip()
        if new_period:
            if not new_period.isdigit() or int(new_period) <= 0:
                print("错误：借阅期限必须是正整数")
                return
            new_period = int(new_period)
        else:
            new_period = current_period
        new_max_borrow = input(f"最大借阅数量 (当前: {current_max_borrow} 本): ").strip()
        if new_max_borrow:
            if not new_max_borrow.isdigit() or int(new_max_borrow) <= 0:
                print("错误：最大借阅数量必须是正整数")
                return
            new_max_borrow = int(new_max_borrow)
        else:
            new_max_borrow = current_max_borrow
        new_max_renew = input(f"最大续借次数 (当前: {current_max_renew} 次): ").strip()
        if new_max_renew:
            if not new_max_renew.isdigit() or int(new_max_renew) < 0:
                print("错误：最大续借次数必须是非负整数")
                return
            new_max_renew = int(new_max_renew)
        else:
            new_max_renew = current_max_renew
        # 确认修改
        print("\n新的借阅权限：")
        print(f"• 借阅期限: {new_period} 天")
        print(f"• 最大借阅数量: {new_max_borrow} 本")
        print(f"• 最大续借次数: {new_max_renew} 次")
        confirm = input("\n是否确认修改？(y/n): ").strip().lower()
        if confirm == "y":
            # 更新借阅权限
            cursor.execute(
                """UPDATE users 
                   SET borrow_period = ?, 
                       max_borrow_count = ?, 
                       max_renew_count = ? 
                   WHERE user_id = ?""",
                (new_period, new_max_borrow, new_max_renew, user_id))
            conn.commit()
            print(f"\n用户 {name} (ID:{user_id}) 的借阅权限已更新！")
        else:
            print("已取消修改")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        conn.close()

def reader_management_menu():
    while True:
        print("读者管理")
        print("1. 添加用户")
        print("2. 搜索用户")
        print("3. 更新用户信息")
        print("4. 删除用户")
        print("5. 显示所有用户")
        print("6. 设置用户借阅权限")
        print("7. 返回上级菜单")

        choice = input("请选择操作 (1-7): ").strip()

        if choice == "1":
            add_user()
        elif choice == "2":
            search_user()
        elif choice == "3":
            update_user()
        elif choice == "4":
            delete_user()
        elif choice == "5":
            display_user_list()
        elif choice == "6":
            mana_user_borrow()
        elif choice == "7":
            break
        else:
            print("无效选择，请重新输入")

def verify_admin_password():
    max_attempts = 5
    attempts = 0
    while attempts < max_attempts:
        password = input("请输入管理员密码 (输入q返回): ").strip()
        if password.lower() == 'q':
            return False
        if password == "123456":
            return True
        attempts += 1
        print(f"密码错误，还剩 {max_attempts - attempts} 次尝试机会")
    print("尝试次数过多，返回主菜单")
    return False

def main_menu():
    while True:
        print("\n   图书馆管理系统   ")
        print("1. 图书管理功能")
        print("2. 借阅管理功能")
        print("3. 读者管理功能")
        print("4. 退出系统")
        choice = input("请选择操作 (1-4): ").strip()
        if choice == "1":
            # 图书管理功能（需要管理员权限）
            if verify_admin_password():
                book_management_menu()
            else:
                print("密码错误，返回主菜单")
        elif choice == "2":
            # 借阅管理功能（无需管理员权限）
            borrow_management_menu()
        elif choice == "3":
            # 读者管理功能（需要管理员权限）
            if verify_admin_password():
                reader_management_menu()
            else:
                print("密码错误，返回主菜单")
        elif choice == "4":
            print("感谢使用图书馆管理系统，再见！")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    create_shujuku()
    main_menu()