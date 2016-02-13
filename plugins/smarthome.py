# -*- coding: utf-8 -*-
from neb.plugins import Plugin
from timer_thread import PeriodicThread
import plotly.plotly as py
import plotly.graph_objs as go
import os
import time
import datetime
import struct
import serial
from serial.serialutil import SerialException

class SmartHomePlugin(Plugin):
    """Control home appliance.
    smarthome remote <appliance> <command>
    smarthome get <sensor>
    """
    name ="smarthome"

    def __init__(self, *args, **kwargs):
        self.temperatureData = []
        self.timeAxis = []
        self.period = 8
        self.monitoringThread = PeriodicThread(callback=self._log_temperature, period=self.period, name="logTemp")
        self._setup_monitoring()

        super(Plugin, self).__init__(*args, **kwargs)
    #def on_sync(self, response):
        #print("SSSSSS", response)
    def _setup_monitoring(self):
        #self.monitoringThread = PeriodicThread(callback=self._log_temperature, period=self.period, name="logTemp")
        self.monitoringThread.start()

    def _log_temperature(self):
        s = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
        try:
            s.open()
        except SerialException:
            print "Port is open"
            pass

        s.write('2')
        time.sleep(2)
        dat = s.read(4)
        temp = struct.unpack('f', dat)
        try:
            s.close()
        except SerialException:
            print "Port is closed"
            pass
        self.timeAxis.append(datetime.datetime.now())
        self.temperatureData.append(temp)
        if(len(self.temperatureData) > 30):
            self.temperatureData.pop(0)
            self.timeAxis.pop(0)
        #print (self.timeAxis, self.temperatureData)

    def cmd_get(self, event, *args):
        # for demo
        sensor = args[0];

        if(len(args) > 1):
            # get the image
            pass

        available_sensor = ["temperature"];
        if sensor in available_sensor:
            return "%s\nLast 5 mins: %s" % (getattr(self, "_get_%s" % sensor)(), self._plot_temp_data());
        else:
            return "%s is currently not available" % sensor;

    def _plot_temp_data(self):
        trace = go.Scatter(
            x = self.timeAxis,
            y = self.temperatureData,
            mode = 'lines+markers',
            name = 'Temperature'
        )
        data = [trace]
        plot_url = py.plot(data, filename="temperaturelog")
        print plot_url
        return plot_url

    def cmd_remote(self, event, *args):
        # for demo
        appliance_list = {
            "ac": {
                "target": "AC",
                "cmd": {
                    "heater": "POWER",
                    "off": "OFF"
                }
            },
            "tv": {
                "target":  "TV",
                "cmd": {
                    "power": "POWER",
                    "ch_up": "CH_UP",
                    "ch_down": "CH_DOWN",
                    "vol_up": "VOL_UP",
                    "vol_down": "VOL_DOWN"
                }
            },
            "light": {
                "target": "LIGHT",
                "cmd": {
                    "on": "ON",
                    "off": "OFF"
                }
            }
        }
        appliance = args[0].lower()
        command = args[1].lower()
        #print(args)
        exe_cmd = "irsend SEND_ONCE %s %s" % (appliance_list[appliance]['target'], appliance_list[appliance]['cmd'][command])
        os.system(exe_cmd)
        return "Remote command received!"

    def _get_temperature(self):
        degree_sign= u'\N{DEGREE SIGN}'
        s = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
        try:
            s.open()
        except SerialException:
            print "Port is open"
            pass

        s.write('2')
        time.sleep(2)
        dat = s.read(4)
        temp = struct.unpack('f', dat)
        try:
            s.close()
        except SerialException:
            print "Port is closed"
            pass

        return "Current Temperature is %.02f%c C" % (temp[0], degree_sign)
