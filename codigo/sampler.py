import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    """
    Sampler: sample & hold SIN retorno a cero (figura 2.b de la guia).

    Entrada 0 : senal sinusoidal.
    Entrada 1 : senal cuadrada de control (niveles 0 / 1).
    Salida  0 : senal PAM plana. En cada flanco de subida de la cuadrada se
                toma una muestra y se mantiene durante TODO el periodo Ts,
                hasta el siguiente flanco (ya no vuelve a cero).
    """

    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='Sampler',
            in_sig=[np.float32, np.float32],
            out_sig=[np.float32]
        )
        self.umbral = 0.5           # decide si el pulso esta en alto
        self.ctrl_prev = False      # estado del pulso en la muestra anterior
        self.valor_retenido = 0.0   # ultima muestra tomada

    def work(self, input_items, output_items):
        in_data = input_items[0]
        in_ctrl = input_items[1]
        out = output_items[0]
        n = len(out)

        # 1) Pulso en alto / bajo
        activo = in_ctrl[:n] > self.umbral

        # 2) Flancos de subida
        anterior = np.concatenate(([self.ctrl_prev], activo[:-1]))
        flancos = activo & ~anterior

        # 3) Indice del ultimo flanco ocurrido para cada muestra
        idx = np.maximum.accumulate(np.where(flancos, np.arange(n), -1))

        # 4) Valor retenido (si aun no hay flanco en este bloque de datos,
        #    se usa el que venia de la llamada anterior)
        valores = np.where(idx >= 0,
                           in_data[np.maximum(idx, 0)],
                           self.valor_retenido)

        # 5) Sin retorno a cero: la muestra se mantiene todo el periodo
        out[:] = valores

        # 6) Guardar estado para la siguiente llamada
        self.valor_retenido = float(valores[-1])
        self.ctrl_prev = bool(activo[-1])
        return len(out)
