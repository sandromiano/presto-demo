
import numpy as np
import matplotlib.pyplot as plt

from vivace import pulsed


with pulsed.Pulsed(ext_ref_clk=False, force_reload=False, address="192.168.42.50", port=3490) as pls:
    ######################################################################
    # Select inputs to store and the duration of each store
    pls.set_store_ports([1, 2, 3, 4, 5 ,6 ,7 ,8]) #all ports
    pls.set_store_duration(4.096e-6) # max window length

    ######################################################################
    # create a 16 4088 sample long templates on each output
    N = 4088 #max single template length
    t = np.arange(N)*0.25e-9
    window =(np.bartlett(N), np.blackman(N), np.hamming(N), np.hanning(N),
             np.kaiser(N, 0), np.kaiser(N, 5), np.kaiser(N, 6), np.kaiser(N, 8.6))
    templates = [ [] for _ in range(8)]
    for port in range(1,9):
        for template_index in range(16):
            f = 10e6 + 1e6 * template_index
            s = np.sin(2*np.pi*f*t) * window[port-1]
            templates[port-1].append(pls.setup_template(port, s))

    ######################################################################
    # define the sequence of pulses and data stores in time
    # The hardware can average ~1e9 samples/second, when this much data is
    # stored simultaneously the stores must be separated in time for the
    # averaging to keep up
    spacing = 4.096e-6 * 4e9 * 8 / 1e9
    for template_index in range(16):
        for port in range(1,9):
            pls.output_pulse(template_index*spacing, templates[port-1][template_index])
        pls.store(template_index*spacing)

    t_arr, data = pls.perform_measurement(period=spacing*16, repeat_count=1, num_averages=1)

fig, ax = plt.subplots(8, 16, sharex=True, sharey=True)
for port in range(8):
    for store in range(16):
        ax[port, store].plot(t_arr, data[store, port, :])
        ax[port, store].axis('off')
fig.tight_layout()
fig.show()


