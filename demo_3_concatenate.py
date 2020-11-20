
import numpy as np
import matplotlib.pyplot as plt

from vivace import pulsed

with pulsed.Pulsed(ext_ref_clk=False, force_reload=False, address="192.168.42.50", port=3490) as pls:
    ######################################################################
    # Select inputs to store and the duration of each store
    pls.set_store_ports([1, 2])
    pls.set_store_duration(1e-6)

    ######################################################################
    # create a long pulse using multiple templates
    N = 60000
    t = np.arange(N)*0.25e-9
    f = 55e6
    s = np.sin(2*np.pi*f*t) * np.hanning(N)
    template_1 = pls.setup_template(1, s)

    ######################################################################
    # create a long pulse of sections long_drive


    ######################################################################
    # define the sequence of pulses and data stores in time
    # output the long pulse and store sections of it
    pls.output_pulse(0e-6, template_1)
    pls.store(0)
    pls.store(4e-6)
    pls.store(8e-6)
    pls.store(12e-6)

    t_arr, data = pls.perform_measurement(period=100e-6, repeat_count=1, num_averages=1)

fig, ax = plt.subplots(4, sharey=True)
for i in range(4):
    ax[i].plot(t_arr, data[i, 0, :], label=f"store {i}, port 0")
    ax[i].legend()
fig.show()


