import flet as ft
import random
import threading
import time
import os
import sys

# === PARCHE INTELIGENTE DE RUTA (WINDOWS EXE VS ANDROID) ===
# Solo se ejecuta si el script está congelado por PyInstaller en Windows
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
    os.environ["FLET_CONTROLS_RESOURCE_PATH"] = os.path.join(base_path, "flet", "controls")
# ==========================================================

class JuegoAgilidad:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Desafío Mental Express ⚡"
        self.page.window_width = 450
        self.page.window_height = 650
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.horizontal_alignment = "center"
        self.page.vertical_alignment = "center"

        # Variables del juego
        self.puntos = 0
        self.tiempo_restante = 30
        self.respuesta_correcta = 0
        self.lista_records = []
        self.juego_activo = False

        # --- COMPONENTES DE LA INTERFAZ ---
        self.input_nombre = ft.TextField(
            label="Tu Nombre", 
            width=250, 
            text_align="center",
            on_submit=self.comenzar_juego
        )
        self.txt_cronometro = ft.Text("⏱️ 30s", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER)
        self.txt_puntos = ft.Text("Score: 0", size=20, color=ft.Colors.GREEN_300)
        self.txt_operacion = ft.Text("", size=40, weight=ft.FontWeight.BOLD)
        
        self.input_respuesta = ft.TextField(
            label="Respuesta", 
            width=150, 
            text_align="center", 
            keyboard_type=ft.KeyboardType.NUMBER, 
            on_submit=self.verificar_respuesta
        )
        self.tabla_records = ft.Column(horizontal_alignment="center")

        # Mostrar pantalla inicial
        self.mostrar_pantalla_inicio()

    def mostrar_pantalla_inicio(self):
        self.page.clean()
        self.page.add(
            ft.Column(
                controls=[
                    ft.Icon(ft.Icons.PSYCHOLOGY, size=60, color=ft.Colors.LIGHT_BLUE_ACCENT),
                    ft.Text("AGILIDAD MENTAL", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Responde presionando ENTER. ¡Ahora más difícil!", text_align="center", color=ft.Colors.GREY_400),
                    ft.Divider(height=20),
                    self.input_nombre,
                    ft.FilledButton("¡Empezar Juego!", icon=ft.Icons.PLAY_ARROW, on_click=self.comenzar_juego),
                    ft.Divider(height=20),
                    ft.Text("🏆 TOP RÉCORDS 🏆", size=18, weight=ft.FontWeight.BOLD),
                    self.tabla_records
                ],
                horizontal_alignment="center",
                alignment="center",
                spacing=15
            )
        )
        self.actualizar_tabla_records()
        self.page.update()

    def comenzar_juego(self, e):
        if not self.input_nombre.value.strip():
            self.input_nombre.error_text = "Por favor, introduce tu nombre"
            self.page.update()
            return
        
        self.puntos = 0
        self.tiempo_restante = 30
        self.juego_activo = True
        self.txt_puntos.value = f"Score: {self.puntos}"
        self.txt_cronometro.value = f"⏱️ {self.tiempo_restante}s"
        self.txt_cronometro.color = ft.Colors.AMBER
        
        self.page.clean()
        self.page.add(
            ft.Column(
                controls=[
                    ft.Row([self.txt_cronometro, self.txt_puntos], alignment="spaceBetween", width=350),
                    ft.Container(height=40),
                    self.txt_operacion,
                    ft.Container(height=20),
                    self.input_respuesta,
                    ft.Text("Presiona ENTER para responder", size=12, color=ft.Colors.GREY_500)
                ],
                horizontal_alignment="center",
                alignment="center",
                spacing=10
            )
        )
        self.generar_operacion()
        
        t = threading.Thread(target=self.reloj_cuenta_atras, daemon=True)
        t.start()

    def reloj_cuenta_atras(self):
        while self.tiempo_restante > 0 and self.juego_activo:
            time.sleep(1)
            self.tiempo_restante -= 1
            self.txt_cronometro.value = f"⏱️ {self.tiempo_restante}s"
            if self.tiempo_restante <= 5:
                self.txt_cronometro.color = ft.Colors.RED_400
            self.page.update()
        
        if self.juego_activo:
            self.finalizar_juego()

    def generar_operacion(self):
        operador = random.choice(["+", "-", "*", "/"])
        
        if operador == "+":
            num1 = random.randint(10, 50)
            num2 = random.randint(10, 50)
            self.respuesta_correcta = num1 + num2
        elif operador == "-":
            num1 = random.randint(15, 50)
            num2 = random.randint(10, num1)
            self.respuesta_correcta = num1 - num2
        elif operador == "*":
            num1 = random.randint(4, 15)
            num2 = random.randint(3, 12)
            self.respuesta_correcta = num1 * num2
        elif operador == "/":
            num2 = random.randint(3, 10)
            self.respuesta_correcta = random.randint(3, 12)
            num1 = num2 * self.respuesta_correcta

        self.txt_operacion.value = f"{num1} {operador} {num2} = ?"
        self.input_respuesta.value = ""
        self.page.update()
        
        self.input_respuesta.focus()
        self.page.update()

    def verificar_respuesta(self, e):
        if self.tiempo_restante <= 0 or not self.juego_activo: return
        
        try:
            r_usuario = int(self.input_respuesta.value)
            if r_usuario == self.respuesta_correcta:
                self.puntos += 1
                self.txt_puntos.value = f"Score: {self.puntos}"
            self.generar_operacion()
        except ValueError:
            self.input_respuesta.value = ""
            self.page.update()

    def finalizar_juego(self):
        self.juego_activo = False
        nombre = self.input_nombre.value.strip()
        self.lista_records.append({"nombre": nombre, "puntos": self.puntos})
        self.lista_records = sorted(self.lista_records, key=lambda x: x["puntos"], reverse=True)[:5]
        
        self.page.clean()
        self.page.add(
            ft.Column(
                controls=[
                    ft.Icon(ft.Icons.TIMER_OFF_ROUNDED, size=60, color=ft.Colors.RED_400),
                    ft.Text("¡Tiempo Agotado!", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Buen intento, {nombre}", size=18, color=ft.Colors.GREY_400),
                    ft.Text(f"Lograste: {self.puntos} aciertos", size=24, color=ft.Colors.GREEN_300, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    ft.FilledButton("Volver al Inicio", icon=ft.Icons.HOME, on_click=lambda _: self.mostrar_pantalla_inicio())
                ],
                horizontal_alignment="center",
                alignment="center",
                spacing=15
            )
        )
        self.page.update()

    def actualizar_tabla_records(self):
        self.tabla_records.controls.clear()
        if not self.lista_records:
            self.tabla_records.controls.append(ft.Text("¡Ninguno todavía! Sé el primero.", color=ft.Colors.GREY_500))
        else:
            for i, record in enumerate(self.lista_records):
                self.tabla_records.controls.append(
                    ft.Row(
                        [
                            ft.Text(f"#{i+1} {record['nombre']}", size=16, weight=ft.FontWeight.W_500),
                            ft.Text(f"{record['puntos']} pts", size=16, color=ft.Colors.GREEN_300, weight=ft.FontWeight.BOLD)
                        ],
                        alignment="spaceBetween",
                        width=250
                    )
                )

def main(page: ft.Page):
    JuegoAgilidad(page)

if __name__ == "__main__":
    ft.app(main)
