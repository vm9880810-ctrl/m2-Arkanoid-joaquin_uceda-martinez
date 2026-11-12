"""Plantilla del juego Arkanoid para el hito M2.

Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""
from arkanoid_core import *

import os
os.environ["SDL_VIDEODRIVER"] = "windows"
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

@arkanoid_method
def cargar_nivel(self) -> list[str]:
    """Lee el fichero de nivel y devuelve la cuadrícula como lista de filas."""

    if not self.level_path.exists() or not self.level_path.is_file():
        raise ValueError("El fichero no existe o no es un archivo")

    filas = []

    with open(self.level_path, encoding="utf-8") as fichero:
        for fila in fichero:
            fila = fila.strip()

            if fila != "":
                filas.append(fila)

    if len(filas) == 0:
        raise ValueError("El fichero de nivel está vacío")

    anchura = len(filas[0])

    for fila in filas:
        if len(fila) != anchura:
            raise ValueError("Todas las filas deben tener la misma longitud")

    self.layout = filas

    return self.layout

    # - Comprueba que `self.level_path` existe y es fichero.
    # - Lee su contenido, filtra líneas vacías y valida que todas tienen el mismo ancho.
    # - Guarda el resultado en `self.layout` y devuélvelo.

@arkanoid_method
def preparar_entidades(self) -> None:
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""
    self.paddle.size = self.PADDLE_SIZE

    self.paddle.midbottom = (
        self.SCREEN_WIDTH // 2,
        self.SCREEN_HEIGHT - self.PADDLE_OFFSET)

    self.score = 0
    self.lives = 3
    self.end_message = ""

    self.reiniciar_bola((1, -1))

    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.
    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.

@arkanoid_method
def crear_bloques(self) -> None:
    """Crea los bloques a partir del diseño del nivel."""

    self.blocks.clear()
    self.block_colors.clear()
    self.block_symbols.clear()

    for fila, contenido in enumerate(self.layout):
        for columna, simbolo in enumerate(contenido):
            if simbolo in self.BLOCK_COLORS:
                bloque = self.calcular_posicion_bloque(fila, columna)
                self.blocks.append(bloque)
                self.block_colors.append(self.BLOCK_COLORS[simbolo])
                self.block_symbols.append(simbolo)

    # - Limpia `self.blocks`, `self.block_colors` y `self.block_symbols`.
    # - Recorre `self.layout` para detectar símbolos de bloque.
    # - Usa `self.calcular_posicion_bloque` y rellena las listas paralelas.

@arkanoid_method
def procesar_input(self) -> None:
    """Gestiona la entrada de teclado para mover la paleta."""
    teclas = self.obtener_estado_teclas()

    if teclas[self.KEY_LEFT] or teclas[self.KEY_A]:
        self.paddle.x -= self.PADDLE_SPEED

    if teclas[self.KEY_RIGHT] or teclas[self.KEY_D]:
        self.paddle.x += self.PADDLE_SPEED

    if self.paddle.left < 0:
        self.paddle.x = 0

    if self.paddle.right > self.SCREEN_WIDTH:
        self.paddle.x = self.SCREEN_WIDTH - self.paddle.width
    # - Obtén el estado de teclas con `self.obtener_estado_teclas()`.
    # - Desplaza la paleta con `self.PADDLE_SPEED` si se pulsan las teclas izquierda/derecha.
    # - Limita la posición para que no salga de la pantalla.

@arkanoid_method
def actualizar_bola(self) -> None:
    """Actualiza la posición de la bola y resuelve colisiones."""

    posicion_anterior = self.obtener_rect_bola()
    self.ball_pos += self.ball_velocity
    bola = self.obtener_rect_bola()

    if bola.left <= 0:
        self.ball_pos.x = self.BALL_RADIUS
        self.ball_velocity.x *= -1
    if bola.right >= self.SCREEN_WIDTH:
        self.ball_pos.x = self.SCREEN_WIDTH - self.BALL_RADIUS
        self.ball_velocity.x *= -1
    if bola.top <= 0:
        self.ball_pos.y = self.BALL_RADIUS
        self.ball_velocity.y *= -1

    bola = self.obtener_rect_bola()

    if bola.top > self.SCREEN_HEIGHT:
        self.lives -= 1
        if self.lives > 0:
            self.reiniciar_bola((1,-1))
        else:
            self.end_message = "¡Has perdido!"
            self.running = False
        return

    if bola.colliderect(self.paddle) and self.ball_velocity.y > 0:
        self.ball_velocity.y *= -1
        self.ball_pos.y = self.paddle.top - self.BALL_RADIUS
        bola = self.obtener_rect_bola()
    for i in range(len(self.blocks) - 1, -1, -1):
        if bola.colliderect(self.blocks[i]):
            bloque = self.blocks[i]
            simbolo = self.block_symbols[i]
            self.score += self.BLOCK_POINTS[simbolo]
            self.blocks.pop(i)
            self.block_colors.pop(i)
            self.block_symbols.pop(i)
            if (posicion_anterior.bottom <= bloque.top
                    or posicion_anterior.top >= bloque.bottom):
                self.ball_velocity.y *= -1
            else:
                self.ball_velocity.x *= -1

            if len(self.blocks) == 0:
                self.end_message = "¡Has ganado!"
                self.running = False
            return


    # - Suma `self.ball_velocity` a `self.ball_pos` y genera `ball_rect` con `self.obtener_rect_bola()`.
    # - Gestiona rebotes con paredes, paleta y bloques, modificando velocidad y puntuación.
    # - Controla fin de nivel cuando no queden bloques y resta vidas si la bola cae.

@arkanoid_method
def dibujar_escena(self) -> None:
    """Dibuja todos los elementos de la escena."""

    self.screen.fill(self.BACKGROUND_COLOR)
    for i in range(len(self.blocks)):
        self.dibujar_rectangulo(self.blocks[i], self.block_colors[i])

    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)
    self.dibujar_circulo(
        (int(self.ball_pos.x), int(self.ball_pos.y)),
        self.BALL_RADIUS,
        self.BALL_COLOR)

    self.dibujar_texto("Puntuación: " + str(self.score), (10, 10))
    self.dibujar_texto("Vidas: " + str(self.lives), (680, 10))
    if self.end_message:
        self.dibujar_texto(self.end_message, (300, 280), grande=True)
    

    # - Rellena el fondo y dibuja cada bloque con `self.dibujar_rectangulo`.
    # - Pinta la paleta y la bola con las utilidades proporcionadas.
    # - Muestra puntuación, vidas y mensajes usando `self.dibujar_texto`.

@arkanoid_method
def run(self) -> None:
    """Ejecuta el bucle principal del juego."""

    self.inicializar_pygame()
    self.cargar_nivel()
    self.preparar_entidades()
    self.crear_bloques()
    self.running = True

    while self.running:
        for accion in self.iterar_eventos():
            if accion.type == self.EVENT_QUIT:
                self.running = False
            if accion.type == self.EVENT_KEYDOWN:
                if accion.key == self.KEY_ESCAPE:
                    self.running = False
        if self.running:
            self.procesar_input()
            self.actualizar_bola()
            self.dibujar_escena()
            self.actualizar_pantalla()
            self.clock.tick(self.FPS)
    if self.end_message:
        self.actualizar_pantalla()
        self.esperar(1000)
    self.finalizar_pygame()

    # - Inicializa recursos (`self.inicializar_pygame`, `self.cargar_nivel`, etc.).
    # - Procesa eventos de `self.iterar_eventos()` y llama a los métodos de actualización/dibujo.
    # - Refresca la pantalla con `self.actualizar_pantalla()` y cierra con `self.finalizar_pygame()`.

def main() -> None:
    """Permite ejecutar el juego desde la línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Plantilla del hito M2: Arkanoid con pygame.",
    )
    parser.add_argument(
        "level",
        type=str,
        help="Ruta al fichero de nivel (texto con # para bloques y . para huecos).",
    )
    args = parser.parse_args()

    game = ArkanoidGame(args.level)
    game.run()


if __name__ == "__main__":
    main()

"""Para ejecutar python arkanoid_game.py niveles/demo.txt en la terminal"""
