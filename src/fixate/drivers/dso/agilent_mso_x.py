import struct
from fixate.core.exceptions import InstrumentError
from fixate.drivers.dso.helper import DSO
import time


class MSO_X_3000(DSO):
    REGEX_ID = "KEYSIGHT TECHNOLOGIES,[DM]SO-X|AGILENT TECHNOLOGIES,[DM]SO-X"
    INSTR_TYPE = "VISA"
    retrys_on_timeout = 1

    def __init__(self, instrument):
        super().__init__(instrument)
        self.display = "on"
        self.is_connected = True
        self.reset()
        self.instrument.query_delay = 0.2
        self._store = {}
        self.api = [
            ("run", self.write, "RUN"),
            ("single", self.write, "SINGLE"),
            ("stop", self.write, "STOP"),
            ("ch1._call", self.write, "CHAN1:DISP {value:d}"),
            ("ch2._call", self.write, "CHAN2:DISP {value:d}"),
            ("ch3._call", self.write, "CHAN3:DISP {value:d}"),
            ("ch4._call", self.write, "CHAN4:DISP {value:d}"),
            ("ch1.scale", self.write, "CHAN1:SCAL {value}"),
            ("ch2.scale", self.write, "CHAN2:SCAL {value}"),
            ("ch3.scale", self.write, "CHAN3:SCAL {value}"),
            ("ch4.scale", self.write, "CHAN4:SCAL {value}"),
            ("ch1.offset", self.write, "CHAN1:OFFS {value}"),
            ("ch2.offset", self.write, "CHAN2:OFFS {value}"),
            ("ch3.offset", self.write, "CHAN3:OFFS {value}"),
            ("ch4.offset", self.write, "CHAN4:OFFS {value}"),
            ("ch1.coupling.ac", self.write, "CHAN1:COUP AC"),
            ("ch2.coupling.ac", self.write, "CHAN2:COUP AC"),
            ("ch3.coupling.ac", self.write, "CHAN3:COUP AC"),
            ("ch4.coupling.ac", self.write, "CHAN4:COUP AC"),
            ("ch1.coupling.dc", self.write, "CHAN1:COUP DC"),
            ("ch2.coupling.dc", self.write, "CHAN2:COUP DC"),
            ("ch3.coupling.dc", self.write, "CHAN3:COUP DC"),
            ("ch4.coupling.dc", self.write, "CHAN4:COUP DC"),
            ("ch1.probe.attenuation", self.write, "CHAN1:PROB {value}"),
            ("ch2.probe.attenuation", self.write, "CHAN2:PROB {value}"),
            ("ch3.probe.attenuation", self.write, "CHAN3:PROB {value}"),
            ("ch4.probe.attenuation", self.write, "CHAN4:PROB {value}"),
            ("time_base.scale", self.write, "TIM:SCAL {value}"),
            ("time_base.position", self.write, "TIM:POS {value}"),
            ("trigger.mode.edge._call", self.write, "TRIG:MODE EDGE"),
            ("trigger.mode.edge.level", self.write, "TRIG:EDGE:LEVEL {value}"),
            ("trigger.mode.edge.source.ch1", self.write, "TRIG:EDGE:SOUR CHAN1"),
            ("trigger.mode.edge.source.ch2", self.write, "TRIG:EDGE:SOUR CHAN2"),
            ("trigger.mode.edge.source.ch3", self.write, "TRIG:EDGE:SOUR CHAN3"),
            ("trigger.mode.edge.source.ch4", self.write, "TRIG:EDGE:SOUR CHAN4"),
            ("trigger.mode.edge.slope.rising", self.write, "TRIG:EDGE:SLOPE POS"),
            ("trigger.mode.edge.slope.falling", self.write, "TRIG:EDGE:SLOPE NEG"),
            ("trigger.mode.edge.slope.either", self.write, "TRIG:EDGE:SLOPE EITH"),
            ("trigger.mode.edge.slope.alternating", self.write, "TRIG:EDGE:SLOPE ALT"),
            ("trigger.sweep.normal", self.write, "TRIG:SWE NORM"),
            ("trigger.sweep.auto", self.write, "TRIG:SWE AUTO"),
            ("trigger.coupling.ac", self.write, "TRIG:COUP AC"),
            ("trigger.coupling.dc", self.write, "TRIG:COUP DC"),
            ("trigger.coupling.lf_reject", self.write, "TRIG:COUP LFR"),
            ("acquire.normal", self.write, "ACQ:TYPE NORM"),
            ("acquire.peak_detect", self.write, "ACQ:TYPE PEAK"),
            ("acquire.averaging", self.write, "ACQ:TYPE AVER;:ACQ:COUN {value}"),
            ("acquire.high_resolution", self.write, "ACQ:TYPE HRES"),
            ("events.trigger", self.query_bool, ":TER?"),
            # Ch1 Measure
            ("measure.counter.ch1", self.query_value, "MEAS:COUN? CHAN1"),
            ("measure.delay.ch1.ch1", self.query_value, "MEAS:DEL? CHAN1,CHAN1"),
            ("measure.delay.ch1.ch2", self.query_value, "MEAS:DEL? CHAN1,CHAN2"),
            ("measure.delay.ch1.ch3", self.query_value, "MEAS:DEL? CHAN1,CHAN3"),
            ("measure.delay.ch1.ch4", self.query_value, "MEAS:DEL? CHAN1,CHAN4"),
            ("measure.delay.ch1.function", self.query_value, "MEAS:DEL? FUNC,CHAN1"),
            ("measure.delay.ch1.math", self.query_value, "MEAS:DEL? MATH,CHAN1"),
            ("measure.delay.ch1.wmemory1", self.query_value, "MEAS:DEL? WMEM1,CHAN1"),
            ("measure.delay.ch1.wmemory2", self.query_value, "MEAS:DEL? WMEM2,CHAN1"),
            ("measure.duty.ch1", self.query_value, "MEAS:DUTY? CHAN1"),
            ("measure.fall_time.ch1", self.query_value, "MEAS:FALL? CHAN1"),
            ("measure.frequency.ch1", self.query_value, "MEAS:FREQ? CHAN1"),
            ("measure.cnt_edge_rising.ch1", self.query_value, "MEAS:NEDG? CHAN1"),
            ("measure.cnt_edge_falling.ch1", self.query_value, "MEAS:PEDG? CHAN1"),
            ("measure.cnt_pulse_positive.ch1", self.query_value, "MEAS:NPUL? CHAN1"),
            ("measure.cnt_pulse_negative.ch1", self.query_value, "MEAS:PPUL? CHAN1"),
            ("measure.period.ch1", self.query_value, "MEAS:PER? CHAN1"),
            ("measure.phase.ch1.ch1", self.query_value, "MEAS:PHAS? CHAN1,CHAN1"),
            ("measure.phase.ch1.ch2", self.query_value, "MEAS:PHAS? CHAN1,CHAN2"),
            ("measure.phase.ch1.ch3", self.query_value, "MEAS:PHAS? CHAN1,CHAN3"),
            ("measure.phase.ch1.ch4", self.query_value, "MEAS:PHAS? CHAN1,CHAN4"),
            ("measure.phase.ch1.function", self.query_value, "MEAS:PHAS? CHAN1,FUNC"),
            ("measure.phase.ch1.math", self.query_value, "MEAS:PHAS? CHAN1,MATH"),
            ("measure.phase.ch1.wmemory1", self.query_value, "MEAS:PHAS? CHAN1,WMEM1"),
            ("measure.phase.ch1.wmemory2", self.query_value, "MEAS:PHAS? CHAN1,WMEM2"),
            ("measure.pulse_width.ch1", self.query_value, "MEAS:PWID? CHAN1"),
            ("measure.vamplitude.ch1", self.query_value, "MEAS:VAMP? CHAN1"),
            ("measure.vaverage.cycle.ch1", self.query_value, "MEAS:VAV? CYCL,CHAN1"),
            ("measure.vaverage.display.ch1", self.query_value, "MEAS:VAV? DISP,CHAN1"),
            ("measure.vbase.ch1", self.query_value, "MEAS:VBAS? CHAN1"),
            ("measure.vmax.ch1", self.query_value, "MEAS:VMAX? CHAN1"),
            ("measure.vmin.ch1", self.query_value, "MEAS:VMIN? CHAN1"),
            ("measure.vpp.ch1", self.query_value, "MEAS:VPP? CHAN1"),
            ("measure.vratio.cycle.ch1.ch1", self.query_value, "MEAS:VRAT? CYCL,CHAN1,CHAN1"),
            ("measure.vratio.cycle.ch1.ch2", self.query_value, "MEAS:VRAT? CYCL,CHAN1,CHAN2"),
            ("measure.vratio.cycle.ch1.ch3", self.query_value, "MEAS:VRAT? CYCL,CHAN1,CHAN3"),
            ("measure.vratio.cycle.ch1.ch4", self.query_value, "MEAS:VRAT? CYCL,CHAN1,CHAN4"),
            ("measure.vratio.cycle.ch1.function", self.query_value, "MEAS:VRAT? CYCL,CHAN1,FUNC"),
            ("measure.vratio.cycle.ch1.math", self.query_value, "MEAS:VRAT? CYCL,CHAN1,MATH"),
            ("measure.vratio.cycle.ch1.wmemory1", self.query_value, "MEAS:VRAT? CYCL,CHAN1,WMEM1"),
            ("measure.vratio.cycle.ch1.wmemory2", self.query_value, "MEAS:VRAT? CYCL,CHAN1,WMEM2"),
            ("measure.vratio.display.ch1.ch1", self.query_value, "MEAS:VRAT? DISP,CHAN1,CHAN1"),
            ("measure.vratio.display.ch1.ch2", self.query_value, "MEAS:VRAT? DISP,CHAN1,CHAN2"),
            ("measure.vratio.display.ch1.ch3", self.query_value, "MEAS:VRAT? DISP,CHAN1,CHAN3"),
            ("measure.vratio.display.ch1.ch4", self.query_value, "MEAS:VRAT? DISP,CHAN1,CHAN4"),
            ("measure.vratio.display.ch1.function", self.query_value, "MEAS:VRAT? DISP,CHAN1,FUNC"),
            ("measure.vratio.display.ch1.math", self.query_value, "MEAS:VRAT? DISP,CHAN1,MATH"),
            ("measure.vratio.display.ch1.wmemory1", self.query_value, "MEAS:VRAT? DISP,CHAN1,WMEM1"),
            ("measure.vratio.display.ch1.wmemory2", self.query_value, "MEAS:VRAT? DISP,CHAN1,WMEM2"),
            ("measure.vrms.dc.cycle.ch1", self.query_value, "MEAS:VRMS? CYCL,DC,CHAN1"),
            ("measure.vrms.dc.display.ch1", self.query_value, "MEAS:VRMS? DISP,DC,CHAN1"),
            ("measure.vrms.ac.cycle.ch1", self.query_value, "MEAS:VRMS? CYCL,AC,CHAN1"),
            ("measure.vrms.ac.display.ch1", self.query_value, "MEAS:VRMS? DISP,AC,CHAN1"),
            ("measure.xmax.ch1", self.query_value, "MEAS:XMAX? CHAN1"),
            ("measure.xmin.ch1", self.query_value, "MEAS:XMIN? CHAN1"),
            # Ch2 Measure
            ("measure.counter.ch2", self.query_value, "MEAS:COUN? CHAN2"),
            ("measure.delay.ch2.ch1", self.query_value, "MEAS:DEL? CHAN2,CHAN1"),
            ("measure.delay.ch2.ch2", self.query_value, "MEAS:DEL? CHAN2,CHAN2"),
            ("measure.delay.ch2.ch3", self.query_value, "MEAS:DEL? CHAN2,CHAN3"),
            ("measure.delay.ch2.ch4", self.query_value, "MEAS:DEL? CHAN2,CHAN4"),
            ("measure.delay.ch2.function", self.query_value, "MEAS:DEL? FUNC,CHAN2"),
            ("measure.delay.ch2.math", self.query_value, "MEAS:DEL? MATH,CHAN2"),
            ("measure.delay.ch2.wmemory1", self.query_value, "MEAS:DEL? WMEM1,CHAN2"),
            ("measure.delay.ch2.wmemory2", self.query_value, "MEAS:DEL? WMEM2,CHAN2"),
            ("measure.duty.ch2", self.query_value, "MEAS:DUTY? CHAN2"),
            ("measure.fall_time.ch2", self.query_value, "MEAS:FALL? CHAN2"),
            ("measure.frequency.ch2", self.query_value, "MEAS:FREQ? CHAN2"),
            ("measure.cnt_edge_rising.ch2", self.query_value, "MEAS:NEDG? CHAN2"),
            ("measure.cnt_edge_falling.ch2", self.query_value, "MEAS:PEDG? CHAN2"),
            ("measure.cnt_pulse_positive.ch2", self.query_value, "MEAS:NPUL? CHAN2"),
            ("measure.cnt_pulse_negative.ch2", self.query_value, "MEAS:PPUL? CHAN2"),
            ("measure.period.ch2", self.query_value, "MEAS:PER? CHAN2"),
            ("measure.phase.ch2.ch1", self.query_value, "MEAS:PHAS? CHAN2,CHAN1"),
            ("measure.phase.ch2.ch2", self.query_value, "MEAS:PHAS? CHAN2,CHAN2"),
            ("measure.phase.ch2.ch3", self.query_value, "MEAS:PHAS? CHAN2,CHAN3"),
            ("measure.phase.ch2.ch4", self.query_value, "MEAS:PHAS? CHAN2,CHAN4"),
            ("measure.phase.ch2.function", self.query_value, "MEAS:PHAS? CHAN2,FUNC"),
            ("measure.phase.ch2.math", self.query_value, "MEAS:PHAS? CHAN2,MATH"),
            ("measure.phase.ch2.wmemory1", self.query_value, "MEAS:PHAS? CHAN2,WMEM1"),
            ("measure.phase.ch2.wmemory2", self.query_value, "MEAS:PHAS? CHAN2,WMEM2"),
            ("measure.pulse_width.ch2", self.query_value, "MEAS:PWID? CHAN2"),
            ("measure.vamplitude.ch2", self.query_value, "MEAS:VAMP? CHAN2"),
            ("measure.vaverage.cycle.ch2", self.query_value, "MEAS:VAV? CYCL,CHAN2"),
            ("measure.vaverage.display.ch2", self.query_value, "MEAS:VAV? DISP,CHAN2"),
            ("measure.vbase.ch2", self.query_value, "MEAS:VBAS? CHAN2"),
            ("measure.vmax.ch2", self.query_value, "MEAS:VMAX? CHAN2"),
            ("measure.vmin.ch2", self.query_value, "MEAS:VMIN? CHAN2"),
            ("measure.vpp.ch2", self.query_value, "MEAS:VPP? CHAN2"),
            ("measure.vratio.cycle.ch2.ch1", self.query_value, "MEAS:VRAT? CYCL,CHAN2,CHAN2"),
            ("measure.vratio.cycle.ch2.ch2", self.query_value, "MEAS:VRAT? CYCL,CHAN2,CHAN2"),
            ("measure.vratio.cycle.ch2.ch3", self.query_value, "MEAS:VRAT? CYCL,CHAN2,CHAN3"),
            ("measure.vratio.cycle.ch2.ch4", self.query_value, "MEAS:VRAT? CYCL,CHAN2,CHAN4"),
            ("measure.vratio.cycle.ch2.function", self.query_value, "MEAS:VRAT? CYCL,CHAN2,FUNC"),
            ("measure.vratio.cycle.ch2.math", self.query_value, "MEAS:VRAT? CYCL,CHAN2,MATH"),
            ("measure.vratio.cycle.ch2.wmemory1", self.query_value, "MEAS:VRAT? CYCL,CHAN2,WMEM1"),
            ("measure.vratio.cycle.ch2.wmemory2", self.query_value, "MEAS:VRAT? CYCL,CHAN2,WMEM2"),
            ("measure.vratio.display.ch2.ch2", self.query_value, "MEAS:VRAT? DISP,CHAN2,CHAN2"),
            ("measure.vratio.display.ch2.ch2", self.query_value, "MEAS:VRAT? DISP,CHAN2,CHAN2"),
            ("measure.vratio.display.ch2.ch3", self.query_value, "MEAS:VRAT? DISP,CHAN2,CHAN3"),
            ("measure.vratio.display.ch2.ch4", self.query_value, "MEAS:VRAT? DISP,CHAN2,CHAN4"),
            ("measure.vratio.display.ch2.function", self.query_value, "MEAS:VRAT? DISP,CHAN2,FUNC"),
            ("measure.vratio.display.ch2.math", self.query_value, "MEAS:VRAT? DISP,CHAN2,MATH"),
            ("measure.vratio.display.ch2.wmemory1", self.query_value, "MEAS:VRAT? DISP,CHAN2,WMEM1"),
            ("measure.vratio.display.ch2.wmemory2", self.query_value, "MEAS:VRAT? DISP,CHAN2,WMEM2"),
            ("measure.vrms.dc.cycle.ch2", self.query_value, "MEAS:VRMS? CYCL,DC,CHAN2"),
            ("measure.vrms.dc.display.ch2", self.query_value, "MEAS:VRMS? DISP,DC,CHAN2"),
            ("measure.vrms.ac.cycle.ch2", self.query_value, "MEAS:VRMS? CYCL,AC,CHAN2"),
            ("measure.vrms.ac.display.ch2", self.query_value, "MEAS:VRMS? DISP,AC,CHAN2"),
            ("measure.xmax.ch2", self.query_value, "MEAS:XMAX? CHAN2"),
            ("measure.xmin.ch2", self.query_value, "MEAS:XMIN? CHAN2"),
            # Ch3 Measure
            ("measure.counter.ch3", self.query_value, "MEAS:COUN? CHAN3"),
            ("measure.delay.ch3.ch1", self.query_value, "MEAS:DEL? CHAN3,CHAN1"),
            ("measure.delay.ch3.ch2", self.query_value, "MEAS:DEL? CHAN3,CHAN2"),
            ("measure.delay.ch3.ch3", self.query_value, "MEAS:DEL? CHAN3,CHAN3"),
            ("measure.delay.ch3.ch4", self.query_value, "MEAS:DEL? CHAN3,CHAN4"),
            ("measure.delay.ch3.function", self.query_value, "MEAS:DEL? FUNC,CHAN3"),
            ("measure.delay.ch3.math", self.query_value, "MEAS:DEL? MATH,CHAN3"),
            ("measure.delay.ch3.wmemory1", self.query_value, "MEAS:DEL? WMEM1,CHAN3"),
            ("measure.delay.ch3.wmemory2", self.query_value, "MEAS:DEL? WMEM2,CHAN3"),
            ("measure.duty.ch3", self.query_value, "MEAS:DUTY? CHAN3"),
            ("measure.fall_time.ch3", self.query_value, "MEAS:FALL? CHAN3"),
            ("measure.frequency.ch3", self.query_value, "MEAS:FREQ? CHAN3"),
            ("measure.cnt_edge_rising.ch3", self.query_value, "MEAS:NEDG? CHAN3"),
            ("measure.cnt_edge_falling.ch3", self.query_value, "MEAS:PEDG? CHAN3"),
            ("measure.cnt_pulse_positive.ch3", self.query_value, "MEAS:NPUL? CHAN3"),
            ("measure.cnt_pulse_negative.ch3", self.query_value, "MEAS:PPUL? CHAN3"),
            ("measure.period.ch3", self.query_value, "MEAS:PER? CHAN3"),
            ("measure.phase.ch3.ch1", self.query_value, "MEAS:PHAS? CHAN3,CHAN1"),
            ("measure.phase.ch3.ch2", self.query_value, "MEAS:PHAS? CHAN3,CHAN2"),
            ("measure.phase.ch3.ch3", self.query_value, "MEAS:PHAS? CHAN3,CHAN3"),
            ("measure.phase.ch3.ch4", self.query_value, "MEAS:PHAS? CHAN3,CHAN4"),
            ("measure.phase.ch3.function", self.query_value, "MEAS:PHAS? CHAN3,FUNC"),
            ("measure.phase.ch3.math", self.query_value, "MEAS:PHAS? CHAN3,MATH"),
            ("measure.phase.ch3.wmemory1", self.query_value, "MEAS:PHAS? CHAN3,WMEM1"),
            ("measure.phase.ch3.wmemory2", self.query_value, "MEAS:PHAS? CHAN3,WMEM2"),
            ("measure.pulse_width.ch3", self.query_value, "MEAS:PWID? CHAN3"),
            ("measure.vamplitude.ch3", self.query_value, "MEAS:VAMP? CHAN3"),
            ("measure.vaverage.cycle.ch3", self.query_value, "MEAS:VAV? CYCL,CHAN3"),
            ("measure.vaverage.display.ch3", self.query_value, "MEAS:VAV? DISP,CHAN3"),
            ("measure.vbase.ch3", self.query_value, "MEAS:VBAS? CHAN3"),
            ("measure.vmax.ch3", self.query_value, "MEAS:VMAX? CHAN3"),
            ("measure.vmin.ch3", self.query_value, "MEAS:VMIN? CHAN3"),
            ("measure.vpp.ch3", self.query_value, "MEAS:VPP? CHAN3"),
            ("measure.vratio.cycle.ch3.ch1", self.query_value, "MEAS:VRAT? CYCL,CHAN3,CHAN3"),
            ("measure.vratio.cycle.ch3.ch2", self.query_value, "MEAS:VRAT? CYCL,CHAN3,CHAN2"),
            ("measure.vratio.cycle.ch3.ch3", self.query_value, "MEAS:VRAT? CYCL,CHAN3,CHAN3"),
            ("measure.vratio.cycle.ch3.ch4", self.query_value, "MEAS:VRAT? CYCL,CHAN3,CHAN4"),
            ("measure.vratio.cycle.ch3.function", self.query_value, "MEAS:VRAT? CYCL,CHAN3,FUNC"),
            ("measure.vratio.cycle.ch3.math", self.query_value, "MEAS:VRAT? CYCL,CHAN3,MATH"),
            ("measure.vratio.cycle.ch3.wmemory1", self.query_value, "MEAS:VRAT? CYCL,CHAN3,WMEM1"),
            ("measure.vratio.cycle.ch3.wmemory2", self.query_value, "MEAS:VRAT? CYCL,CHAN3,WMEM2"),
            ("measure.vratio.display.ch3.ch3", self.query_value, "MEAS:VRAT? DISP,CHAN3,CHAN3"),
            ("measure.vratio.display.ch3.ch2", self.query_value, "MEAS:VRAT? DISP,CHAN3,CHAN2"),
            ("measure.vratio.display.ch3.ch3", self.query_value, "MEAS:VRAT? DISP,CHAN3,CHAN3"),
            ("measure.vratio.display.ch3.ch4", self.query_value, "MEAS:VRAT? DISP,CHAN3,CHAN4"),
            ("measure.vratio.display.ch3.function", self.query_value, "MEAS:VRAT? DISP,CHAN3,FUNC"),
            ("measure.vratio.display.ch3.math", self.query_value, "MEAS:VRAT? DISP,CHAN3,MATH"),
            ("measure.vratio.display.ch3.wmemory1", self.query_value, "MEAS:VRAT? DISP,CHAN3,WMEM1"),
            ("measure.vratio.display.ch3.wmemory2", self.query_value, "MEAS:VRAT? DISP,CHAN3,WMEM2"),
            ("measure.vrms.dc.cycle.ch3", self.query_value, "MEAS:VRMS? CYCL,DC,CHAN3"),
            ("measure.vrms.dc.display.ch3", self.query_value, "MEAS:VRMS? DISP,DC,CHAN3"),
            ("measure.vrms.ac.cycle.ch3", self.query_value, "MEAS:VRMS? CYCL,AC,CHAN3"),
            ("measure.vrms.ac.display.ch3", self.query_value, "MEAS:VRMS? DISP,AC,CHAN3"),
            ("measure.xmax.ch3", self.query_value, "MEAS:XMAX? CHAN3"),
            ("measure.xmin.ch3", self.query_value, "MEAS:XMIN? CHAN3"),
            # Ch4 Measure
            ("measure.counter.ch4", self.query_value, "MEAS:COUN? CHAN4"),
            ("measure.delay.ch4.ch1", self.query_value, "MEAS:DEL? CHAN4,CHAN1"),
            ("measure.delay.ch4.ch2", self.query_value, "MEAS:DEL? CHAN4,CHAN2"),
            ("measure.delay.ch4.ch3", self.query_value, "MEAS:DEL? CHAN4,CHAN3"),
            ("measure.delay.ch4.ch4", self.query_value, "MEAS:DEL? CHAN4,CHAN4"),
            ("measure.delay.ch4.function", self.query_value, "MEAS:DEL? FUNC,CHAN4"),
            ("measure.delay.ch4.math", self.query_value, "MEAS:DEL? MATH,CHAN4"),
            ("measure.delay.ch4.wmemory1", self.query_value, "MEAS:DEL? WMEM1,CHAN4"),
            ("measure.delay.ch4.wmemory2", self.query_value, "MEAS:DEL? WMEM2,CHAN4"),
            ("measure.duty.ch4", self.query_value, "MEAS:DUTY? CHAN4"),
            ("measure.fall_time.ch4", self.query_value, "MEAS:FALL? CHAN4"),
            ("measure.frequency.ch4", self.query_value, "MEAS:FREQ? CHAN4"),
            ("measure.cnt_edge_rising.ch4", self.query_value, "MEAS:NEDG? CHAN4"),
            ("measure.cnt_edge_falling.ch4", self.query_value, "MEAS:PEDG? CHAN4"),
            ("measure.cnt_pulse_positive.ch4", self.query_value, "MEAS:NPUL? CHAN4"),
            ("measure.cnt_pulse_negative.ch4", self.query_value, "MEAS:PPUL? CHAN4"),
            ("measure.period.ch4", self.query_value, "MEAS:PER? CHAN4"),
            ("measure.phase.ch4.ch1", self.query_value, "MEAS:PHAS? CHAN4,CHAN1"),
            ("measure.phase.ch4.ch2", self.query_value, "MEAS:PHAS? CHAN4,CHAN2"),
            ("measure.phase.ch4.ch3", self.query_value, "MEAS:PHAS? CHAN4,CHAN3"),
            ("measure.phase.ch4.ch4", self.query_value, "MEAS:PHAS? CHAN4,CHAN4"),
            ("measure.phase.ch4.function", self.query_value, "MEAS:PHAS? CHAN4,FUNC"),
            ("measure.phase.ch4.math", self.query_value, "MEAS:PHAS? CHAN4,MATH"),
            ("measure.phase.ch4.wmemory1", self.query_value, "MEAS:PHAS? CHAN4,WMEM1"),
            ("measure.phase.ch4.wmemory2", self.query_value, "MEAS:PHAS? CHAN4,WMEM2"),
            ("measure.pulse_width.ch4", self.query_value, "MEAS:PWID? CHAN4"),
            ("measure.vamplitude.ch4", self.query_value, "MEAS:VAMP? CHAN4"),
            ("measure.vaverage.cycle.ch4", self.query_value, "MEAS:VAV? CYCL,CHAN4"),
            ("measure.vaverage.display.ch4", self.query_value, "MEAS:VAV? DISP,CHAN4"),
            ("measure.vbase.ch4", self.query_value, "MEAS:VBAS? CHAN4"),
            ("measure.vmax.ch4", self.query_value, "MEAS:VMAX? CHAN4"),
            ("measure.vmin.ch4", self.query_value, "MEAS:VMIN? CHAN4"),
            ("measure.vpp.ch4", self.query_value, "MEAS:VPP? CHAN4"),
            ("measure.vratio.cycle.ch4.ch1", self.query_value, "MEAS:VRAT? CYCL,CHAN4,CHAN4"),
            ("measure.vratio.cycle.ch4.ch2", self.query_value, "MEAS:VRAT? CYCL,CHAN4,CHAN2"),
            ("measure.vratio.cycle.ch4.ch3", self.query_value, "MEAS:VRAT? CYCL,CHAN4,CHAN3"),
            ("measure.vratio.cycle.ch4.ch4", self.query_value, "MEAS:VRAT? CYCL,CHAN4,CHAN4"),
            ("measure.vratio.cycle.ch4.function", self.query_value, "MEAS:VRAT? CYCL,CHAN4,FUNC"),
            ("measure.vratio.cycle.ch4.math", self.query_value, "MEAS:VRAT? CYCL,CHAN4,MATH"),
            ("measure.vratio.cycle.ch4.wmemory1", self.query_value, "MEAS:VRAT? CYCL,CHAN4,WMEM1"),
            ("measure.vratio.cycle.ch4.wmemory2", self.query_value, "MEAS:VRAT? CYCL,CHAN4,WMEM2"),
            ("measure.vratio.display.ch4.ch4", self.query_value, "MEAS:VRAT? DISP,CHAN4,CHAN4"),
            ("measure.vratio.display.ch4.ch2", self.query_value, "MEAS:VRAT? DISP,CHAN4,CHAN2"),
            ("measure.vratio.display.ch4.ch3", self.query_value, "MEAS:VRAT? DISP,CHAN4,CHAN3"),
            ("measure.vratio.display.ch4.ch4", self.query_value, "MEAS:VRAT? DISP,CHAN4,CHAN4"),
            ("measure.vratio.display.ch4.function", self.query_value, "MEAS:VRAT? DISP,CHAN4,FUNC"),
            ("measure.vratio.display.ch4.math", self.query_value, "MEAS:VRAT? DISP,CHAN4,MATH"),
            ("measure.vratio.display.ch4.wmemory1", self.query_value, "MEAS:VRAT? DISP,CHAN4,WMEM1"),
            ("measure.vratio.display.ch4.wmemory2", self.query_value, "MEAS:VRAT? DISP,CHAN4,WMEM2"),
            ("measure.vrms.dc.cycle.ch4", self.query_value, "MEAS:VRMS? CYCL,DC,CHAN4"),
            ("measure.vrms.dc.display.ch4", self.query_value, "MEAS:VRMS? DISP,DC,CHAN4"),
            ("measure.vrms.ac.cycle.ch4", self.query_value, "MEAS:VRMS? CYCL,AC,CHAN4"),
            ("measure.vrms.ac.display.ch4", self.query_value, "MEAS:VRMS? DISP,AC,CHAN4"),
            ("measure.xmax.ch4", self.query_value, "MEAS:XMAX? CHAN4"),
            ("measure.xmin.ch4", self.query_value, "MEAS:XMIN? CHAN4"),
            # Function Measure
            ("measure.delay.function.ch1", self.query_value, "MEAS:DEL? FUNC,CHAN1"),
            ("measure.delay.function.ch2", self.query_value, "MEAS:DEL? FUNC,CHAN2"),
            ("measure.delay.function.ch3", self.query_value, "MEAS:DEL? FUNC,CHAN3"),
            ("measure.delay.function.ch4", self.query_value, "MEAS:DEL? FUNC,CHAN4"),
            ("measure.delay.function.function", self.query_value, "MEAS:DEL? FUNC,FUNC"),
            ("measure.delay.function.math", self.query_value, "MEAS:DEL? MATH,FUNC"),
            ("measure.delay.function.wmemory1", self.query_value, "MEAS:DEL? WMEM1,FUNC"),
            ("measure.delay.function.wmemory2", self.query_value, "MEAS:DEL? WMEM2,FUNC"),
            ("measure.duty.function", self.query_value, "MEAS:DUTY? FUNC"),
            ("measure.fall_time.function", self.query_value, "MEAS:FALL? FUNC"),
            ("measure.frequency.function", self.query_value, "MEAS:FREQ? FUNC"),
            ("measure.cnt_edge_rising.function", self.query_value, "MEAS:NEDG? FUNC"),
            ("measure.cnt_edge_falling.function", self.query_value, "MEAS:PEDG? FUNC"),
            ("measure.cnt_pulse_positive.function", self.query_value, "MEAS:NPUL? FUNC"),
            ("measure.cnt_pulse_negative.function", self.query_value, "MEAS:PPUL? FUNC"),
            ("measure.period.function", self.query_value, "MEAS:PER? FUNC"),
            ("measure.phase.function.ch1", self.query_value, "MEAS:PHAS? FUNC,CHAN1"),
            ("measure.phase.function.ch2", self.query_value, "MEAS:PHAS? FUNC,CHAN2"),
            ("measure.phase.function.ch3", self.query_value, "MEAS:PHAS? FUNC,CHAN3"),
            ("measure.phase.function.ch4", self.query_value, "MEAS:PHAS? FUNC,CHAN4"),
            ("measure.phase.function.function", self.query_value, "MEAS:PHAS? FUNC,FUNC"),
            ("measure.phase.function.math", self.query_value, "MEAS:PHAS? FUNC,MATH"),
            ("measure.phase.function.wmemory1", self.query_value, "MEAS:PHAS? FUNC,WMEM1"),
            ("measure.phase.function.wmemory2", self.query_value, "MEAS:PHAS? FUNC,WMEM2"),
            ("measure.pulse_width.function", self.query_value, "MEAS:PWID? FUNC"),
            ("measure.vamplitude.function", self.query_value, "MEAS:VAMP? FUNC"),
            ("measure.vaverage.cycle.function", self.query_value, "MEAS:VAV? CYCL,FUNC"),
            ("measure.vaverage.display.function", self.query_value, "MEAS:VAV? DISP,FUNC"),
            ("measure.vbase.function", self.query_value, "MEAS:VBAS? FUNC"),
            ("measure.vmax.function", self.query_value, "MEAS:VMAX? FUNC"),
            ("measure.vmin.function", self.query_value, "MEAS:VMIN? FUNC"),
            ("measure.vpp.function", self.query_value, "MEAS:VPP? FUNC"),
            ("measure.vratio.cycle.function.ch1", self.query_value, "MEAS:VRAT? CYCL,FUNC,FUNC"),
            ("measure.vratio.cycle.function.ch2", self.query_value, "MEAS:VRAT? CYCL,FUNC,CHAN2"),
            ("measure.vratio.cycle.function.ch3", self.query_value, "MEAS:VRAT? CYCL,FUNC,CHAN3"),
            ("measure.vratio.cycle.function.ch4", self.query_value, "MEAS:VRAT? CYCL,FUNC,CHAN4"),
            ("measure.vratio.cycle.function.function", self.query_value, "MEAS:VRAT? CYCL,FUNC,FUNC"),
            ("measure.vratio.cycle.function.math", self.query_value, "MEAS:VRAT? CYCL,FUNC,MATH"),
            ("measure.vratio.cycle.function.wmemory1", self.query_value, "MEAS:VRAT? CYCL,FUNC,WMEM1"),
            ("measure.vratio.cycle.function.wmemory2", self.query_value, "MEAS:VRAT? CYCL,FUNC,WMEM2"),
            ("measure.vratio.display.function.function", self.query_value, "MEAS:VRAT? DISP,FUNC,FUNC"),
            ("measure.vratio.display.function.ch2", self.query_value, "MEAS:VRAT? DISP,FUNC,CHAN2"),
            ("measure.vratio.display.function.ch3", self.query_value, "MEAS:VRAT? DISP,FUNC,CHAN3"),
            ("measure.vratio.display.function.ch4", self.query_value, "MEAS:VRAT? DISP,FUNC,CHAN4"),
            ("measure.vratio.display.function.function", self.query_value, "MEAS:VRAT? DISP,FUNC,FUNC"),
            ("measure.vratio.display.function.math", self.query_value, "MEAS:VRAT? DISP,FUNC,MATH"),
            ("measure.vratio.display.function.wmemory1", self.query_value, "MEAS:VRAT? DISP,FUNC,WMEM1"),
            ("measure.vratio.display.function.wmemory2", self.query_value, "MEAS:VRAT? DISP,FUNC,WMEM2"),
            ("measure.vrms.dc.cycle.function", self.query_value, "MEAS:VRMS? CYCL,DC,FUNC"),
            ("measure.vrms.dc.display.function", self.query_value, "MEAS:VRMS? DISP,DC,FUNC"),
            ("measure.vrms.ac.cycle.function", self.query_value, "MEAS:VRMS? CYCL,AC,FUNC"),
            ("measure.vrms.ac.display.function", self.query_value, "MEAS:VRMS? DISP,AC,FUNC"),
            ("measure.xmax.function", self.query_value, "MEAS:XMAX? FUNC"),
            ("measure.xmin.function", self.query_value, "MEAS:XMIN? FUNC"),
            # MATH,Measure
            ("measure.delay.math.ch1", self.query_value, "MEAS:DEL? MATH,CHAN1"),
            ("measure.delay.math.ch2", self.query_value, "MEAS:DEL? MATH,CHAN2"),
            ("measure.delay.math.ch3", self.query_value, "MEAS:DEL? MATH,CHAN3"),
            ("measure.delay.math.ch4", self.query_value, "MEAS:DEL? MATH,CHAN4"),
            ("measure.delay.math.function", self.query_value, "MEAS:DEL? FUNC,MATH"),
            ("measure.delay.math.math", self.query_value, "MEAS:DEL? MATH,MATH"),
            ("measure.delay.math.wmemory1", self.query_value, "MEAS:DEL? WMEM1,MATH"),
            ("measure.delay.math.wmemory2", self.query_value, "MEAS:DEL? WMEM2,MATH"),
            ("measure.duty.math", self.query_value, "MEAS:DUTY? MATH"),
            ("measure.fall_time.math", self.query_value, "MEAS:FALL? MATH"),
            ("measure.frequency.math", self.query_value, "MEAS:FREQ? MATH"),
            ("measure.cnt_edge_rising.math", self.query_value, "MEAS:NEDG? MATH"),
            ("measure.cnt_edge_falling.math", self.query_value, "MEAS:PEDG? MATH"),
            ("measure.cnt_pulse_positive.math", self.query_value, "MEAS:NPUL? MATH"),
            ("measure.cnt_pulse_negative.math", self.query_value, "MEAS:PPUL? MATH"),
            ("measure.period.math", self.query_value, "MEAS:PER? MATH"),
            ("measure.phase.math.ch1", self.query_value, "MEAS:PHAS? MATH,CHAN1"),
            ("measure.phase.math.ch2", self.query_value, "MEAS:PHAS? MATH,CHAN2"),
            ("measure.phase.math.ch3", self.query_value, "MEAS:PHAS? MATH,CHAN3"),
            ("measure.phase.math.ch4", self.query_value, "MEAS:PHAS? MATH,CHAN4"),
            ("measure.phase.math.function", self.query_value, "MEAS:PHAS? MATH,FUNC"),
            ("measure.phase.math.math", self.query_value, "MEAS:PHAS? MATH,MATH"),
            ("measure.phase.math.wmemory1", self.query_value, "MEAS:PHAS? MATH,WMEM1"),
            ("measure.phase.math.wmemory2", self.query_value, "MEAS:PHAS? MATH,WMEM2"),
            ("measure.pulse_width.math", self.query_value, "MEAS:PWID? MATH"),
            ("measure.vamplitude.math", self.query_value, "MEAS:VAMP? MATH"),
            ("measure.vaverage.cycle.math", self.query_value, "MEAS:VAV? CYCL,MATH"),
            ("measure.vaverage.display.math", self.query_value, "MEAS:VAV? DISP,MATH"),
            ("measure.vbase.math", self.query_value, "MEAS:VBAS? MATH"),
            ("measure.vmax.math", self.query_value, "MEAS:VMAX? MATH"),
            ("measure.vmin.math", self.query_value, "MEAS:VMIN? MATH"),
            ("measure.vpp.math", self.query_value, "MEAS:VPP? MATH"),
            ("measure.vratio.cycle.math.ch1", self.query_value, "MEAS:VRAT? CYCL,MATH,MATH"),
            ("measure.vratio.cycle.math.ch2", self.query_value, "MEAS:VRAT? CYCL,MATH,CHAN2"),
            ("measure.vratio.cycle.math.ch3", self.query_value, "MEAS:VRAT? CYCL,MATH,CHAN3"),
            ("measure.vratio.cycle.math.ch4", self.query_value, "MEAS:VRAT? CYCL,MATH,CHAN4"),
            ("measure.vratio.cycle.math.function", self.query_value, "MEAS:VRAT? CYCL,MATH,FUNC"),
            ("measure.vratio.cycle.math.math", self.query_value, "MEAS:VRAT? CYCL,MATH,MATH"),
            ("measure.vratio.cycle.math.wmemory1", self.query_value, "MEAS:VRAT? CYCL,MATH,WMEM1"),
            ("measure.vratio.cycle.math.wmemory2", self.query_value, "MEAS:VRAT? CYCL,MATH,WMEM2"),
            ("measure.vratio.display.math.math", self.query_value, "MEAS:VRAT? DISP,MATH,MATH"),
            ("measure.vratio.display.math.ch2", self.query_value, "MEAS:VRAT? DISP,MATH,CHAN2"),
            ("measure.vratio.display.math.ch3", self.query_value, "MEAS:VRAT? DISP,MATH,CHAN3"),
            ("measure.vratio.display.math.ch4", self.query_value, "MEAS:VRAT? DISP,MATH,CHAN4"),
            ("measure.vratio.display.math.function", self.query_value, "MEAS:VRAT? DISP,MATH,FUNC"),
            ("measure.vratio.display.math.math", self.query_value, "MEAS:VRAT? DISP,MATH,MATH"),
            ("measure.vratio.display.math.wmemory1", self.query_value, "MEAS:VRAT? DISP,MATH,WMEM1"),
            ("measure.vratio.display.math.wmemory2", self.query_value, "MEAS:VRAT? DISP,MATH,WMEM2"),
            ("measure.vrms.dc.cycle.math", self.query_value, "MEAS:VRMS? CYCL,DC,MATH"),
            ("measure.vrms.dc.display.math", self.query_value, "MEAS:VRMS? DISP,DC,MATH"),
            ("measure.vrms.ac.cycle.math", self.query_value, "MEAS:VRMS? CYCL,AC,MATH"),
            ("measure.vrms.ac.display.math", self.query_value, "MEAS:VRMS? DISP,AC,MATH"),
            ("measure.xmax.math", self.query_value, "MEAS:XMAX? MATH"),
            ("measure.xmin.math", self.query_value, "MEAS:XMIN? MATH"),
        ]
        self.init_api()
        self.instrument.timeout = 1000

    def _write(self, value):
        self.instrument.write(value)
        self._raise_if_error()

    def acquire(self, acquire_type="normal", averaging_samples=0):
        """
        :param channel
         string indicating the channel eg. 1, 2, 3, 4, FUNC,(FUNC,includes MATH,functions)
        :param acquire_type:
         "normal"
         "averaging"
         "hresolution" - High Resolution
         "peak" - Peak Detect
        :param averaging_samples:
         averaging_samples: number of samples used when acquire_type is set to averaging
        :return:
        """
        self.write("TIMebase:MODE MAIN")
        if acquire_type.lower() == "normal":
            self.write(":ACQuire:TYPE normal")
        elif acquire_type.lower() == "averaging":
            self.write(":ACQuire:TYPE average")
            self.write(":ACQuire:COUNt {}".format(averaging_samples))
        elif acquire_type.lower() == "hresolution":
            self.write(":ACQuire:TYPE hresolution")
        elif acquire_type.lower() == "peak":
            self.write(":ACQuire:TYPE peak")
        else:
            raise ValueError("Invalid acquire type {}".format(acquire_type))

    def waveform_preamble(self):
        values = self.query_ascii_values(":WAV:PRE?")
        wav_form_dict = {"0": "BYTE",
                         "1": "WORD",
                         "4": "ASCii"}
        acq_type_dict = {"0": "NORMAL",
                         "1": "PEAK",
                         "2": "AVERAGE",
                         "3": "HIGH RESOLUTION"}
        labels = ["format", "acquire", "wav_points", "avg_cnt", "x_increment", "x_origin", "x_reference", "y_increment",
                  "y_origin", "y_reference"]
        preamble = {}
        for index, val in enumerate(values):
            if index == 0:
                preamble["format"] = wav_form_dict[str(int(values[0]))]
            elif index == 1:
                preamble["acquire"] = acq_type_dict[str(int(values[1]))]
            else:
                preamble[labels[index]] = val
        return preamble

    def waveform_values(self, signals, file_name='', file_type='csv'):
        """
        :param signals:
         The channel ie "1", "2", "3", "4", "MATH", "FUNC"
        :param file_name:
         If
        :param file_type:
        :return:
        """
        signals = self.digitize(signals)
        return_vals = {}
        for sig in signals:
            return_vals[sig] = []
            results = return_vals[sig]
            self.write(":WAV:SOUR {}".format(sig))
            self.write(":WAV:FORM BYTE")
            self.write(":WAV:POIN:MODE RAW")
            preamble = self.waveform_preamble()
            data = self.retrieve_waveform_data()
            for index, datum in enumerate(data):
                time_val = index * preamble["x_increment"]
                y_val = preamble["y_origin"] + (datum - preamble["y_reference"]) * preamble["y_increment"]
                results.append((time_val, y_val))
        if file_name and file_type == 'csv':  # Needs work for multiple references
            with open(file_name, 'w') as f:
                f.write("x,y")
                for label in sorted(preamble):
                    f.write(",{},{}".format(label, preamble[label]))
                f.write('\n')
                for time_val, y_val in enumerate(results):
                    f.write("{time_val},{voltage}\n".format(time_val=time_val, voltage=y_val))
        elif file_name and file_type == 'bin':
            raise NotImplemented("Binary Output not implemented")
        return results

    def retrieve_waveform_data(self):
        self.instrument.write(":WAV:DATA?")
        time.sleep(0.2)
        data = self.read_raw()[:-1]  # Strip \n
        if data[0:1] != '#'.encode():
            raise InstrumentError("Pound Character missing in waveform data response")
        valid_bytes = data[int(data[1:2]) + 2:]  # data[1] denotes length value digits
        values = struct.unpack("%dB" % len(valid_bytes), valid_bytes)
        return values

    def digitize(self, signals):
        signals = [self.validate_signal(sig) for sig in signals]
        self.write(":DIG {}".format(','.join(signals)))
        return signals

    def validate_signal(self, signal):
        """
        :param signal: String ie. "1", "2", "3", "4", "func", "math"
        :return:
        """
        try:
            if not (1 <= int(signal) <= 4):
                raise ValueError("Invalid source channel {}".format(signal))
            else:
                signal = "CHAN{}".format(int(signal))
        except ValueError:
            if signal.lower() not in ["func", "math"]:
                raise ValueError("Invalid source channel {}".format(signal))
            signal = signal.lower()
        return signal

    def reset(self):
        self.write("*CLS")
        self.write("*RST")

    def auto_scale(self):
        self.write(":AUT")

    def save_setup(self, file_name):
        self.instrument.timeout = 5000
        try:
            with open(file_name, 'w') as f:
                setup = self.query(":SYSTem:SETup?")
                f.write(setup)
        finally:
            self.instrument.timeout = 1000

    def load_setup(self, file_name):
        self.instrument.timeout = 5000
        try:
            with open(file_name, 'r') as f:
                setup = f.read()
            self.write(":SYSTem:SETup {}".format(setup))
        finally:
            self.instrument.timeout = 1000

    def query(self, value):
        try:
            response = self.instrument.query(value)
        finally:
            self._raise_if_error()
        return response

    def query_bool(self, value):
        return bool(self.query_ascii_value(value))

    def query_binary_values(self, value):
        response = self.instrument.query_binary_values(value)
        self._raise_if_error()
        return response

    def query_ascii_values(self, value):
        response = self.instrument.query_ascii_values(value)
        self._raise_if_error()
        return response

    def query_ascii_value(self, value):
        return self.query_ascii_values(value)[0]

    def query_value(self, base_str, *args, **kwargs):
        formatted_string = self._format_string(base_str, **kwargs)
        return self.query_ascii_value(formatted_string)

    def read_raw(self):
        data = self.instrument.read_raw()
        self._raise_if_error()
        return data

    def _check_errors(self):
        resp = self.instrument.query("SYST:ERR?")
        code, msg = resp.strip('\n').split(',')
        code = int(code)
        msg = msg.strip('"')
        return code, msg

    def _raise_if_error(self):
        errors = []
        while True:
            code, msg = self._check_errors()
            if code != 0:
                errors.append((code, msg))
            else:
                break
        if errors:
            raise InstrumentError("Error(s) Returned from DSO\n" +
                                  "\n".join(["Code: {}\nMessage:{}".format(code, msg) for code, msg in errors]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.instrument.close()
        self.is_connected = False

    def write(self, base_str, *args, **kwargs):
        formatted_string = self._format_string(base_str, **kwargs)
        self._write(formatted_string)

    def _format_string(self, base_str, **kwargs):
        kwargs['self'] = self
        prev_string = base_str
        cur_string = ""
        while True:
            cur_string = prev_string.format(**kwargs)
            if cur_string == prev_string:
                break
            prev_string = cur_string
        return cur_string

    def store(self, store_dict, *args, **kwargs):
        """
        Store a dictionary of values in TestClass
        :param kwargs:
        Dictionary containing the parameters to store
        :return:
        """
        new_dict = store_dict.copy()
        for k, v in store_dict.items():
            # I want the same function from write to set up the string before putting it in new_dict
            try:
                new_dict[k] = v.format(**kwargs)
            except:
                pass
        self._store.update(new_dict)

    def store_and_write(self, params, *args, **kwargs):
        base_str, store_dict = params
        self.store(store_dict)
        self.write(base_str, *args, **kwargs)
