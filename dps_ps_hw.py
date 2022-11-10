from ScopeFoundry import HardwareComponent
import time
import threading

class DPSPowerSupplyHW(HardwareComponent):
    
    name = 'dps_powersupply'
    
    def setup(self):
        
        self.settings.New('port', dtype=str, initial='COM4')
        
        
        self.settings.New('v_set', dtype=float, ro=False, unit='V', spinbox_decimals=3)
        self.settings.New('i_set', dtype=float, ro=False, unit='A', spinbox_decimals=3)
        self.settings.New('v_out', dtype=float, ro=True, unit='V', spinbox_decimals=3)
        self.settings.New('i_out', dtype=float, ro=True, unit='A', spinbox_decimals=3)
        self.settings.New('pow_out', dtype=float, ro=True, unit='W', spinbox_decimals=3)
        self.settings.New('v_supply', dtype=float, ro=True, unit='V', spinbox_decimals=3)
        self.settings.New('key_lock', dtype=bool, ro=False)
        self.settings.New('protect', dtype=bool, ro=False)
        self.settings.New('compliance', dtype=str, ro=True, choices=('?','CV', 'CC'))
        self.settings.New('output_enable', dtype=bool, ro=False)
        self.settings.New('disp_bright', dtype=int, vmin=0, vmax=5, ro=False) # LED Brightness (0-5)
        self.settings.New('model', dtype=int, ro=True)
        self.settings.New('firmware', dtype=int, ro=True)
        
        
        
    def connect(self):
        
        self.tlock = threading.Lock()
        
        # Note each register read takes about 350ms, so its better
        # to read all parameters with a single read
        
        S = self.settings
        
        import minimalmodbus
        
        self.dev = dev= minimalmodbus.Instrument(S['port'], 1)
        
        dev.serial.baudrate = 9600
        dev.serial.bytesize = 8
        dev.serial.timeout = 0.5
        dev.mode = minimalmodbus.MODE_RTU
        

        S.v_set.connect_to_hardware(
            #read_func=self.read_v_set,
            write_func=self.write_v_set,
            )
        S.i_set.connect_to_hardware(
            #read_func=self.read_i_set,
            write_func=self.write_i_set,
            )        
        S.v_out.connect_to_hardware(
            #read_func=self.read_v_out
            )
        S.i_out.connect_to_hardware(
            #read_func=self.read_i_out
            )
        S.pow_out.connect_to_hardware(
            #read_func=self.read_power_out
            )
        S.v_supply.connect_to_hardware(
            #read_func=self.read_v_supply
            )
        S.key_lock.connect_to_hardware(
            #read_func=self.read_key_lock,
            write_func=self.write_key_lock
            )
        S.protect.connect_to_hardware(
            #read_func=self.read_protect_status
            )
        S.compliance.connect_to_hardware(
            #read_func=self.read_cv_cc_status
            )
        S.output_enable.connect_to_hardware(
            #read_func=self.read_output_enable,
            write_func=self.write_output_enable
            )

        
        
        S['model'] = self.read_model()
        S['firmware'] = self.read_firmware_version()
        
        self.read_state()
    
    
    reg_table = [
        ('v_set', 2), # lq name, decimals #reg 0x00
        ('i_set', 3), 
        ('v_out', 2),
        ('i_out', 3),
        ('pow_out', 2),
        ('v_supply',2),
        ('key_lock',0),
        ('protect',0),
        (None,0), # compliance is a special case
        ('output_enable',0),
        ('disp_bright',0),
        ]
    
    def read_state(self):
        with self.tlock:
            x = self.dev.read_registers(0, 13)
        print(x)
        
        for i, (lq_name, decimals) in enumerate(self.reg_table):
            #print (i, lq_name,decimals)
            if lq_name is None:
                continue
            self.settings[lq_name] = x[i]*10**-decimals
        
        print(x[0x08])
        self.settings['compliance'] = ('CV', 'CC')[bool(x[0x08])]
        
        
    def disconnect(self):
        #disconnect logged quantities from hardware
        self.settings.disconnect_all_from_hardware()

        if hasattr(self, 'dev'):
            #disconnect hardware
            self.dev.serial.close()

            # clean up hardware object
            del self.dev
    
    def threaded_update(self):
        self.read_state()
        time.sleep(3.0)
        
    def read_v_set(self):
        with self.tlock:
            return self.dev.read_register(0x00, 2)
    def write_v_set(self,v):
        with self.tlock:
            return self.dev.write_register(0x00, v, 2)
    
    def read_i_set(self):
        with self.tlock:
            return self.dev.read_register(0x01, 3)
    def write_i_set(self, i):
        with self.tlock:
            return self.dev.write_register(0x01, i, 3)
       
    def read_v_out(self):
        with self.tlock:
            return self.dev.read_register(0x02, 2)
    
    def read_i_out(self):
        with self.tlock:
            return self.dev.read_register(0x03, 3)

    def read_power_out(self):
        with self.tlock:
            return self.dev.read_register(0x04, 2)
            
    def read_v_supply(self):
        with self.tlock:
            return self.dev.read_register(0x05, 2) # Watts
    
    def read_key_lock(self):
        with self.tlock:
            return bool(
                self.dev.read_register(0x06, 0))
    def write_key_lock(self, lock):
        with self.tlock:
            self.dev.write_register(0x06, bool(lock), 0)
        
    def read_protect_status(self):
        with self.tlock:
            return bool(
                self.dev.read_register(0x07, 0))

    def read_cv_cc_status(self):
        with self.tlock:
            x = bool(self.dev.read_register(0x08, 0))
        return ('CV', 'CC')[x]
    
    def read_output_enable(self):
        with self.tlock:
            return bool(
                self.dev.read_register(0x09, 0))
    def write_output_enable(self, enable):
        with self.tlock:
            self.dev.write_register(0x09, bool(enable), 0)

    def read_display_brightness(self):
        with self.tlock:
            return self.dev.read_register(0x0A, 0)   

    def read_model(self):
        with self.tlock:
            return self.dev.read_register(0x0B, 0)   

    def read_firmware_version(self):
        with self.tlock:
            return self.dev.read_register(0x0C, 0)
