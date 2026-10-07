import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    """
    Muestreo Instantaneo Plano (Sample & Hold con retorno a cero).

    Entrada 0 : senal analogica (sinusoide de 1 kHz).
    Entrada 1 : senal cuadrada de control (20 kHz, niveles 0 / 1).
    Salida  0 : senal PAM plana (figura 2.a de la guia).

    En cada flanco de subida de la senal cuadrada se toma UNA muestra de
    la senal analogica y ese valor se mantiene constante (plano) mientras
    el pulso este en alto. Cuando el pulso vuelve a cero, la salida
    tambien vuelve a cero (PAM instantanea con retorno a cero).
    """

    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='Muestreo Instantaneo Plano',
            in_sig=[np.float32, np.float32],
            out_sig=[np.float32]
        )
        # Umbral para decidir si el pulso de control esta en alto
        self.umbral = 0.5
        # Memoria entre llamadas a work(): estado del control y valor retenido
        self.ctrl_prev = False
        self.valor_retenido = 0.0

    def work(self, input_items, output_items):
        in_data = input_items[0]   # senal sinusoidal
        in_ctrl = input_items[1]   # senal cuadrada
        out = output_items[0]
        n = len(out)

        # 1) Pulso en alto (True) o en bajo (False)
        activo = in_ctrl[:n] > self.umbral

        # 2) Deteccion de flanco de subida: alto ahora y bajo en la muestra anterior
        anterior = np.concatenate(([self.ctrl_prev], activo[:-1]))
        flancos = activo & ~anterior

        # 3) Para cada muestra, indice del ultimo flanco de subida ocurrido
        idx = np.maximum.accumulate(np.where(flancos, np.arange(n), -1))

        # 4) Valor retenido: el de la senal en ese flanco (o el que venia del
        #    bloque de datos anterior si todavia no ha ocurrido ningun flanco)
        valores = np.where(idx >= 0,
                           in_data[np.maximum(idx, 0)],
                           self.valor_retenido)

        # 5) Plano mientras el pulso este alto, cero cuando el pulso baja
        out[:] = np.where(activo, valores, 0.0)

        # 6) Guardar estado para la siguiente llamada a work()
        self.valor_retenido = float(valores[-1])
        self.ctrl_prev = bool(activo[-1])

        return len(out)
