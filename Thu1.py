# main.py - Phần mềm quản lý quán cafe Nợ Qì ☕
import customtkinter as ctk
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class CafeApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("PHẦN MỀM QUẢN LÝ QUÁN CAFE - NỢ QÌ")
        self.root.geometry("1400x800")
        self.root.state('zoomed')

        # KẾT NỐI MYSQL
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="root",
                password="",
                database="quan_ly_quan_cafe",
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            self.cursor = self.conn.cursor(buffered=True)
            print("✅ Kết nối MySQL thành công!")
        except mysql.connector.Error as err:
            messagebox.showerror("❌ Lỗi kết nối MySQL",
                                 f"Không thể kết nối đến MySQL!\n\nChi tiết lỗi: {err}")
            exit()

        self.current_user = None
        self.current_role = None
        self.selected_ban = None

        # Reference cho cửa sổ thống kê
        self.thong_ke_window = None
        self.tree_thong_ke_ref = None
        self.lbl_tong_all_ref = None

        self.show_login()
        self.root.mainloop()

    # ================== LOGIN ==================
    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self.root, corner_radius=20)
        frame.pack(expand=True)

        try:
            logo = Image.open("logo.png").resize((180, 180))
            logo_tk = ImageTk.PhotoImage(logo)
            lbl_logo = ctk.CTkLabel(frame, image=logo_tk, text="")
            lbl_logo.image = logo_tk
            lbl_logo.pack(pady=20)
        except:
            ctk.CTkLabel(frame, text="☕ NỢ QÌ CAFE",
                         font=("Arial", 40, "bold"),
                         text_color="#8B4513").pack(pady=20)

        ctk.CTkLabel(frame, text="ĐĂNG NHẬP HỆ THỐNG",
                     font=("Arial", 24, "bold")).pack(pady=20)

        entry_user = ctk.CTkEntry(frame, placeholder_text="Tên đăng nhập",
                                  width=300, height=40)
        entry_user.pack(pady=10)

        entry_pass = ctk.CTkEntry(frame, placeholder_text="Mật khẩu",
                                  show="*", width=300, height=40)
        entry_pass.pack(pady=10)

        role_var = tk.StringVar(value="Quản lý")
        ctk.CTkOptionMenu(frame, values=["Quản lý", "Nhân viên"],
                          variable=role_var).pack(pady=10)

        def login():
            user = entry_user.get().strip().upper()
            pwd = entry_pass.get()
            role = role_var.get()

            try:
                sql = """SELECT TenDangNhap, VaiTro
                         FROM taikhoan
                         WHERE TenDangNhap = %s AND MatKhau = %s AND VaiTro = %s"""
                self.cursor.execute(sql, (user, pwd, role))
                result = self.cursor.fetchone()

                if result:
                    self.current_user = user
                    self.current_role = role
                    messagebox.showinfo("Thành công",
                                        f"Chào mừng {user}!\nVai trò: {role}")
                    self.show_main()
                else:
                    messagebox.showerror("Lỗi",
                                         "Sai tên đăng nhập, mật khẩu hoặc vai trò!")
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi database", f"Lỗi truy vấn: {err}")

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="ĐĂNG NHẬP", width=140, height=50,
                      command=login, fg_color="#2E8B57",
                      hover_color="#206040").pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="ĐĂNG KÝ", width=140, height=50,
                      command=self.show_register, fg_color="#1E90FF",
                      hover_color="#1873CC").pack(side="left", padx=10)

        ctk.CTkButton(frame, text="Thoát", width=300, height=40,
                      fg_color="gray", command=self.root.quit).pack()

    # ================== REGISTER ==================
    def show_register(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Đăng ký tài khoản")
        win.geometry("400x450")
        win.resizable(False, False)

        ctk.CTkLabel(win, text="ĐĂNG KÝ TÀI KHOẢN",
                     font=("Arial", 24, "bold")).pack(pady=20)

        ctk.CTkLabel(win, text="Tên đăng nhập:").pack(anchor="w", padx=30)
        entry_user = ctk.CTkEntry(win, placeholder_text="Nhập tên đăng nhập",
                                  width=300, height=35)
        entry_user.pack(pady=5, padx=30)

        ctk.CTkLabel(win, text="Mật khẩu:").pack(anchor="w", padx=30)
        entry_pass = ctk.CTkEntry(win, placeholder_text="Nhập mật khẩu",
                                  show="*", width=300, height=35)
        entry_pass.pack(pady=5, padx=30)

        ctk.CTkLabel(win, text="Xác nhận mật khẩu:").pack(anchor="w", padx=30)
        entry_confirm = ctk.CTkEntry(win, placeholder_text="Xác nhận mật khẩu",
                                     show="*", width=300, height=35)
        entry_confirm.pack(pady=5, padx=30)

        ctk.CTkLabel(win, text="Vai trò:").pack(anchor="w", padx=30)
        role_var = tk.StringVar(value="Nhân viên")
        ctk.CTkOptionMenu(win, values=["Quản lý", "Nhân viên"],
                          variable=role_var, width=300).pack(pady=5, padx=30)

        def dang_ky():
            user = entry_user.get().strip().upper()
            pwd = entry_pass.get()
            pwd_confirm = entry_confirm.get()
            role = role_var.get()

            if user == "" or pwd == "":
                messagebox.showerror("Lỗi", "Tên đăng nhập và mật khẩu không được để trống!")
                return
            if pwd != pwd_confirm:
                messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
                return
            if len(pwd) < 4:
                messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 4 ký tự!")
                return

            try:
                self.cursor.execute("SELECT TenDangNhap FROM taikhoan WHERE TenDangNhap = %s", (user,))
                if self.cursor.fetchone():
                    messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
                    return

                sql_insert = "INSERT INTO taikhoan (TenDangNhap, MatKhau, VaiTro) VALUES (%s, %s, %s)"
                self.cursor.execute(sql_insert, (user, pwd, role))
                self.conn.commit()
                messagebox.showinfo("✅ Thành công", f"Đã đăng ký tài khoản '{user}'\nVai trò: {role}")
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi database", f"Lỗi: {err}")

        button_frame = ctk.CTkFrame(win)
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Đăng ký", width=120, height=40,
                      command=dang_ky, fg_color="#1E90FF",
                      hover_color="#1873CC").pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Quay lại", width=120, height=40,
                      fg_color="gray", command=win.destroy).pack(side="left", padx=10)

    # ================== MAIN ==================
    def show_main(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Menu trên
        menu_frame = ctk.CTkFrame(self.root, height=60, corner_radius=0)
        menu_frame.pack(fill="x")
        menu_frame.pack_propagate(False)

        # ----------- MENU HỆ THỐNG -----------
        menu_system = ctk.CTkOptionMenu(
            menu_frame,
            values=["Chọn chức năng", "➕ Thêm món mới", "➕ Tạo bàn mới"],
            width=180,
            command=self.xu_ly_menu_he_thong
        )
        menu_system.pack(side="left", padx=20)
        menu_system.set("☰ Hệ thống")

        # ✨ NÚT QUẢN LÝ DANH MỤC - CHỈ QUẢN LÝ
        if self.current_role == "Quản lý":
            ctk.CTkButton(menu_frame, text="📂 Quản lý danh mục", width=150,
                          command=self.show_quan_ly_danh_muc).pack(side="left", padx=10)

        # ✨ NÚT QUẢN LÝ KHÁCH HÀNG
        ctk.CTkButton(menu_frame, text="👥 Quản lý khách hàng", width=150,
                      command=self.show_quan_ly_khach_hang).pack(side="left", padx=10)

        # ✨ NÚT THỐNG KÊ - CHỈ QUẢN LÝ
        if self.current_role == "Quản lý":
            ctk.CTkButton(menu_frame, text="📊 Thống kê", width=100,
                          command=self.show_thong_ke).pack(side="left", padx=10)

        ctk.CTkLabel(menu_frame, text=f"👤 Xin chào: {self.current_user}",
                     font=("Arial", 16)).pack(side="right", padx=20)
        ctk.CTkButton(menu_frame, text="Đăng xuất", width=100,
                      command=self.show_login).pack(side="right", padx=10)

        # Nội dung chính
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = ctk.CTkFrame(main_frame, width=300)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="BÀN ĐANG CHỌN:", font=("Arial", 14, "bold")).pack(pady=10)
        self.lbl_ban_chon = ctk.CTkLabel(left_frame, text="Chưa chọn bàn",
                                         font=("Arial", 16), text_color="red")
        self.lbl_ban_chon.pack(pady=5)

        scroll = tk.Scrollbar(left_frame)
        self.list_ban = tk.Listbox(left_frame, yscrollcommand=scroll.set,
                                   font=("Arial", 12), bg="#FFF8DC")
        scroll.config(command=self.list_ban.yview)
        scroll.pack(side="right", fill="y")
        self.list_ban.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_ban()
        self.list_ban.bind("<<ListboxSelect>>", self.chon_ban)

        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        top_frame = ctk.CTkFrame(right_frame)
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top_frame, text="Loại đồ uống:").pack(side="left", padx=5)
        self.cb_danhmuc = ctk.CTkComboBox(top_frame, values=self.get_danhmuc(),
                                          command=self.load_mon_theo_danhmuc)
        self.cb_danhmuc.pack(side="left", padx=5)
        self.cb_danhmuc.set("Tất cả")

        ctk.CTkLabel(top_frame, text="Số lượng:").pack(side="left", padx=5)
        self.entry_sl = ctk.CTkEntry(top_frame, width=80)
        self.entry_sl.insert(0, "1")
        self.entry_sl.pack(side="left", padx=5)

        ctk.CTkButton(top_frame, text="➕ Thêm món", fg_color="#1E90FF",
                      command=self.them_mon).pack(side="left", padx=10)

        cols = ("Mã món", "Tên món", "Giá tiền", "Trạng thái")
        self.tree_mon = ttk.Treeview(right_frame, columns=cols,
                                     show="headings", height=12)
        for col in cols:
            self.tree_mon.heading(col, text=col)
            width = 200 if col == "Tên món" else 120
            self.tree_mon.column(col, width=width)
        self.tree_mon.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_mon.bind("<Double-1>", lambda e: self.them_mon())

        order_frame = ctk.CTkFrame(right_frame)
        order_frame.pack(fill="both", padx=10, pady=10)

        cols_order = ("Mã món", "Tên đồ uống", "Đơn giá", "Số lượng", "Thành tiền")
        self.tree_order = ttk.Treeview(order_frame, columns=cols_order,
                                       show="headings")
        for col in cols_order:
            self.tree_order.heading(col, text=col)
            self.tree_order.column(col, width=120)
        self.tree_order.pack(side="left", fill="both", expand=True)

        bottom_frame = ctk.CTkFrame(right_frame)
        bottom_frame.pack(fill="x", pady=10)

        self.lbl_tong = ctk.CTkLabel(bottom_frame, text="TỔNG: 0 VNĐ",
                                     font=("Arial", 20, "bold"), text_color="red")
        self.lbl_tong.pack(side="left", padx=20)

        ctk.CTkButton(bottom_frame, text="💰 Thanh toán", width=150, height=50,
                      fg_color="#32CD32", font=("Arial", 16, "bold"),
                      command=self.thanh_toan).pack(side="right", padx=10)
        ctk.CTkButton(bottom_frame, text="🖨️ In hóa đơn", width=150, height=50,
                      fg_color="#228B22", font=("Arial", 16, "bold"),
                      command=self.in_hoa_don).pack(side="right", padx=10)

        self.load_mon()

    # ================== QUẢN LÝ DANH MỤC ==================
    def show_quan_ly_danh_muc(self):
        win = ctk.CTkToplevel(self.root)
        win.title("📂 Quản lý danh mục")
        win.geometry("900x600")
        win.resizable(True, True)

        top_frame = ctk.CTkFrame(win)
        top_frame.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(top_frame, text="📂 QUẢN LÝ DANH MỤC",
                     font=("Arial", 20, "bold")).pack(side="left")
        ctk.CTkButton(top_frame, text="➕ Thêm danh mục", width=130,
                      command=lambda: self.form_them_danh_muc(win)).pack(side="right", padx=5)
        ctk.CTkButton(top_frame, text="🔄 Làm mới", width=100,
                      command=lambda: self.load_danh_muc(tree_dm)).pack(side="right", padx=5)

        table_frame = ctk.CTkFrame(win)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)
        cols = ("Mã DM", "Tên danh mục", "Mô tả", "Trạng thái", "Số món", "Thao tác")
        tree_dm = ttk.Treeview(table_frame, columns=cols, show="headings", height=20)

        for col in cols:
            tree_dm.heading(col, text=col)
            width = {"Mã DM": 70, "Tên danh mục": 150, "Mô tả": 250, "Trạng thái": 120,
                     "Số món": 100, "Thao tác": 150}.get(col, 100)
            tree_dm.column(col, width=width, anchor="center" if col != "Tên danh mục" and col != "Mô tả" else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree_dm.yview)
        tree_dm.configure(yscroll=scrollbar.set)
        tree_dm.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tree_dm.bind("<Double-1>", lambda e: self.form_sua_danh_muc(tree_dm, win))

        self.load_danh_muc(tree_dm)

    def load_danh_muc(self, tree):
        try:
            for item in tree.get_children():
                tree.delete(item)

            sql = """SELECT d.MaDanhMuc, d.TenDanhMuc, d.MoTa, d.TrangThai,
                            COALESCE(COUNT(m.MaMon), 0) as SoMon
                     FROM danhmuc d
                     LEFT JOIN mon m ON d.MaDanhMuc = m.MaDanhMuc
                     GROUP BY d.MaDanhMuc
                     ORDER BY d.MaDanhMuc"""
            self.cursor.execute(sql)
            for row in self.cursor.fetchall():
                trang_thai_icon = "✅ Kích hoạt" if row[3] == "Kích hoạt" else "❌ Tạm ngưng"
                tree.insert("", "end",
                            values=(row[0], row[1], row[2] or "", trang_thai_icon, row[4],
                                    "✏️ Sửa | 🗑️ Xóa"))
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi database", f"Lỗi: {err}")

    def form_them_danh_muc(self, parent_win):
        win = ctk.CTkToplevel(parent_win)
        win.title("Thêm danh mục mới")
        win.geometry("400x380")
        win.resizable(False, False)

        ctk.CTkLabel(win, text="THÊM DANH MỤC MỚI",
                     font=("Arial", 20, "bold")).pack(pady=15)

        ctk.CTkLabel(win, text="Tên danh mục:").pack(anchor="w", padx=30)
        entry_ten = ctk.CTkEntry(win, placeholder_text="VD: Cà phê, Trà, Kem...",
                                 width=300, height=35)
        entry_ten.pack(pady=5, padx=30)

        ctk.CTkLabel(win, text="Mô tả:").pack(anchor="w", padx=30)
        entry_mota = ctk.CTkEntry(win, placeholder_text="Mô tả danh mục",
                                  width=300, height=35)
        entry_mota.pack(pady=5, padx=30)

        ctk.CTkLabel(win, text="Trạng thái:").pack(anchor="w", padx=30)
        trang_thai_var = tk.StringVar(value="Kích hoạt")
        cb_tt = ctk.CTkComboBox(win, values=["Kích hoạt", "Tạm ngưng"],
                                variable=trang_thai_var, width=300, height=35)
        cb_tt.pack(pady=5, padx=30)

        def them_dm():
            ten = entry_ten.get().strip()
            mota = entry_mota.get().strip()
            trang_thai = trang_thai_var.get()
            if not ten:
                messagebox.showerror("Lỗi", "Tên danh mục không được để trống!")
                return
            try:
                self.cursor.execute("SELECT MaDanhMuc FROM danhmuc WHERE TenDanhMuc = %s", (ten,))
                if self.cursor.fetchone():
                    messagebox.showerror("Lỗi", "Danh mục này đã tồn tại!")
                    return

                sql = """INSERT INTO danhmuc (TenDanhMuc, MoTa, TrangThai)
                         VALUES (%s, %s, %s)"""
                self.cursor.execute(sql, (ten, mota or None, trang_thai))
                self.conn.commit()
                messagebox.showinfo("✅ Thành công", f"Đã thêm danh mục: {ten}")
                win.destroy()
                for widget in parent_win.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Treeview):
                                self.load_danh_muc(child)
                                break
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi database", f"Lỗi: {err}")

        ctk.CTkButton(win, text="Lưu", width=300, height=40,
                      fg_color="#1E90FF", hover_color="#1873CC",
                      command=them_dm).pack(pady=20, padx=30)

    def form_sua_danh_muc(self, tree, parent_win):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn danh mục!")
            return

        values = tree.item(sel[0])['values']
        ma_dm = values[0]

        try:
            self.cursor.execute("""SELECT MaDanhMuc, TenDanhMuc, MoTa, TrangThai
                                   FROM danhmuc WHERE MaDanhMuc = %s""", (ma_dm,))
            result = self.cursor.fetchone()
            if not result:
                messagebox.showerror("Lỗi", "Không tìm thấy danh mục!")
                return

            win = ctk.CTkToplevel(parent_win)
            win.title("Sửa danh mục")
            win.geometry("400x400")
            win.resizable(False, False)

            ctk.CTkLabel(win, text=f"SỬA DANH MỤC - Mã: {ma_dm}",
                         font=("Arial", 20, "bold")).pack(pady=15)

            ctk.CTkLabel(win, text="Tên danh mục:").pack(anchor="w", padx=30)
            entry_ten = ctk.CTkEntry(win, width=300, height=35)
            entry_ten.insert(0, result[1])
            entry_ten.pack(pady=5, padx=30)

            ctk.CTkLabel(win, text="Mô tả:").pack(anchor="w", padx=30)
            entry_mota = ctk.CTkEntry(win, width=300, height=35)
            entry_mota.insert(0, result[2] if result[2] else "")
            entry_mota.pack(pady=5, padx=30)

            ctk.CTkLabel(win, text="Trạng thái:").pack(anchor="w", padx=30)
            trang_thai_var = tk.StringVar(value=result[3])
            cb_tt = ctk.CTkComboBox(win, values=["Kích hoạt", "Tạm ngưng"],
                                    variable=trang_thai_var, width=300, height=35)
            cb_tt.pack(pady=5, padx=30)

            def luu_sua():
                ten = entry_ten.get().strip()
                mota = entry_mota.get().strip()
                trang_thai = trang_thai_var.get()
                if not ten:
                    messagebox.showerror("Lỗi", "Tên danh mục không được để trống!")
                    return
                try:
                    sql = """UPDATE danhmuc SET TenDanhMuc = %s, MoTa = %s,
                                             TrangThai = %s WHERE MaDanhMuc = %s"""
                    self.cursor.execute(sql, (ten, mota or None, trang_thai, ma_dm))
                    self.conn.commit()
                    messagebox.showinfo("✅ Thành công", "Cập nhật danh mục thành công!")
                    win.destroy()
                    self.load_danh_muc(tree)
                except mysql.connector.Error as err:
                    messagebox.showerror("Lỗi database", f"Lỗi: {err}")

            button_frame = ctk.CTkFrame(win)
            button_frame.pack(pady=15)
            ctk.CTkButton(button_frame, text="💾 Lưu", width=120, height=40,
                          fg_color="#1E90FF", command=luu_sua).pack(side="left", padx=10)
            ctk.CTkButton(button_frame, text="🗑️ Xóa", width=120, height=40,
                          fg_color="red", command=lambda: self.xoa_danh_muc(ma_dm, tree, win)).pack(side="left",
                                                                                                    padx=10)

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi database", f"Lỗi: {err}")

    def xoa_danh_muc(self, ma_dm, tree, win):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM mon WHERE MaDanhMuc = %s", (ma_dm,))
            so_mon = self.cursor.fetchone()[0]
            if so_mon > 0:
                messagebox.showwarning("Cảnh báo",
                                       f"Không thể xóa! Danh mục này còn {so_mon} món hàng.\n"
                                       "Vui lòng xóa hoặc chuyển các món sang danh mục khác trước.")
                return

            if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa danh mục này?\nMã DM: {ma_dm}"):
                self.cursor.execute("DELETE FROM danhmuc WHERE MaDanhMuc = %s", (ma_dm,))
                self.conn.commit()
                messagebox.showinfo("✅ Thành công", "Đã xóa danh mục!")
                win.destroy()
                self.load_danh_muc(tree)
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi database", f"Lỗi: {err}")

    # ================== QUẢN LÝ KHÁCH HÀNG ==================
    def show_quan_ly_khach_hang(self):
        win = ctk.CTkToplevel(self.root)
        win.title("👥 Quản lý khách hàng")
        win.geometry("1000x700")
        win.resizable(True, True)

        top_frame = ctk.CTkFrame(win)
        top_frame.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(top_frame, text="👥 QUẢN LÝ KHÁCH HÀNG",
                     font=("Arial", 20, "bold")).pack(side="left")
        if self.current_role == "Quản lý":
            ctk.CTkButton(top_frame, text="➕ Thêm khách hàng", width=130,
                          command=lambda: self.form_them_khach_hang(win)).pack(side="right", padx=5)
        ctk.CTkButton(top_frame, text="🔄 Làm mới", width=100,
                      command=lambda: self.load_khach_hang(tree_kh, is_admin=(self.current_role == "Quản lý"))).pack(
            side="right", padx=5)

        search_frame = ctk.CTkFrame(win)
        search_frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(search_frame, text="Tìm kiếm:").pack(side="left", padx=5)
        entry_search = ctk.CTkEntry(search_frame, placeholder_text="Nhập SDT hoặc tên khách hàng",
                                    width=300, height=35)
        entry_search.pack(side="left", padx=5)

        def tim_khach_hang():
            keyword = entry_search.get().strip()
            self.load_khach_hang(tree_kh, keyword, is_admin=(self.current_role == "Quản lý"))

        ctk.CTkButton(search_frame, text="🔍 Tìm", width=80,
                      command=tim_khach_hang).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Xóa lọc", width=80,
                      command=lambda: self.load_khach_hang(tree_kh, is_admin=(self.current_role == "Quản lý"))).pack(
            side="left", padx=5)

        table_frame = ctk.CTkFrame(win)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)
        cols = ("Mã KH", "Tên khách hàng", "Số điện thoại", "Email", "Địa chỉ", "Tổng chi tiêu", "Đồ ưu thích",
                "Thao tác")
        tree_kh = ttk.Treeview(table_frame, columns=cols, show="headings", height=20)

        for col in cols:
            tree_kh.heading(col, text=col)

        tree_kh.column("Mã KH", width=70, anchor="center")
        tree_kh.column("Tên khách hàng", width=140, anchor="w")
        tree_kh.column("Số điện thoại", width=120, anchor="center")
        tree_kh.column("Email", width=120, anchor="w")
        tree_kh.column("Địa chỉ", width=150, anchor="w")
        tree_kh.column("Tổng chi tiêu", width=130, anchor="center")
        tree_kh.column("Đồ ưu thích", width=150, anchor="w")
        tree_kh.column("Thao tác", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree_kh.yview)
        tree_kh.configure(yscroll=scrollbar.set)
        tree_kh.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.current_role == "Quản lý":
            tree_kh.bind("<Double-1>", lambda e: self.form_sua_khach_hang(tree_kh, win))
        else:
            tree_kh.bind("<Double-1>", lambda e: self.xem_chi_tiet_khach_hang(tree_kh))

        self.load_khach_hang(tree_kh, is_admin=(self.current_role == "Quản lý"))

    def load_khach_hang(self, tree, keyword="", is_admin=False):
        try:
            for item in tree.get_children():
                tree.delete(item)

            if keyword:
                sql = """SELECT k.MaKhachHang, k.TenKhachHang, k.SoDienThoai, k.Email, k.DiaChi,
                                COALESCE(SUM(h.TongTien), 0) as TongChiTieu
                         FROM khachhang k
                         LEFT JOIN hoadon h ON k.MaKhachHang = h.MaKhachHang
                         WHERE k.SoDienThoai LIKE %s OR k.TenKhachHang LIKE %s
                         GROUP BY k.MaKhachHang
                         ORDER BY k.MaKhachHang"""
                self.cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%"))
            else:
                sql = """SELECT k.MaKhachHang, k.TenKhachHang, k.SoDienThoai, k.Email, k.DiaChi,
                                COALESCE(SUM(h.TongTien), 0) as TongChiTieu
                         FROM khachhang k
                         LEFT JOIN hoadon h ON k.MaKhachHang = h.MaKhachHang
                         GROUP BY k.MaKhachHang
                         ORDER BY k.MaKhachHang"""
                self.cursor.execute(sql)

            for row in self.cursor.fetchall():
                ma_kh = row[0]

                self.cursor.execute("""SELECT m.TenMon FROM chitiethoadon ct
                                      JOIN mon m ON ct.MaMon = m.MaMon
                                      JOIN hoadon h ON ct.MaHoaDon = h.MaHoaDon
                                      WHERE h.MaKhachHang = %s
                                      GROUP BY m.TenMon
                                      ORDER BY COUNT(*) DESC LIMIT 1""", (ma_kh,))
                do_uu_thich = self.cursor.fetchone()
                do_uu_thich = do_uu_thich[0] if do_uu_thich else "Chưa có"

                thao_tac = "✏️ Sửa | 🗑️ Xóa" if is_admin else "👁️ Xem"

                tree.insert("", "end",
                            values=(ma_kh, row[1], row[2], row[3] or "", row[4] or "", f"{row[5]:,.0f}",
                                    do_uu_thich, thao_tac))

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi database", f"Lỗi: {err}")

    def form_them_khach_hang(self, parent_win):
        win = ctk.CTkToplevel(parent_win)
        win.title("Thêm khách hàng mới")
        win.geometry("400x450")
        win.resizable(False, False)

        ctk.CTkLabel(win, text="THÊM KHÁCH HÀNG MỚI",
                     font=("Arial", 20, "bold")).pack(pady=15)

        ctk.CTkLabel(win, text="Tên khách hàng:").pack(anchor="w", padx=30)
        entry_ten = ctk.CTkEntry(win, placeholder_text="Nhập tên khách hàng",
                                 width=300, height=35)
        entry_ten.pack(pady=5, padx=30)

        ctk.CTkLabel(win, text="Số điện thoại:").pack(anchor="w", padx=30)
        entry_sdt = ctk.CTkEntry(win, placeholder_text="Nhập số điện thoại",
                                 width=300, height=35)
        entry_sdt.pack(pady=5, padx=30)

        ctk.CTkLabel(win, text="Email:").pack(anchor="w", padx=30)
        entry_email = ctk.CTkEntry(win, placeholder_text="Nhập email",
                                   width=300, height=35)
        entry_email.pack(pady=5, padx=30)

        ctk.CTkLabel(win, text="Địa chỉ:").pack(anchor="w", padx=30)
        entry_dia_chi = ctk.CTkEntry(win, placeholder_text="Nhập địa chỉ",
                                     width=300, height=35)
        entry_dia_chi.pack(pady=5, padx=30)

        def them_kh():
            ten = entry_ten.get().strip()
            sdt = entry_sdt.get().strip()
            email = entry_email.get().strip()
            dia_chi = entry_dia_chi.get().strip()

            if not ten or not sdt:
                messagebox.showerror("Lỗi", "Tên và số điện thoại không được để trống!")
                return

            try:
                self.cursor.execute("SELECT MaKhachHang FROM khachhang WHERE SoDienThoai = %s", (sdt,))
                if self.cursor.fetchone():
                    messagebox.showerror("Lỗi", "Số điện thoại đã tồn tại!")
                    return

                sql = """INSERT INTO khachhang (TenKhachHang, SoDienThoai, Email, DiaChi)
                         VALUES (%s, %s, %s, %s)"""
                self.cursor.execute(sql, (ten, sdt, email or None, dia_chi or None))
                self.conn.commit()

                messagebox.showinfo("✅ Thành công", f"Đã thêm khách hàng: {ten}")
                win.destroy()
                for widget in parent_win.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Treeview):
                                self.load_khach_hang(child, is_admin=True)
                                break

            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi database", f"Lỗi: {err}")

        ctk.CTkButton(win, text="Lưu", width=300, height=40,
                      fg_color="#1E90FF", hover_color="#1873CC",
                      command=them_kh).pack(pady=20, padx=30)

    def form_sua_khach_hang(self, tree, parent_win):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
            return

        item = tree.item(sel[0])
        values = item['values']
        ma_kh = values[0]

        try:
            self.cursor.execute("""SELECT MaKhachHang, TenKhachHang, SoDienThoai, Email, DiaChi
                                   FROM khachhang WHERE MaKhachHang = %s""", (ma_kh,))
            result = self.cursor.fetchone()

            if not result:
                messagebox.showerror("Lỗi", "Không tìm thấy khách hàng!")
                return

            win = ctk.CTkToplevel(parent_win)
            win.title("Sửa thông tin khách hàng")
            win.geometry("400x450")
            win.resizable(False, False)

            ctk.CTkLabel(win, text=f"SỬA KHÁCH HÀNG - Mã: {ma_kh}",
                         font=("Arial", 20, "bold")).pack(pady=15)

            ctk.CTkLabel(win, text="Tên khách hàng:").pack(anchor="w", padx=30)
            entry_ten = ctk.CTkEntry(win, width=300, height=35)
            entry_ten.insert(0, result[1])
            entry_ten.pack(pady=5, padx=30)

            ctk.CTkLabel(win, text="Số điện thoại:").pack(anchor="w", padx=30)
            entry_sdt = ctk.CTkEntry(win, width=300, height=35)
            entry_sdt.insert(0, result[2])
            entry_sdt.pack(pady=5, padx=30)

            ctk.CTkLabel(win, text="Email:").pack(anchor="w", padx=30)
            entry_email = ctk.CTkEntry(win, width=300, height=35)
            entry_email.insert(0, result[3] if result[3] else "")
            entry_email.pack(pady=5, padx=30)

            ctk.CTkLabel(win, text="Địa chỉ:").pack(anchor="w", padx=30)
            entry_dia_chi = ctk.CTkEntry(win, width=300, height=35)
            entry_dia_chi.insert(0, result[4] if result[4] else "")
            entry_dia_chi.pack(pady=5, padx=30)

            def luu_sua():
                ten = entry_ten.get().strip()
                sdt = entry_sdt.get().strip()
                email = entry_email.get().strip()
                dia_chi = entry_dia_chi.get().strip()

                if not ten or not sdt:
                    messagebox.showerror("Lỗi", "Tên và số điện thoại không được để trống!")
                    return

                try:
                    sql = """UPDATE khachhang SET TenKhachHang = %s, SoDienThoai = %s, 
                                              Email = %s, DiaChi = %s WHERE MaKhachHang = %s"""
                    self.cursor.execute(sql, (ten, sdt, email or None, dia_chi or None, ma_kh))
                    self.conn.commit()

                    messagebox.showinfo("✅ Thành công", "Cập nhật thông tin khách hàng thành công!")
                    win.destroy()
                    self.load_khach_hang(tree, is_admin=True)

                except mysql.connector.Error as err:
                    messagebox.showerror("Lỗi database", f"Lỗi: {err}")

            button_frame = ctk.CTkFrame(win)
            button_frame.pack(pady=15)

            ctk.CTkButton(button_frame, text="💾 Lưu", width=120, height=40,
                          fg_color="#1E90FF", command=luu_sua).pack(side="left", padx=10)

            ctk.CTkButton(button_frame, text="🗑️ Xóa", width=120, height=40,
                          fg_color="red", command=lambda: self.xoa_khach_hang(ma_kh, tree, win)).pack(side="left",
                                                                                                      padx=10)

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi database", f"Lỗi: {err}")

    def xoa_khach_hang(self, ma_kh, tree, win):
        if messagebox.askyesno("Xác nhận xóa",
                               f"Bạn có chắc chắn muốn xóa khách hàng này?\nMã KH: {ma_kh}"):
            try:
                self.cursor.execute("DELETE FROM khachhang WHERE MaKhachHang = %s", (ma_kh,))
                self.conn.commit()

                messagebox.showinfo("✅ Thành công", "Đã xóa khách hàng!")
                win.destroy()
                self.load_khach_hang(tree, is_admin=True)

            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi database", f"Lỗi: {err}")

    def xem_chi_tiet_khach_hang(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
            return

        item = tree.item(sel[0])
        values = item['values']
        ma_kh = values[0]

        try:
            self.cursor.execute("""SELECT MaKhachHang, TenKhachHang, SoDienThoai, Email, DiaChi
                                   FROM khachhang WHERE MaKhachHang = %s""", (ma_kh,))
            result = self.cursor.fetchone()

            if not result:
                messagebox.showerror("Lỗi", "Không tìm thấy khách hàng!")
                return

            win = ctk.CTkToplevel(self.root)
            win.title("Chi tiết khách hàng")
            win.geometry("500x600")
            win.resizable(False, False)

            ctk.CTkLabel(win, text=f"👤 CHI TIẾT KHÁCH HÀNG",
                         font=("Arial", 20, "bold")).pack(pady=15)

            info_frame = ctk.CTkFrame(win)
            info_frame.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(info_frame, text=f"Mã KH: {result[0]}",
                         font=("Arial", 13, "bold")).pack(anchor="w", pady=5)
            ctk.CTkLabel(info_frame, text=f"Tên: {result[1]}",
                         font=("Arial", 13)).pack(anchor="w", pady=5)
            ctk.CTkLabel(info_frame, text=f"SDT: {result[2]}",
                         font=("Arial", 13)).pack(anchor="w", pady=5)
            ctk.CTkLabel(info_frame, text=f"Email: {result[3] if result[3] else 'Chưa cập nhập'}",
                         font=("Arial", 13)).pack(anchor="w", pady=5)
            ctk.CTkLabel(info_frame, text=f"Địa chỉ: {result[4] if result[4] else 'Chưa cập nhập'}",
                         font=("Arial", 13)).pack(anchor="w", pady=5)

            ctk.CTkLabel(win, text="🎁 ĐỒ ƯU THÍCH",
                         font=("Arial", 14, "bold")).pack(pady=10)

            self.cursor.execute("""SELECT m.TenMon, COUNT(*) as SoLan, SUM(ct.SoLuong) as TongSoLuong
                                  FROM chitiethoadon ct
                                  JOIN mon m ON ct.MaMon = m.MaMon
                                  JOIN hoadon h ON ct.MaHoaDon = h.MaHoaDon
                                  WHERE h.MaKhachHang = %s
                                  GROUP BY m.TenMon
                                  ORDER BY SoLan DESC
                                  LIMIT 5""", (ma_kh,))

            favorites = self.cursor.fetchall()
            if favorites:
                for i, fav in enumerate(favorites, 1):
                    ctk.CTkLabel(win, text=f"{i}. {fav[0]} - Mua {fav[1]} lần ({fav[2] or 0} cái)",
                                 font=("Arial", 12)).pack(anchor="w", padx=30, pady=5)
            else:
                ctk.CTkLabel(win, text="Chưa có lịch sử mua hàng",
                             font=("Arial", 12)).pack(anchor="w", padx=30, pady=5)

            ctk.CTkLabel(win, text="📋 LỊCH SỬ MUA HÀNG",
                         font=("Arial", 14, "bold")).pack(pady=10)

            self.cursor.execute("""SELECT h.MaHoaDon, h.NgayGio, h.TongTien
                                  FROM hoadon h
                                  WHERE h.MaKhachHang = %s
                                  ORDER BY h.NgayGio DESC
                                  LIMIT 10""", (ma_kh,))

            history = self.cursor.fetchall()
            if history:
                for h in history:
                    ctk.CTkLabel(win, text=f"HĐ #{h[0]} - {h[1]} - {h[2]:,.0f} VNĐ",
                                 font=("Arial", 11)).pack(anchor="w", padx=30, pady=3)
            else:
                ctk.CTkLabel(win, text="Chưa có hóa đơn",
                             font=("Arial", 11)).pack(anchor="w", padx=30, pady=3)

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi database", f"Lỗi: {err}")

    # ================== THỐNG KÊ DOANH THU ==================
    def show_thong_ke(self):
        if self.thong_ke_window and self.thong_ke_window.winfo_exists():
            self.thong_ke_window.lift()
            return

        self.thong_ke_window = ctk.CTkToplevel(self.root)
        self.thong_ke_window.title("📊 Thống kê doanh thu")
        self.thong_ke_window.geometry("900x600")
        self.thong_ke_window.resizable(True, True)
        self.thong_ke_window.protocol("WM_DELETE_WINDOW", self.on_close_thong_ke)

        top_frame = ctk.CTkFrame(self.thong_ke_window)
        top_frame.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(top_frame, text="THỐNG KÊ DOANH THU HÀNG NGÀY",
                     font=("Arial", 20, "bold")).pack(side="left")
        ctk.CTkButton(top_frame, text="🔄 Làm mới", width=100,
                      command=lambda: self.load_thong_ke(self.tree_thong_ke_ref)).pack(side="right", padx=5)

        filter_frame = ctk.CTkFrame(self.thong_ke_window)
        filter_frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(filter_frame, text="Chọn ngày:").pack(side="left", padx=5)
        entry_ngay = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD", width=150, height=35)
        entry_ngay.pack(side="left", padx=5)
        ctk.CTkLabel(filter_frame, text="Chọn tháng:").pack(side="left", padx=5)
        entry_thang = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM", width=150, height=35)
        entry_thang.pack(side="left", padx=5)
        ctk.CTkLabel(filter_frame, text="Chọn năm:").pack(side="left", padx=5)
        entry_nam = ctk.CTkEntry(filter_frame, placeholder_text="YYYY", width=100, height=35)
        entry_nam.pack(side="left", padx=5)

        def loc_thong_ke():
            ngay = entry_ngay.get().strip()
            thang = entry_thang.get().strip()
            nam = entry_nam.get().strip()
            self.load_thong_ke(self.tree_thong_ke_ref, ngay, thang, nam)

        ctk.CTkButton(filter_frame, text="🔍 Lọc", width=100,
                      command=loc_thong_ke).pack(side="left", padx=10)

        table_frame = ctk.CTkFrame(self.thong_ke_window)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)
        cols = ("Ngày", "Tổng hóa đơn", "Tổng tiền (VNĐ)", "Trung bình/hóa đơn")
        self.tree_thong_ke_ref = ttk.Treeview(table_frame, columns=cols, show="headings", height=20)

        for col in cols:
            self.tree_thong_ke_ref.heading(col, text=col)
            self.tree_thong_ke_ref.column(col, width=150 if col == "Ngày" else 200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_thong_ke_ref.yview)
        self.tree_thong_ke_ref.configure(yscroll=scrollbar.set)
        self.tree_thong_ke_ref.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        summary_frame = ctk.CTkFrame(self.thong_ke_window)
        summary_frame.pack(fill="x", padx=15, pady=10)
        self.lbl_tong_all_ref = ctk.CTkLabel(summary_frame, text="📊 TỔNG TOÀN BỘ: 0 VNĐ",
                                             font=("Arial", 13, "bold"), text_color="green")
        self.lbl_tong_all_ref.pack(side="left", padx=20, pady=10)

        self.load_thong_ke(self.tree_thong_ke_ref)

    def on_close_thong_ke(self):
        self.thong_ke_window.destroy()
        self.thong_ke_window = None
        self.tree_thong_ke_ref = None
        self.lbl_tong_all_ref = None

    def load_thong_ke(self, tree, ngay="", thang="", nam=""):
        try:
            for item in tree.get_children():
                tree.delete(item)

            if ngay:
                sql = """SELECT DATE(NgayGio) as Ngay,
                                COUNT(*) as TongHoaDon,
                                SUM(TongTien) as TongTien,
                                ROUND(AVG(TongTien), 0) as TrungBinh
                         FROM hoadon
                         WHERE DATE(NgayGio) = %s
                         GROUP BY DATE(NgayGio)
                         ORDER BY NgayGio DESC"""
                self.cursor.execute(sql, (ngay,))
            elif thang:
                sql = """SELECT DATE(NgayGio) as Ngay,
                                COUNT(*) as TongHoaDon,
                                SUM(TongTien) as TongTien,
                                ROUND(AVG(TongTien), 0) as TrungBinh
                         FROM hoadon
                         WHERE DATE_FORMAT(NgayGio, '%Y-%m') = %s
                         GROUP BY DATE(NgayGio)
                         ORDER BY NgayGio DESC"""
                self.cursor.execute(sql, (thang,))
            elif nam:
                sql = """SELECT DATE(NgayGio) as Ngay,
                                COUNT(*) as TongHoaDon,
                                SUM(TongTien) as TongTien,
                                ROUND(AVG(TongTien), 0) as TrungBinh
                         FROM hoadon
                         WHERE YEAR(NgayGio) = %s
                         GROUP BY DATE(NgayGio)
                         ORDER BY NgayGio DESC"""
                self.cursor.execute(sql, (nam,))
            else:
                sql = """SELECT DATE(NgayGio) as Ngay,
                                COUNT(*) as TongHoaDon,
                                SUM(TongTien) as TongTien,
                                ROUND(AVG(TongTien), 0) as TrungBinh
                         FROM hoadon
                         GROUP BY DATE(NgayGio)
                         ORDER BY NgayGio DESC"""
                self.cursor.execute(sql)

            tong_tien_all = 0
            so_hoa_don_all = 0
            so_ngay = 0

            for row in self.cursor.fetchall():
                tong_tien = row[2] if row[2] is not None else 0
                trung_binh = row[3] if row[3] is not None else 0
                tree.insert("", "end",
                            values=(row[0], f"{row[1]}", f"{tong_tien:,.0f}", f"{trung_binh:,.0f}"))
                tong_tien_all += tong_tien
                so_hoa_don_all += row[1]
                so_ngay += 1

            trung_binh_tien = tong_tien_all / so_hoa_don_all if so_hoa_don_all > 0 else 0
            thong_tin = (f"📊 TỔNG TOÀN BỘ: {tong_tien_all:,.0f} VNĐ | "
                         f"📝 Tổng hóa đơn: {so_hoa_don_all} | "
                         f"📅 Số ngày: {so_ngay} | "
                         f"💰 TB/Hóa đơn: {trung_binh_tien:,.0f} VNĐ")

            if self.lbl_tong_all_ref:
                self.lbl_tong_all_ref.configure(text=thong_tin)

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi database", f"Lỗi: {err}")

    # ================== CÁC HÀM KHÁC ==================
    def xu_ly_menu_he_thong(self, lua_chon):
        if lua_chon == "➕ Thêm món mới":
            if self.current_role != "Quản lý":
                messagebox.showwarning("Không đủ quyền", "Chỉ Quản lý mới thêm món!")
                return
            self.show_them_mon_moi()
        elif lua_chon == "➕ Tạo bàn mới":
            self.form_tao_ban_moi()

    def form_tao_ban_moi(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Tạo bàn mới")
        win.geometry("450x650")  # Tăng chiều cao để chứa nút
        win.resizable(False, False)
        ctk.CTkLabel(win, text="NHẬP THÔNG TIN BÀN",
                     font=("Arial", 20, "bold")).pack(pady=15)
        # ===== PHẦN THÔNG TIN BÀN =====
        ctk.CTkLabel(win, text="Tên bàn / Số bàn:").pack(anchor="w", padx=30)
        entry_ten_ban = ctk.CTkEntry(win, placeholder_text="VD: Bàn 1, Bàn A,...",
                                     width=350, height=35)
        entry_ten_ban.pack(pady=5, padx=30)
        ctk.CTkLabel(win, text="Loại bàn:").pack(anchor="w", padx=30)
        loai_ban_var = tk.StringVar(value="Bàn 2 người")
        cb_loai = ctk.CTkComboBox(win,
                                  values=["Bàn 2 người", "Bàn 4 người", "Bàn 6 người", "Bàn 8 người"],
                                  variable=loai_ban_var,
                                  width=350, height=35)
        cb_loai.pack(pady=5, padx=30)
        # ===== PHẦN THÔNG TIN KHÁCH HÀNG =====
        ctk.CTkLabel(win, text="📱 THÔNG TIN KHÁCH HÀNG (Tùy chọn)",
                     font=("Arial", 12, "bold")).pack(pady=(15, 10), padx=30)
        ctk.CTkLabel(win, text="Tên khách hàng:").pack(anchor="w", padx=30)
        entry_ten_kh = ctk.CTkEntry(win, placeholder_text="Nhập tên khách hàng",
                                    width=350, height=35)
        entry_ten_kh.pack(pady=5, padx=30)
        ctk.CTkLabel(win, text="Số điện thoại:").pack(anchor="w", padx=30)
        entry_sdt = ctk.CTkEntry(win, placeholder_text="Nhập số điện thoại",
                                 width=350, height=35)
        entry_sdt.pack(pady=5, padx=30)
        ctk.CTkLabel(win, text="Email:").pack(anchor="w", padx=30)
        entry_email = ctk.CTkEntry(win, placeholder_text="Nhập email (không bắt buộc)",
                                   width=350, height=35)
        entry_email.pack(pady=5, padx=30)
        ctk.CTkLabel(win, text="Địa chỉ:").pack(anchor="w", padx=30)
        entry_dia_chi = ctk.CTkEntry(win, placeholder_text="Nhập địa chỉ (không bắt buộc)",
                                     width=350, height=35)
        entry_dia_chi.pack(pady=5, padx=30)
        # ===== NÚT LƯU VÀ HỦY =====
        def them_ban():
            ten_ban = entry_ten_ban.get().strip()
            loai_ban = loai_ban_var.get()
            if ten_ban == "":
                messagebox.showerror("Lỗi", "Tên bàn không được để trống!")
                return
            try:
                # Kiểm tra bàn đã tồn tại chưa
                self.cursor.execute("SELECT MaBan FROM ban WHERE MaBan = %s", (ten_ban,))
                if self.cursor.fetchone():
                    messagebox.showerror("Lỗi", f"Bàn '{ten_ban}' đã tồn tại!")
                    return
                # Thêm bàn
                sql_ban = "INSERT INTO ban (MaBan, LoaiBan, TrangThai) VALUES (%s, %s, 'Trống')"
                self.cursor.execute(sql_ban, (ten_ban, loai_ban))
                self.conn.commit()
                # Kiểm tra có thêm khách hàng không
                ten_kh = entry_ten_kh.get().strip()
                sdt = entry_sdt.get().strip()
                email = entry_email.get().strip()
                dia_chi = entry_dia_chi.get().strip()
                ma_kh = None
                if ten_kh and sdt:  # Nếu có tên và SDT
                    try:
                        # Kiểm tra khách hàng đã tồn tại
                        self.cursor.execute("SELECT MaKhachHang FROM khachhang WHERE SoDienThoai = %s", (sdt,))
                        result = self.cursor.fetchone()
                        if result:
                            ma_kh = result[0]
                            messagebox.showinfo("ℹ️ Thông báo",
                                                f"Khách hàng với SDT {sdt} đã tồn tại!\nSử dụng thông tin khách cũ.")
                        else:
                            # Thêm khách hàng mới
                            sql_kh = """INSERT INTO khachhang (TenKhachHang, SoDienThoai, Email, DiaChi)
                                       VALUES (%s, %s, %s, %s)"""
                            self.cursor.execute(sql_kh, (ten_kh, sdt, email or None, dia_chi or None))
                            self.conn.commit()
                            # Lấy ID khách hàng vừa thêm
                            ma_kh = self.cursor.lastrowid
                            messagebox.showinfo("✅ Thành công",
                                                f"Đã tạo bàn: {ten_ban}\nLoại: {loai_ban}\n\n"
                                                f"Khách hàng: {ten_kh}\nSDT: {sdt}")
                    except mysql.connector.Error as err:
                        messagebox.showwarning("⚠️ Cảnh báo",
                                               f"Tạo bàn thành công nhưng lỗi thêm khách hàng!\n\nLỗi: {err}")
                else:
                    if ten_kh or sdt:  # Nếu chỉ nhập một cái
                        messagebox.showwarning("⚠️ Cảnh báo",
                                               "Để thêm khách hàng, bạn cần nhập cả Tên và Số điện thoại!\n"
                                               "Nếu không, để trống cả hai trường.")
                    messagebox.showinfo("✅ Thành công", f"Đã tạo bàn mới: {ten_ban}\nLoại: {loai_ban}")
                self.load_ban()
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi database", f"Không thể thêm bàn: {err}")
        # ===== FRAME CHỨA CÁC NÚT =====
        button_frame = ctk.CTkFrame(win)
        button_frame.pack(pady=20)
        # Nút Lưu (màu xanh dương)
        ctk.CTkButton(button_frame,
                      text="✅ Lưu thông tin",
                      width=160,
                      height=45,
                      font=("Arial", 14, "bold"),
                      fg_color="#1E90FF",
                      hover_color="#1873CC",
                      command=them_ban).pack(side="left", padx=10)
        # Nút Hủy (màu xám)
        ctk.CTkButton(button_frame,
                      text="❌ Hủy",
                      width=160,
                      height=45,
                      font=("Arial", 14, "bold"),
                      fg_color="gray",
                      hover_color="#666666",
                      command=win.destroy).pack(side="left", padx=10)

    def get_danhmuc(self):
        try:
            self.cursor.execute("SELECT TenDanhMuc FROM danhmuc")
            return ["Tất cả"] + [row[0] for row in self.cursor.fetchall()]
        except:
            return ["Tất cả"]

    def load_ban(self):
        try:
            self.list_ban.delete(0, tk.END)
            self.cursor.execute("SELECT MaBan, TrangThai FROM ban ORDER BY MaBan")
            for row in self.cursor.fetchall():
                status = "🟢 Trống" if row[1] == "Trống" else "🔴 Có khách" if "khách" in row[
                    1].lower() else "🟡 Đặt trước"
                self.list_ban.insert(tk.END, f"{row[0]} - {status}")
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không load được danh sách bàn: {err}")

    def chon_ban(self, event):
        sel = self.list_ban.curselection()
        if not sel:
            return
        ban = self.list_ban.get(sel[0]).split(" - ")[0]
        self.selected_ban = ban
        self.lbl_ban_chon.configure(text=f"✅ {ban}", text_color="green")

    def load_mon(self):
        try:
            for i in self.tree_mon.get_children():
                self.tree_mon.delete(i)
            sql = "SELECT MaMon, TenMon, DonGia, TrangThai FROM mon"
            self.cursor.execute(sql)
            for row in self.cursor.fetchall():
                self.tree_mon.insert("", "end",
                                     values=(row[0], row[1], f"{row[2]:,.0f}đ", row[3]))
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không load được danh sách món: {err}")

    def load_mon_theo_danhmuc(self, danhmuc):
        try:
            for i in self.tree_mon.get_children():
                self.tree_mon.delete(i)
            if danhmuc == "Tất cả":
                self.load_mon()
            else:
                sql = """SELECT m.MaMon, m.TenMon, m.DonGia, m.TrangThai
                         FROM mon m JOIN danhmuc d ON m.MaDanhMuc = d.MaDanhMuc
                         WHERE d.TenDanhMuc = %s"""
                self.cursor.execute(sql, (danhmuc,))
                for row in self.cursor.fetchall():
                    self.tree_mon.insert("", "end",
                                         values=(row[0], row[1], f"{row[2]:,.0f}đ", row[3]))
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không lọc được món: {err}")

    def them_mon(self):
        if not self.selected_ban:
            messagebox.showwarning("⚠️ Chọn bàn", "Vui lòng chọn bàn trước!")
            return
        sel = self.tree_mon.selection()
        if not sel:
            messagebox.showwarning("⚠️ Chọn món", "Vui lòng chọn món cần thêm!")
            return
        item = self.tree_mon.item(sel[0])
        values = item['values']
        try:
            sl = int(self.entry_sl.get())
            if sl <= 0:
                raise ValueError
        except:
            messagebox.showerror("Lỗi", "Số lượng không hợp lệ!")
            return

        ma_mon = values[0]
        ten_mon = values[1]
        don_gia = int(values[2].replace("đ", "").replace(",", ""))
        thanh_tien = don_gia * sl
        thoi_gian = datetime.now().strftime("%H:%M:%S")

        self.tree_order.insert("", "end",
                               values=(ma_mon, ten_mon, f"{don_gia:,.0f}đ", sl, f"{thanh_tien:,.0f}đ"),
                               tags=(thoi_gian,))
        self.cap_nhat_tong_tien()
        messagebox.showinfo("✅ Thành công", f"Đã thêm {ten_mon} x{sl} lúc {thoi_gian}")

    def cap_nhat_tong_tien(self):
        tong = 0
        for item in self.tree_order.get_children():
            values = self.tree_order.item(item)['values']
            thanh_tien = int(values[4].replace("đ", "").replace(",", ""))
            tong += thanh_tien
        self.lbl_tong.configure(text=f"TỔNG: {tong:,.0f} VNĐ")

    def thanh_toan(self):
        if not self.selected_ban:
            messagebox.showwarning("Lỗi", "Chưa chọn bàn!")
            return
        if not self.tree_order.get_children():
            messagebox.showwarning("Lỗi", "Chưa có món nào trong order!")
            return

        tong_text = self.lbl_tong.cget("text")
        tong = int(tong_text.replace("TỔNG: ", "").replace(" VNĐ", "").replace(",", ""))

        if messagebox.askyesno("Xác nhận thanh toán",
                               f"Thanh toán bàn {self.selected_ban}\nTổng tiền: {tong:,.0f} VNĐ"):
            try:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "INSERT INTO hoadon (MaBan, TongTien, NgayGio) VALUES (%s, %s, %s)"
                self.cursor.execute(sql, (self.selected_ban, tong, now))
                self.conn.commit()

                messagebox.showinfo("✅ Thanh toán thành công", f"Đã thanh toán {tong:,.0f} VNĐ")
                self.tree_order.delete(*self.tree_order.get_children())
                self.cap_nhat_tong_tien()
                self.load_ban()

                if self.tree_thong_ke_ref and self.lbl_tong_all_ref:
                    self.load_thong_ke(self.tree_thong_ke_ref)

            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi", f"Không thể thanh toán: {err}")

    def in_hoa_don(self):
        if not self.tree_order.get_children():
            messagebox.showwarning("Lỗi", "Chưa có món nào để in!")
            return
        print("===== HÓA ĐƠN CAFE NỢ QÌ =====")
        print(f"Bàn: {self.selected_ban} - Ngày: {datetime.now()}")
        print("{:<5} {:<20} {:<10} {:<5} {:<10}".format("Mã", "Tên món", "Đơn giá", "SL", "Thành tiền"))
        for item in self.tree_order.get_children():
            v = self.tree_order.item(item)['values']
            print("{:<5} {:<20} {:<10} {:<5} {:<10}".format(*v))
        print(f"TỔNG: {self.lbl_tong.cget('text')}")
        print("==============================")

    def show_them_mon_moi(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Thêm món mới")
        win.geometry("400x400")
        ctk.CTkLabel(win, text="THÊM MÓN MỚI", font=("Arial", 20, "bold")).pack(pady=15)
        ctk.CTkLabel(win, text="Tên món:").pack()
        entry_ten = ctk.CTkEntry(win, width=300)
        entry_ten.pack(pady=5)
        ctk.CTkLabel(win, text="Giá tiền:").pack()
        entry_gia = ctk.CTkEntry(win, width=300)
        entry_gia.pack(pady=5)
        ctk.CTkLabel(win, text="Danh mục:").pack()
        cb_dm = ctk.CTkComboBox(win, values=self.get_danhmuc())
        cb_dm.pack(pady=5)
        cb_dm.set("Tất cả")
        ctk.CTkLabel(win, text="Trạng thái:").pack()
        cb_tt = ctk.CTkComboBox(win, values=["Sẵn sàng", "Hết hàng"])
        cb_tt.pack(pady=5)
        cb_tt.set("Sẵn sàng")

        def them_mon_moi():
            ten = entry_ten.get().strip()
            try:
                gia = int(entry_gia.get())
            except:
                messagebox.showerror("Lỗi", "Giá tiền không hợp lệ!")
                return
            dm = cb_dm.get()
            tt = cb_tt.get()
            if not ten or dm == "Tất cả":
                messagebox.showerror("Lỗi", "Chưa nhập tên hoặc chọn danh mục!")
                return
            try:
                self.cursor.execute("SELECT MaDanhMuc FROM danhmuc WHERE TenDanhMuc=%s", (dm,))
                ma_dm = self.cursor.fetchone()[0]
                sql = "INSERT INTO mon (TenMon, DonGia, MaDanhMuc, TrangThai) VALUES (%s, %s, %s, %s)"
                self.cursor.execute(sql, (ten, gia, ma_dm, tt))
                self.conn.commit()
                messagebox.showinfo("✅ Thành công", f"Đã thêm món: {ten}")
                self.load_mon()
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi", f"Không thêm được món: {err}")

        ctk.CTkButton(win, text="Lưu", fg_color="#1E90FF", command=them_mon_moi).pack(pady=20)

if __name__ == "__main__":
    app = CafeApp()