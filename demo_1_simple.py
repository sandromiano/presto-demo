
import numpy as np
import matplotlib.pyplot as plt

from vivace import pulsed


with pulsed.Pulsed(ext_ref_clk=False, force_reload=False, address="192.168.42.50", port=3490) as pls:
    ######################################################################
    # Select inputs to store and the duration of each store
    pls.set_store_ports([1,])
    pls.set_store_duration(1e-6)

    ######################################################################
    # create a 512 sample long template on output 1
    N = 512
    t = np.arange(N)*0.25e-9
    f = 55e6
    s = np.sin(2*np.pi*f*t) * np.hanning(N)
    template_1 = pls.setup_template(1, s)

    ######################################################################
    # define the sequence of pulses and data stores in time
    # at time 1us, output the template and start a store window
    pls.output_pulse(1e-6, template_1)
    pls.store(1e-6)


    ######################################################################
    # Actually run the sequence, only run once with no averaging
    t_arr, data = pls.perform_measurement(period=10e-6, repeat_count=1, num_averages=1)

fig, ax = plt.subplots()
ax.plot(t_arr, data[0, 0, :], label="store 0, port 0")
ax.legend()
fig.show()


