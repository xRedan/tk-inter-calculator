# Data: 13/03/2026

from enum import Enum
import math
import tkinter as tk
from tkinter import ttk

# I possibili stati previsti.
class State(Enum):
    INIT = 0  # --> Stato iniziale, mostra "0".
    IN_N1 = 1  # --> Stato in cui si inserisce il primo numero.
    IN_OP = 2  # --> Stato in cui si é selezionato l'operatore.
    IN_N2 = 3  # --> Stato in cui si inserisce il secondo numero.
    RESULT = 4  # --> Stato in cui si mostra il risultato.
    ERROR = 5  # --> Stato per le operazioni non consentite.


# Utile a definire la tipologia di input ricevuta.
class InputType(Enum):
    DIGIT = 0  # --> Cifra numerica.
    BIN_OP = 1  # --> Operatore binario (+-/*^).
    UNA_OP = 2  # --> Operatore unario (√logsincos).
    EQ = 3  # --> Uguale.
    BACKSPACE = 4  # --> Cancella l'ultima cifra.
    CLEAR = 5  # --> Reset.


# Classe che gestisce tutta la logica della calcolatrice.
class Calcolatrice:
    def __init__(self):
        # Attributi per i numeri.
        self.n1 = 0.0
        self.n2 = 0.0
        self.result = 0.0

        self.op = ""
        self.buffer = "0"

        # Attributi per il log.
        self.n1_log = ""
        self.n2_log = ""
        self.error_log = ""

        self.state = State.INIT  # Attributo per la gestione degli stati.

    # Metodo dove risiede tutta la logica della calcolatrice.
    # Si base su un sistema di macchine a stati, e in base allo stato attuale
    # e all'input ricevuto si comporta di conseguenza.
    def process_input(self, input_type, value, operator=""):
        print(
            f"STATE:{self.state}, INPUT_TYPE:{input_type}, VALUE:{value}, OPERATOR:{operator}"
        )

        if input_type == InputType.CLEAR:
            self.reset()
            return
        match self.state:
            # Stato iniziale o dell'inserimento del primo numero.
            case State.INIT | State.IN_N1:
                match input_type:  # In base all'input ricevuto.
                    case InputType.DIGIT:
                        self.state = State.IN_N1
                        self.append_digit(value)
                    case InputType.BACKSPACE:
                        self.state = State.IN_N1
                        self.backspace()
                    case InputType.BIN_OP:
                        self.state = State.IN_OP
                        self.convert_buffer(1)
                        self.set_op(operator)
                    case InputType.UNA_OP:
                        self.state = State.RESULT
                        self.convert_buffer(1)
                        self.set_op(operator)
                        self.execute_unary(self.n1)
                    case InputType.EQ:
                        self.result = float(self.buffer)
            # Stato che riceve l'operatore.
            case State.IN_OP:
                match input_type:
                    case InputType.DIGIT:
                        self.state = State.IN_N2
                        self.clear_buffer()
                        self.append_digit(value)
                    case InputType.BIN_OP:
                        self.state = State.IN_OP
                        self.set_op(operator)
                    case InputType.UNA_OP:
                        self.state = State.IN_N2
                        new_op = self.op
                        self.convert_buffer(2)
                        self.n2_log = f"{operator}({self.n1_log})"
                        self.set_op(operator)
                        self.execute_unary(self.n1)
                        self.set_op(new_op)
                        self.append_digit(self.get_result())
                    case InputType.EQ:
                        self.state = State.RESULT
                        self.n2 = self.n1
                        self.execute_binary()
            # Stato dell'inserimento del secondo numero.
            case State.IN_N2:
                match input_type:
                    case InputType.DIGIT:
                        print("dentro in_2")
                        self.state = State.IN_N2
                        self.append_digit(value)
                    case InputType.BACKSPACE:
                        self.state = State.IN_N2
                        self.backspace()
                    case InputType.UNA_OP:
                        self.state = State.IN_N2
                        new_op = self.op
                        self.convert_buffer(2)
                        self.n2_log = f"{operator}({self.n2_log})"
                        self.set_op(operator)
                        self.execute_unary(self.n2)
                        self.set_op(new_op)
                        self.append_digit(self.get_result())
                    case InputType.BIN_OP:
                        self.state = State.IN_OP
                        self.convert_buffer(2)
                        self.execute_binary()
                        self.n1 = self.result
                        self.n1_log = f"{self.get_n1()}"
                        self.set_op(operator)
                    case InputType.EQ:
                        self.state = State.RESULT
                        self.convert_buffer(2)
                        self.execute_binary()
            # Stato che calcola il risultato.
            case State.RESULT:
                match input_type:
                    case InputType.DIGIT:
                        self.reset()
                        self.state = State.IN_N1
                        self.append_digit(value)
                    case InputType.BACKSPACE:
                        self.state = State.RESULT
                        self.n1_log = ""
                    case InputType.UNA_OP:
                        self.state = State.RESULT
                        self.n1 = self.result
                        self.n1_log = self.get_n1()
                        self.set_op(operator)
                        self.execute_unary(self.n1)
                    case InputType.BIN_OP:
                        print(f"dentro result value:{value}")
                        self.state = State.IN_OP
                        self.n1 = self.result
                        self.n1_log = self.get_n1()
                        self.set_op(operator)
                    case InputType.EQ:
                        print(f"value:{value}")
                        self.state = State.RESULT
                        self.buffer = value
                        self.convert_buffer(1)
                        self.repeat_result()
            # In caso operazioni non concesse.
            case State.ERROR:
                self.reset()
                if input_type == InputType.DIGIT:
                    self.state = State.IN_N1
                    self.append_digit(value)

    # Alla pressione dell'uguale ripete l'ultima operazione.
    def repeat_result(self):
        if self.op in "+-*/^":
            self.execute_binary()
        else:
            self.execute_unary(self.n1)

    # Esegue le operazioni binarie.
    def execute_binary(self):
        print(f"Operatore:{self.op}")
        try:
            match self.op:
                case "+":
                    self.result = self.n1 + self.n2
                    print(f"{self.n1}, {self.n2}, {self.result}")
                case "-":
                    self.result = self.n1 - self.n2
                case "*":
                    self.result = self.n1 * self.n2
                case "/":
                    self.result = self.n1 / self.n2
                case "^":
                    self.result = self.n1**self.n2
        except ZeroDivisionError:  # Divisione per zero.
            self.state = State.ERROR
            self.error_log = "Divisione per zero."
            print("Errore")
        except (OverflowError, ValueError):  # Overflow o input errato.
            self.state = State.ERROR
            self.error_log = "Input non valido."

    # Esegue le operazioni unarie.
    def execute_unary(self, value):
        print(f"Unary:{self.result}")
        try:
            match self.op:
                case "v":
                    self.result = math.sqrt(value)
                    print(f"Unary:{self.result}")
                case "log":
                    self.result = math.log10(value)
                case "sin":
                    self.result = math.sin(math.radians(value))
                case "cos":
                    self.result = math.cos(math.radians(value))
                case "tan":
                    self.result = math.tan(math.radians(value))
        except ZeroDivisionError:  # Divisione per zero.
            self.state = State.ERROR
            self.error_log = "Divisione per zero."
            print("Errore")
        except (OverflowError, ValueError):  # Overflow o input errato.
            self.state = State.ERROR
            self.error_log = "Input non valido."

    # Aggiunge un carattere al buffer oppure lo sovrascrive.
    def append_digit(self, digit):
        if digit == "." and "." in self.buffer:
            return
        if self.buffer == "0" and digit != ".":
            self.buffer = digit
            return
        self.buffer += digit

    # Cancella l'ultimo carattere nel buffer, se é l'ultimo resetta.
    def backspace(self):
        if len(self.buffer) == 1:
            self.buffer = "0"
        else:
            self.buffer = self.buffer[:-1]

    # Converte il buffer nel relativo numero (n1 o n2) in float.
    def convert_buffer(self, n):
        if n == 1:
            self.n1 = float(self.buffer)
            self.n1_log = self.get_n1()
        else:
            self.n2 = float(self.buffer)
            self.n2_log = self.get_n2()
        self.clear_buffer()

    def clear_buffer(self):
        self.buffer = "0"

    def set_op(self, operator):
        self.op = operator

    def get_n1(self):
        return f"{self.n1:g}"

    def get_n2(self):
        return f"{self.n2:g}"

    def get_result(self):
        return f"{self.result:g}"

    def get_display(self):
        if self.state == State.IN_OP:
            return self.get_n1()
        elif self.state == State.RESULT:
            return self.get_result()
        elif self.state == State.ERROR:
            return self.error_log
        else:
            return self.buffer

    # Ritorna un simbolo esteticamente migliore.
    def get_better_sign(self, sign):
        match sign:
            case "-":
                return "−"
            case "*":
                return "×"
            case "/":
                return "÷"
            case "^":
                return "xʸ"
            case "B":
                return "⌫"
            case "v":
                return "√"
            case _:
                return sign

    def get_operation_history(self):
        if self.n1_log == "":
            return ""
        if self.state == State.IN_OP:
            return f"{self.n1_log} {self.get_better_sign(self.op)} "
        elif self.state == State.IN_N2:
            return f"{self.n1_log} {self.get_better_sign(self.op)} {self.n2_log}"
        elif self.state == State.RESULT:
            if self.op in "+-*/^":
                return f"{self.n1_log} {self.get_better_sign(self.op)} {self.n2_log} ="
            else:
                return f"{self.get_better_sign(self.op)}({self.n1_log}) ="
        return ""

    def reset(self):
        self.clear_buffer()
        self.n1 = 0.0
        self.n2 = 0.0
        self.result = 0.0
        self.op = ""
        self.n1_log = ""
        self.n2_log = ""
        self.state = State.INIT


# Interfaccia grafica delle calcolatrice.
class CalcolatriceGUI:
    def __init__(self, root):
        self.calcolatrice = Calcolatrice()
        self.window = root
        self.window_setup()
        self.style_setup()
        self.widget_setup()
        self.clear()

    # Setup degli attributi della finestra.
    def window_setup(self):
        self.window.title("Calcolatrice")
        self.window.geometry("440x640")
        self.window.minsize(440, 640)
        self.window["padx"] = 5
        self.window["pady"] = 5

    # Serve a settare lo stile della finestra e dei widget.
    def style_setup(self):
        # FONTS #
        self.huge_font = ("Segoe UI", 32, "bold")
        self.big_font = ("Segoe UI", 22)
        self.medium_font = ("Segoe UI", 18)
        self.small_font = ("Segoe UI", 16)

        colors = {
            "bg": "#292929",
            "fg": "#ffffff",
            "digit": "#303030",
            "op": "#b35a25",
            "eq": "#22b14c",
            "clear": "#b8161c",
            "log": "#7f7f7f",
            "frame": "#555555",
        }

        style = ttk.Style()
        style.theme_use("clam")  # Per personalizzare i colori.
        self.window.configure(background=colors["bg"])  # Bg della finestra.

        # Pulsante dei numeri e del punto.
        style.configure(
            "Digit.TButton",
            background=colors["digit"],
            foreground=colors["fg"],
            font=self.medium_font,
            relief="flat",
        )

        # Pulsante delle operazioni binarie.
        style.configure(
            "Op.TButton",
            background=colors["op"],
            foreground=colors["fg"],
            font=self.big_font,
            relief="flat",
        )

        # Pulsante delle operazioni unarie.
        style.configure(
            "Op2.TButton",
            background=colors["op"],
            foreground=colors["fg"],
            font=self.medium_font,
            relief="flat",
        )

        # Pulsante uguale.
        style.configure(
            "Eq.TButton",
            background=colors["eq"],
            foreground=colors["fg"],
            font=self.medium_font,
            relief="flat",
        )

        # Pulsante per pulire.
        style.configure(
            "Clear.TButton",
            background=colors["clear"],
            foreground=colors["fg"],
            font=self.medium_font,
            relief="flat",
        )
        style.configure(
            "Log.TLabel", background=colors["bg"], foreground=colors["log"]
        )  # Log label.
        style.configure(
            "Calculator.TFrame", background=colors["frame"]
        )  # Frame contenente i pulsanti.

    def widget_setup(self):
        # Log delle operazioni.
        self.log_text = ttk.Label(
            self.window, style="Log.TLabel", font=self.small_font, anchor="e"
        )
        self.log_text.pack(side="top", fill="x")

        # Entry dove verrá mostrato l'input e le operazioni.
        self.output_text = tk.Entry(
            self.window,
            justify="right",
            font=self.huge_font,
            state="readonly",
            readonlybackground="#292929",
            foreground="#ffffff",
            borderwidth=0,
        )
        self.output_text.pack(side="top", fill="x")

        # Frame che conterrá tutti i pulsanti della calcolatrice.
        self.number_frame = ttk.Frame(
            self.window, relief=tk.FLAT, style="Calculator.TFrame"
        )
        self.number_frame.pack(fill="both", expand=True)

        self.number_setup()
        self.window.bind("<Key>", self.key_handler)

    # Metodo che cattura gli input da tastiera e richiama i giusti metodi.
    def key_handler(self, event):
        c = event.char
        keysym = event.keysym

        # Se il tasto premuto non é un carattere valido esci dal metodo.
        if not c and keysym not in ("Return", "BackSpace", "Delete"):
            return
        if c.isdigit() or c == ".":
            self.add_digit(c)
        elif c == "=" or keysym == "Return":
            self.get_result()
        elif c in "+-*^/":
            self.binary_operator(c)
        if keysym == "BackSpace":
            self.backspace()
        elif keysym == "Delete":
            self.clear()

    # Genera i pulsanti, setta la posizione e collega i relativi metodi.
    def number_setup(self):
        # É una lista contenete delle tuple utili per la generazione dei pulsanti.
        n_button = [
            ("tan", "log", "sin", "cos"),
            ("C", "v", "^", "/"),
            ("7", "8", "9", "*"),
            ("4", "5", "6", "-"),
            ("1", "2", "3", "+"),
            ("0", ".", "B", "="),
        ]

        # Itero la lista e ottengo i che é il valore del suo indice,
        # annido al suo interno un altro ciclo per iterare le tuple, j indica l'indice all'interno della tupla.
        for i, (n) in enumerate(n_button):
            self.number_frame.grid_rowconfigure(
                i, weight=1, uniform="g"
            )  # Serve ad avere i pulsati tutti grandi uguali.

            for j, e in enumerate(n):
                self.number_frame.grid_columnconfigure(j, weight=1, uniform="g")
                btn = ttk.Button(
                    self.number_frame, text=self.calcolatrice.get_better_sign(e)
                )
                btn.grid(column=j, row=i, sticky="nsew")

                # Numeri e il punto.
                if e.isdigit() or e == ".":
                    btn.config(
                        style="Digit.TButton", command=lambda t=e: self.add_digit(t)
                    )

                # Carattere che utilizzo per identificare il "backspace".
                elif e == "B":
                    btn.config(
                        style="Digit.TButton", command=lambda t=e: self.backspace()
                    )

                # Clear, per pulire tutto.
                elif e == "C":
                    btn.config(style="Clear.TButton", command=self.clear)

                # Per ottenere il risultato.
                elif e == "=":
                    btn.config(style="Eq.TButton", command=self.get_result)

                # Tutte le operazioni binarie.
                elif e in "+-*^/":
                    btn.config(
                        style="Op.TButton", command=lambda t=e: self.binary_operator(t)
                    )

                # Tutte le operazioni unarie.
                elif e == "v":
                    btn.config(
                        style="Op.TButton", command=lambda t=e: self.unary_operator(t)
                    )
                else:
                    btn.config(
                        style="Op2.TButton", command=lambda t=e: self.unary_operator(t)
                    )

    # Riceve come parametro un digit (oppure un punto), lo invia come input alla classe logica.
    def add_digit(self, digit):
        self.calcolatrice.process_input(InputType.DIGIT, digit)
        self.update_operation_history()
        self.update_out_text()

    # Riceve come parametro un operatore binario, lo invia come input alla classe logica.
    def binary_operator(self, operator):
        self.calcolatrice.process_input(
            InputType.BIN_OP, self.calcolatrice.get_result(), operator
        )
        self.update_operation_history()
        self.update_out_text()

    # Riceve come parametro un operatore unario, lo invia come input alla classe logica.
    def unary_operator(self, operator):
        self.calcolatrice.process_input(
            InputType.UNA_OP, self.calcolatrice.get_result(), operator
        )
        self.update_operation_history()
        self.update_out_text()

    def backspace(self):
        self.calcolatrice.process_input(InputType.BACKSPACE, self.output_text.get())
        self.update_operation_history()
        self.update_out_text()

    def get_result(self):
        self.calcolatrice.process_input(InputType.EQ, self.output_text.get())
        self.update_operation_history()
        self.update_out_text()

    def update_operation_history(self):
        self.clear_history_log()
        self.log_text.config(text=self.calcolatrice.get_operation_history())

    # Pulisce e aggiorna l'output text.
    def update_out_text(self):
        self.clear_out_text()
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, self.calcolatrice.get_display())
        self.output_text.config(state="readonly")

    # Pulisce l'output text.
    def clear_out_text(self):
        self.output_text.config(state="normal")
        self.output_text.delete(0, tk.END)
        self.output_text.config(state="readonly")

    def clear_history_log(self):
        self.log_text.config(text="")

    def clear(self):
        print("CLEAR!")
        self.calcolatrice.process_input(InputType.CLEAR, "0")
        self.clear_history_log()
        self.update_out_text()

## MAIN ##
if __name__ == "__main__":
    root = tk.Tk()
    app = CalcolatriceGUI(root)
    root.mainloop()
