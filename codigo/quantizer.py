import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    """
    Quantizer: cuantizador uniforme (mid-rise) de N_bits sobre [-M_p, +M_p].

    N_bits : numero de bits del cuantizador  ->  L = 2**N_bits niveles
    M_p    : valor maximo de entrada (fondo de escala)

    Paso de cuantizacion:  delta = 2*M_p / L
    Cada muestra se reemplaza por el centro del escalon que le corresponde.
    """

    def __init__(self, N_bits=4, M_p=1.0):
        gr.sync_block.__init__(
            self,
            name='Quantizer',
            in_sig=[np.float32],
            out_sig=[np.float32]
        )
        self.N_bits = N_bits
        self.M_p = M_p

    def work(self, input_items, output_items):
        x = input_items[0]
        out = output_items[0]

        # Se recalcula en cada llamada para que el slider de N_bits
        # cambie el cuantizador en vivo
        N = int(round(self.N_bits))
        Mp = float(self.M_p)
        L = 2 ** N                      # numero de niveles
        delta = 2.0 * Mp / L            # paso de cuantizacion

        # 1) Limitar al fondo de escala (evita sobrecarga)
        xc = np.clip(x, -Mp, Mp)

        # 2) Indice del escalon: de -L/2 a L/2-1
        k = np.floor(xc / delta)
        k = np.clip(k, -L / 2, L / 2 - 1)

        # 3) Valor cuantizado = centro del escalon
        out[:] = (k + 0.5) * delta
        return len(out)
