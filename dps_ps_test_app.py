from ScopeFoundry import BaseMicroscopeApp

class DPSPowerSupplyTestApp(BaseMicroscopeApp):
    
    name = 'dps_powersupply_app'
    
    def setup(self):
        from ScopeFoundryHW.dps3005_powersupply.dps_ps_hw import DPSPowerSupplyHW
        hw = self.add_hardware(DPSPowerSupplyHW)
        
        # from ScopeFoundryHW.oceanoptics_spec import OOSpecLive
        # self.add_measurement(OOSpecLive(self))
                
if __name__ == '__main__':
    import sys
    app = DPSPowerSupplyTestApp(sys.argv)
    app.exec_()