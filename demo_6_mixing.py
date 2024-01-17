""" Create one output template, upconvert it, sample it and downconvert it.

Connect one output port directly to one input port.
"""
import matplotlib.pyplot as plt
import numpy as np

from presto import pulsed
from presto.utils import sin2

# Any port on Vivace
# Any port on Presto wide or wamp
# Ports 1-4 on Presto-8-QC
# Ports 1-8 on Presto-16-QC
output_port = 1
input_port = 1

ADDRESS = "192.168.20.19"  # set address/hostname of Vivace/Presto here
EXT_REF = False  # set to True to use external 10 MHz reference


with pulsed.Pulsed(
    ext_ref_clk=EXT_REF,
    address=ADDRESS,
    adc_mode=pulsed.AdcMode.Mixed,
    dac_mode=pulsed.DacMode.Mixed,
) as pls:
    LO_freq = 6.51e9
    pls.hardware.configure_mixer(
        LO_freq, out_ports=output_port, in_ports=input_port, sync=True
    )  # sync here
    ######################################################################
    # Select input ports to store and the duration of each store
    pls.set_store_ports(input_port)
    pls.set_store_duration(2000e-9)  # 2000 ns

    ######################################################################
    # create a 200 ns long template on output_port
    # make a sine wave with a square window
    duration = 200e-9
    N = int(round(duration * pls.get_fs("dac")))
    data = sin2(N)
    template_1 = pls.setup_template(output_port, group=0, template=data, envelope=False)

    ######################################################################
    # setup scale for the (output, group). only one scale used
    pls.setup_scale_lut(output_port, group=0, scales=1.0)

    ######################################################################
    # define the sequence of pulses and data stores in time
    # at time zero, output the template and start a store window
    T = 0.0
    pls.output_pulse(T, template_1)
    pls.store(T)

    ######################################################################
    # Actually run the sequence, only run once with no averaging
    pls.run(period=10e-6, repeat_count=1, num_averages=100)
    t_arr, data = pls.get_store_data()

fig, ax = plt.subplots(tight_layout=True)
ax.plot(1e9 * t_arr, data[0, 0, :].real, label="real")
ax.plot(1e9 * t_arr, data[0, 0, :].imag, label="imag")
ax.set_xlabel("Time [ns]")
ax.set_ylabel("Input signal [FS]")
ax.legend()
fig.show()
