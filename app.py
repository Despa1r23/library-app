import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime
import platform

# Настройка стилей
def setup_styles():
    style = ttk.Style()
    
    # Современная тема
    style.theme_use('clam')
    
    # Настраиваем цвета
    style.configure('TFrame', background='#f0f8ff')
    style.configure('TLabel', background='#f0f8ff', font=('Arial', 10))
    style.configure('TButton', font=('Arial', 9), padding=6)
    style.configure('Treeview', font=('Arial', 9), rowheight=25)
    style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    style.configure('Accent.TButton', background='#3498db', foreground='white')
    style.configure('Card.TFrame', background='#ffffff', relief='raised', borderwidth=1)
    
    return style

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Моя библиотека")
        
        # Получаем размер экрана для Linux
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Устанавливаем размер окна почти на весь экран (с небольшими отступами)
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.85)
        
        # Центрируем окно
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#f0f8ff')
        
        # Настраиваем стили
        self.style = setup_styles()
        
        # Подключаемся к базе данных
        self.db = Database()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Загружаем книги
        self.load_books()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        
        # Главный контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame, padding="20")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                              text="📖 Моя библиотека", 
                              font=('Arial', 20, 'bold'),
                              foreground='#2c3e50')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame,
                                 text="Управляйте своей коллекцией книг",
                                 font=('Arial', 12),
                                 foreground='#7f8c8d')
        subtitle_label.pack()
        
        # Фрейм для добавления новой книги
        add_frame = ttk.Frame(main_frame, padding="15", style='Card.TFrame')
        add_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(add_frame, text="✍️ Автор:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.author_entry = ttk.Entry(add_frame, width=30, font=('Arial', 10))
        self.author_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="📖 Название:", font=('Arial', 10)).grid(row=0, column=2, sticky=tk.W, padx=20)
        self.title_entry = ttk.Entry(add_frame, width=30, font=('Arial', 10))
        self.title_entry.grid(row=0, column=3, padx=5)
        
        self.add_button = ttk.Button(add_frame, 
                                   text="➕ Добавить книгу", 
                                   command=self.add_book,
                                   style='Accent.TButton')
        self.add_button.grid(row=0, column=4, padx=15)
        
        # Фрейм для списка книг
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Таблица для отображения книг
        columns = ("ID", "Автор", "Название", "Статус", "Дата прочтения", "Дата добавления")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Настраиваем заголовки
        self.tree.heading("ID", text="📋 ID")
        self.tree.heading("Автор", text="👤 Автор")
        self.tree.heading("Название", text="📚 Название")
        self.tree.heading("Статус", text="✅ Статус")
        self.tree.heading("Дата прочтения", text="📅 Дата прочтения")
        self.tree.heading("Дата добавления", text="⏰ Дата добавления")
        
        # Настраиваем ширину колонок
        self.tree.column("ID", width=60, anchor=tk.CENTER)
        self.tree.column("Автор", width=200)
        self.tree.column("Название", width=300)
        self.tree.column("Статус", width=150, anchor=tk.CENTER)
        self.tree.column("Дата прочтения", width=120, anchor=tk.CENTER)
        self.tree.column("Дата добавления", width=120, anchor=tk.CENTER)
        
        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Фрейм для кнопок управления
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.mark_read_button = ttk.Button(
            button_frame, 
            text="✅ Отметить как прочитанную", 
            command=lambda: self.change_read_status(True),
            width=25
        )
        self.mark_read_button.pack(side=tk.LEFT, padx=5)
        
        self.mark_unread_button = ttk.Button(
            button_frame, 
            text="⏳ Хочу прочитать",
            command=lambda: self.change_read_status(False),
            width=20
        )
        self.mark_unread_button.pack(side=tk.LEFT, padx=5)
        
        self.update_date_button = ttk.Button(
            button_frame, 
            text="📅 Изменить дату прочтения", 
            command=self.open_date_dialog,
            width=25
        )
        self.update_date_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = ttk.Button(
            button_frame, 
            text="🔄 Обновить список", 
            command=self.load_books,
            width=20
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        self.status_frame = ttk.Frame(main_frame, padding="10")
        self.status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(self.status_frame, text="Готов к работе", 
                                    font=('Arial', 9), foreground='#666666')
        self.status_label.pack()
    
    def add_book(self):
        """Добавление новой книги"""
        author = self.author_entry.get().strip()
        title = self.title_entry.get().strip()
        
        if not author or not title:
            messagebox.showerror("Ошибка", "Заполните поля автора и названия")
            return
        
        if self.db.add_book(author, title):
            messagebox.showinfo("Успех", "Книга добавлена успешно!")
            self.author_entry.delete(0, tk.END)
            self.title_entry.delete(0, tk.END)
            self.load_books()
            self.status_label.config(text=f"Книга '{title}' добавлена успешно")
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить книгу")
            self.status_label.config(text="Ошибка при добавлении книги")
    
    def load_books(self):
        """Загрузка и отображение списка книг"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        books = self.db.get_all_books()
        for book in books:
            book_id, author, title, is_read, date_read, created_at = book
            
            status = "✅ Прочитана" if is_read else "⏳ Хочу прочитать"
            date_read_str = date_read.strftime("%d.%m.%Y") if date_read else ""
            created_str = created_at.strftime("%d.%m.%Y") if created_at else ""
            
            self.tree.insert("", tk.END, values=(
                book_id, author, title, status, date_read_str, created_str
            ))
        
        self.status_label.config(text=f"Загружено книг: {len(books)}")
    
    def change_read_status(self, is_read):
        """Изменение статуса прочтения книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу из списка")
            return
        
        item = selected[0]
        book_id = self.tree.item(item)['values'][0]
        title = self.tree.item(item)['values'][2]
        
        if self.db.mark_as_read(book_id, is_read):
            status = "прочитанной" if is_read else "хочу прочитать"
            messagebox.showinfo("Успех", f"Книга '{title}' отмечена как {status}")
            self.load_books()
            self.status_label.config(text=f"Статус книги '{title}' изменен")
        else:
            messagebox.showerror("Ошибка", "Не удалось изменить статус книги")
            self.status_label.config(text="Ошибка при изменении статуса")
    
    def open_date_dialog(self):
        """Открыть диалог для изменения даты прочтения"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу из списка")
            return
        
        item = selected[0]
        book_id = self.tree.item(item)['values'][0]
        author = self.tree.item(item)['values'][1]
        title = self.tree.item(item)['values'][2]
        
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменение даты прочтения")
        dialog.geometry("400x200")
        dialog.configure(bg='#f0f8ff')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрируем диалог
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text=f"📚 Книга: {author}", 
                 font=('Arial', 11, 'bold')).pack(pady=10)
        ttk.Label(dialog, text=f"'{title}'", 
                 font=('Arial', 10)).pack(pady=2)
        ttk.Label(dialog, text="📅 Новая дата прочтения (ГГГГ-ММ-ДД):", 
                 font=('Arial', 10)).pack(pady=8)
        
        # Поле для ввода даты
        date_entry = ttk.Entry(dialog, font=('Arial', 10), width=15, justify=tk.CENTER)
        date_entry.pack(pady=5)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def apply_date():
            new_date = date_entry.get().strip()
            if not new_date:
                messagebox.showerror("Ошибка", "Введите дату")
                return
            
            try:
                datetime.strptime(new_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД\nНапример: 2025-08-25")
                return
            
            if self.db.update_read_date(book_id, new_date):
                messagebox.showinfo("Успех", "Дата прочтения обновлена!")
                dialog.destroy()
                self.load_books()
                self.status_label.config(text=f"Дата прочтения книги '{title}' обновлена")
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить дату")
        
        ttk.Button(button_frame, text="💾 Применить", command=apply_date, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Отмена", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=5)
        
        date_entry.focus()
        date_entry.select_range(0, tk.END)
    
    def __del__(self):
        """Закрываем соединение с БД при закрытии приложения"""
        if hasattr(self, 'db'):
            self.db.close()

def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
