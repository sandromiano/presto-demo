
import numpy as np
import matplotlib.pyplot as plt

from vivace import pulsed


with pulsed.Pulsed(ext_ref_clk=False, force_reload=False, address="192.168.42.50", port=3490) as pls:
    ######################################################################
    # Select inputs to store and the duration of each store
    pls.set_store_ports([1,])
    pls.set_store_duration(2e-6)

    ######################################################################
    # Sinewave generator, template as envelope

    # The template defines the envelope, specify that it is an envelope
    # for carrier generator 1
    N = 4088
    t = np.arange(N)*0.25e-9
    s = np.hanning(N)
    template_1 = pls.setup_template(1, s, envelope=1)

    # setup a list of frequencies for carrier generator 1
    f = np.linspace(10e6, 100e6, 10)
    p = np.zeros(10)
    pls.setup_freq_lut(output_ports=1, carrier=1, frequencies=f, phases=p)


    ######################################################################
    # define the sequence of pulses and data stores in time
    for i in range(10):
        pls.output_pulse(10e-6*i, template_1)
        pls.store(10e-6*i)
        pls.next_frequency(10e-6*i+5e-6, 1)

    t_arr, data = pls.perform_measurement(period=500e-6, repeat_count=1, num_averages=1)

fig, ax = plt.subplots(10)
for i in range(10):
    ax[i].plot(t_arr, data[i, 0, :])
fig.show()


