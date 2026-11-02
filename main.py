"""Affiliate management application for Caja de Compensacion Compensandote.

Linear data structures: Stack (LIFO), Queue (FIFO), and List.
All identifiers and source-code messages are written in English.
The graphical interface is presented in Spanish to match the assignment.

Dependency: pip install tkcalendar
"""

import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from datetime import date

try:
    from tkcalendar import DateEntry
except ImportError as exc:
    raise SystemExit(
        "Missing dependency 'tkcalendar'. Install it with: python -m pip install tkcalendar"
    ) from exc


STUDENT_NAME = "Efren Ubaldo Fuentes Mosquera"
COURSE_NAME = "Estructura de Datos - 301305"
COLLABORATIVE_GROUP = "301305_19"
LOGIN_PASSWORD = "Caja"

ID_TYPES = ["CC", "CE", "NUIP", "PAS"]
SERVICES = [
    "Subsidio de desempleo",
    "Ingreso a parque",
    "Curso de formación",
    "Paquete de viaje",
    "Medicina preventiva",
]
EMPLOYMENT_TYPES = ["Empleado", "Independiente"]
STRUCTURES = ["Pila", "Cola", "Lista"]

# The ranges follow the assignment's thresholds:
# 1,000,000 <= income <= 2,000,000; then (2,000,000, 3,000,000], etc.
# Income above 5,000,000 belongs to the final range.
EMPLOYEE_TARIFF_TABLE = [
    (1_000_000, 2_000_000, 45_000),
    (2_000_000, 3_000_000, 60_000),
    (3_000_000, 4_000_000, 75_000),
    (4_000_000, 5_000_000, 90_000),
    (5_000_000, float("inf"), 150_000),
]

INDEPENDENT_TARIFF_TABLE = [
    (1_000_000, 2_000_000, 10_000),
    (2_000_000, 3_000_000, 20_000),
    (3_000_000, 4_000_000, 30_000),
    (4_000_000, 5_000_000, 40_000),
    (5_000_000, float("inf"), 80_000),
]

SERVICE_SURCHARGES = {
    "Subsidio de desempleo": ("fixed", 0),
    "Ingreso a parque": ("fixed", 2_500),
    "Curso de formación": ("fixed", 7_500),
    "Paquete de viaje": ("fixed", 10_000),
    "Medicina preventiva": ("percent", 0.10),
}


def calculate_base_tariff(income, employment_type):
    """Return the base tariff for a valid income and employment type."""
    if income < 1_000_000:
        raise ValueError("Los ingresos deben ser iguales o superiores a $1.000.000.")

    if employment_type == "Empleado":
        tariff_table = EMPLOYEE_TARIFF_TABLE
    elif employment_type == "Independiente":
        tariff_table = INDEPENDENT_TARIFF_TABLE
    else:
        raise ValueError("La modalidad de empleo no es válida.")

    for lower_bound, upper_bound, tariff in tariff_table:
        if lower_bound <= income <= upper_bound:
            # A shared boundary belongs to the lower range. For example,
            # exactly $2,000,000 must receive the first range's tariff.
            if income == lower_bound and lower_bound > 1_000_000:
                continue
            return tariff

    # The final range is strictly greater than $5,000,000.
    if income > 5_000_000:
        return tariff_table[-1][2]

    raise ValueError("No existe una tarifa para los ingresos indicados.")


def calculate_tariff(income, employment_type, desired_service):
    """Calculate the affiliation tariff, including the selected service surcharge."""
    base_tariff = calculate_base_tariff(income, employment_type)
    try:
        surcharge_type, surcharge_value = SERVICE_SURCHARGES[desired_service]
    except KeyError as exc:
        raise ValueError("El servicio seleccionado no es válido.") from exc

    if surcharge_type == "fixed":
        return base_tariff + surcharge_value
    return base_tariff + income * surcharge_value


class Affiliate:
    """Data model for one affiliate."""

    def __init__(self, id_type, id_number, full_name, income,
                 desired_service, employment_type, tariff, affiliation_date):
        self.id_type = id_type
        self.id_number = id_number
        self.full_name = full_name
        self.income = income
        self.desired_service = desired_service
        self.employment_type = employment_type
        self.tariff = tariff
        self.affiliation_date = affiliation_date

    def as_row(self):
        return (
            self.id_type,
            self.id_number,
            self.full_name,
            f"${self.income:,.0f}",
            self.desired_service,
            self.employment_type,
            f"${self.tariff:,.0f}",
            self.affiliation_date,
        )


class AffiliateStack:
    """Stack implementation using list (LIFO)."""

    def __init__(self):
        self.items = []

    def push(self, affiliate):
        self.items.append(affiliate)

    def pop(self):
        return self.items.pop() if self.items else None

    def is_empty(self):
        return not self.items

    def total_tariff(self):
        return sum(affiliate.tariff for affiliate in self.items)


class AffiliateQueue:
    """Queue implementation using collections.deque (FIFO)."""

    def __init__(self):
        self.items = deque()

    def enqueue(self, affiliate):
        self.items.append(affiliate)

    def dequeue(self):
        return self.items.popleft() if self.items else None

    def is_empty(self):
        return not self.items

    def count(self):
        return len(self.items)


class AffiliateList:
    """List implementation using Python list."""

    def __init__(self):
        self.items = []

    def add_last(self, affiliate):
        self.items.append(affiliate)

    def find_by_id(self, id_number):
        for affiliate in self.items:
            if affiliate.id_number == id_number:
                return affiliate
        return None

    def remove_by_id(self, id_number):
        affiliate = self.find_by_id(id_number)
        if affiliate is not None:
            self.items.remove(affiliate)
        return affiliate

    def average_income(self):
        if not self.items:
            return 0
        return sum(affiliate.income for affiliate in self.items) / len(self.items)


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Compensándote")
        self.geometry("430x270")
        self.resizable(False, False)

        menu_bar = tk.Menu(self)
        menu_bar.add_command(label="Acerca de", command=self.show_about)
        self.config(menu=menu_bar)

        tk.Label(self, text="Compensándote", font=("Segoe UI", 19, "bold")).pack(pady=(24, 6))
        tk.Label(self, text="Sistema de control de afiliaciones").pack(pady=(0, 22))
        tk.Label(self, text="Contraseña").pack()

        self.password_entry = tk.Entry(self, show="*", width=30)
        self.password_entry.pack(pady=(5, 20))
        self.password_entry.bind("<Return>", lambda event: self.validate_login())

        buttons_frame = tk.Frame(self)
        buttons_frame.pack()
        tk.Button(buttons_frame, text="Ingresar", width=12,
                  command=self.validate_login).grid(row=0, column=0, padx=8)
        tk.Button(buttons_frame, text="Salir", width=12,
                  command=self.destroy).grid(row=0, column=1, padx=8)

    def show_about(self):
        information = (
            f"Curso: {COURSE_NAME}\n"
            f"Estudiante: {STUDENT_NAME}\n"
            f"Grupo colaborativo: {COLLABORATIVE_GROUP}"
        )
        messagebox.showinfo("Acerca de", information)

    def validate_login(self):
        if self.password_entry.get() == LOGIN_PASSWORD:
            self.destroy()
            application = MainWindow()
            application.mainloop()
        else:
            messagebox.showerror("Inicio de sesión", "La contraseña es incorrecta.")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Caja Compensándote - Control de Afiliados")
        self.geometry("1180x650")
        self.minsize(1050, 600)

        self.stack = AffiliateStack()
        self.queue = AffiliateQueue()
        self.linked_list = AffiliateList()

        self.build_form()
        self.build_table()
        self.refresh_treeview()

    def build_form(self):
        form = tk.Frame(self, padx=14, pady=12)
        form.pack(side="left", fill="y")

        tk.Label(form, text="Tipo de identificación").grid(row=0, column=0, sticky="w")
        self.id_type_var = tk.StringVar(value=ID_TYPES[0])
        ttk.Combobox(form, textvariable=self.id_type_var, values=ID_TYPES,
                     state="readonly", width=23).grid(row=0, column=1, pady=4)

        tk.Label(form, text="Número de identificación").grid(row=1, column=0, sticky="w")
        self.id_number_entry = tk.Entry(form, width=26)
        self.id_number_entry.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Nombre completo").grid(row=2, column=0, sticky="w")
        self.full_name_entry = tk.Entry(form, width=26)
        self.full_name_entry.grid(row=2, column=1, pady=4)

        tk.Label(form, text="Ingresos actuales ($)").grid(row=3, column=0, sticky="w")
        self.income_entry = tk.Entry(form, width=26)
        self.income_entry.grid(row=3, column=1, pady=4)
        self.income_entry.bind("<KeyRelease>", lambda event: self.calculate_tariff_field())

        tk.Label(form, text="Servicio deseado").grid(row=4, column=0, sticky="w")
        self.service_var = tk.StringVar(value=SERVICES[0])
        service_box = ttk.Combobox(form, textvariable=self.service_var, values=SERVICES,
                                   state="readonly", width=23)
        service_box.grid(row=4, column=1, pady=4)
        service_box.bind("<<ComboboxSelected>>", lambda event: self.calculate_tariff_field())

        tk.Label(form, text="Modalidad de empleo").grid(row=5, column=0, sticky="w")
        self.employment_var = tk.StringVar(value=EMPLOYMENT_TYPES[0])
        employment_frame = tk.Frame(form)
        employment_frame.grid(row=5, column=1, sticky="w")
        tk.Radiobutton(employment_frame, text="Empleado", variable=self.employment_var,
                       value="Empleado", command=self.calculate_tariff_field).pack(side="left")
        tk.Radiobutton(employment_frame, text="Independiente", variable=self.employment_var,
                       value="Independiente", command=self.calculate_tariff_field).pack(side="left")

        tk.Label(form, text="Tarifa de afiliación ($)").grid(row=6, column=0, sticky="w")
        self.tariff_entry = tk.Entry(form, width=26, state="readonly")
        self.tariff_entry.grid(row=6, column=1, pady=4)

        tk.Label(form, text="Fecha de afiliación").grid(row=7, column=0, sticky="w", pady=(10, 0))
        self.date_entry = DateEntry(form, width=23, date_pattern="dd/mm/yyyy",
                                    locale="es_ES", year=date.today().year)
        self.date_entry.grid(row=7, column=1, pady=4, sticky="w")

        tk.Label(form, text="Ver estructura").grid(row=8, column=0, sticky="w", pady=(10, 0))
        self.structure_var = tk.StringVar(value=STRUCTURES[0])
        structure_box = ttk.Combobox(form, textvariable=self.structure_var,
                                     values=STRUCTURES, state="readonly", width=23)
        structure_box.grid(row=8, column=1, pady=4)
        structure_box.bind("<<ComboboxSelected>>", lambda event: self.on_structure_changed())

        tk.Label(form, text="Reporte").grid(row=9, column=0, sticky="w", pady=(10, 0))
        self.report_entry = tk.Entry(form, width=32, state="readonly")
        self.report_entry.grid(row=10, column=0, columnspan=2, pady=4, sticky="w")

        buttons_frame = tk.Frame(form)
        buttons_frame.grid(row=11, column=0, columnspan=2, pady=18)
        tk.Button(buttons_frame, text="Registrar", width=13,
                  command=self.register_affiliate).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(buttons_frame, text="Eliminar", width=13,
                  command=self.delete_affiliate).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(buttons_frame, text="Reporte", width=13,
                  command=self.show_report).grid(row=1, column=0, padx=4, pady=4)
        tk.Button(buttons_frame, text="Limpiar", width=13,
                  command=self.clear_form).grid(row=1, column=1, padx=4, pady=4)
        tk.Button(buttons_frame, text="Salir", width=29,
                  command=self.destroy).grid(row=2, column=0, columnspan=2, padx=4, pady=4)

    def build_table(self):
        table_frame = tk.Frame(self, padx=10, pady=12)
        table_frame.pack(side="right", fill="both", expand=True)

        columns = ("id_type", "id_number", "full_name", "income", "service",
                   "employment", "tariff", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headers = ("Tipo ID", "Número ID", "Nombre completo", "Ingresos", "Servicio",
                   "Empleo", "Tarifa", "Fecha")
        widths = (65, 100, 155, 100, 145, 95, 100, 90)

        for column, header, width in zip(columns, headers, widths):
            self.tree.heading(column, text=header)
            self.tree.column(column, width=width, anchor="center")

        vertical_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        horizontal_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical_scroll.set,
                            xscrollcommand=horizontal_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    def calculate_tariff_field(self):
        income_text = self.income_entry.get().strip()
        if not income_text.isdigit():
            self.set_readonly_entry(self.tariff_entry, "")
            return

        income = int(income_text)
        try:
            tariff = calculate_tariff(income, self.employment_var.get(), self.service_var.get())
        except ValueError:
            self.set_readonly_entry(self.tariff_entry, "")
            return
        self.set_readonly_entry(self.tariff_entry, f"{tariff:.0f}")

    @staticmethod
    def set_readonly_entry(entry, value):
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)
        entry.config(state="readonly")

    def validate_fields(self):
        id_number = self.id_number_entry.get().strip()
        full_name = self.full_name_entry.get().strip()
        income_text = self.income_entry.get().strip()

        if not id_number or not id_number.isdigit():
            messagebox.showerror("Validación", "El número de identificación debe contener solo números.")
            return None

        # Accept Unicode letters (including accents), spaces, hyphens and apostrophes.
        normalized_name = full_name.replace(" ", "").replace("-", "").replace("'", "").replace("’", "")
        if not full_name or not normalized_name.isalpha():
            messagebox.showerror("Validación", "El nombre debe contener únicamente letras y separadores válidos.")
            return None

        if not income_text.isdigit():
            messagebox.showerror("Validación", "Los ingresos deben contener solo números enteros.")
            return None

        income = int(income_text)
        if income < 1_000_000:
            messagebox.showerror("Validación", "Los ingresos deben ser iguales o superiores a $1.000.000.")
            return None

        try:
            tariff = calculate_tariff(income, self.employment_var.get(), self.service_var.get())
            affiliation_date = self.date_entry.get_date().strftime("%d/%m/%Y")
        except (ValueError, KeyError) as error:
            messagebox.showerror("Validación", str(error))
            return None

        return Affiliate(
            self.id_type_var.get(), id_number, full_name, income,
            self.service_var.get(), self.employment_var.get(), tariff, affiliation_date
        )

    def get_selected_items(self):
        structure = self.structure_var.get()
        if structure == "Pila":
            return self.stack.items
        if structure == "Cola":
            return self.queue.items
        return self.linked_list.items

    def register_affiliate(self):
        affiliate = self.validate_fields()
        if affiliate is None:
            return

        structure = self.structure_var.get()
        if structure == "Pila":
            self.stack.push(affiliate)
        elif structure == "Cola":
            self.queue.enqueue(affiliate)
        else:
            self.linked_list.add_last(affiliate)

        self.refresh_treeview()
        messagebox.showinfo("Registro", "Afiliado registrado correctamente.")

    def delete_affiliate(self):
        structure = self.structure_var.get()

        if structure == "Pila":
            if self.stack.is_empty():
                messagebox.showwarning("Eliminar", "La pila está vacía.")
                return
            if messagebox.askyesno("Confirmar eliminación", "¿Desea desapilar el último afiliado registrado?"):
                self.stack.pop()

        elif structure == "Cola":
            if self.queue.is_empty():
                messagebox.showwarning("Eliminar", "La cola está vacía.")
                return
            if messagebox.askyesno("Confirmar eliminación", "¿Desea desencolar el primer afiliado registrado?"):
                self.queue.dequeue()

        else:
            id_number = self.id_number_entry.get().strip()
            if not id_number or not id_number.isdigit():
                messagebox.showwarning("Eliminar", "Ingrese un número de identificación válido.")
                return
            affiliate = self.linked_list.find_by_id(id_number)
            if affiliate is None:
                messagebox.showwarning("Eliminar", "No se encontró el afiliado en la lista.")
                return
            if messagebox.askyesno("Confirmar eliminación", f"¿Desea eliminar a {affiliate.full_name}?"):
                self.linked_list.remove_by_id(id_number)

        self.refresh_treeview()
        self.set_readonly_entry(self.report_entry, "")

    def show_report(self):
        structure = self.structure_var.get()
        if structure == "Pila":
            report = f"Suma de tarifas: ${self.stack.total_tariff():,.0f}"
        elif structure == "Cola":
            report = f"Cantidad de afiliados: {self.queue.count()}"
        else:
            report = f"Promedio de ingresos: ${self.linked_list.average_income():,.0f}"

        self.set_readonly_entry(self.report_entry, report)

    def clear_form(self):
        """Clear input fields without modifying any data structure."""
        self.id_number_entry.delete(0, tk.END)
        self.full_name_entry.delete(0, tk.END)
        self.income_entry.delete(0, tk.END)
        self.set_readonly_entry(self.tariff_entry, "")
        self.set_readonly_entry(self.report_entry, "")
        self.id_type_var.set(ID_TYPES[0])
        self.service_var.set(SERVICES[0])
        self.employment_var.set(EMPLOYMENT_TYPES[0])
        self.date_entry.set_date(date.today())
        self.id_number_entry.focus_set()

    def on_structure_changed(self):
        self.refresh_treeview()
        self.set_readonly_entry(self.report_entry, "")

    def refresh_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for affiliate in self.get_selected_items():
            self.tree.insert("", tk.END, values=affiliate.as_row())


if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()
