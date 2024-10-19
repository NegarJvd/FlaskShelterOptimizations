import math

class LoadCaluculator: 
    def __init__(self, material, footprint):
        self.material = material
        self.footprint = footprint

        # Inputs for dead load calculation
        self.rho = self.material.get('density') or 450       #The density of the slab material (kg/m³): "))
        self.T_sl = self.footprint.get('slab_thickness') or 0.2       #The thickness of the slab (m): "))
        self.W_sl = self.footprint.get('width') or 2         #Enter the width of the slab (m): "))
        self.L_sl = self.footprint.get('length') or 4         #"Enter the length of the slab (m): "))
        
        # Get the wind load inputs
        self.h = self.footprint.get('height') or 2           #Enter the height of the building h (m): "))
        self.n =  self.footprint.get('column_number') or 6          #"Enter the number of columns n: "))
        
        self.z0 = 0.3        #Enter the roughness length (z0) in meters: "))
        self.c0 = 1          #"Enter the orography factor (c0): "))
        self.vb0 = 24        #"Enter the basic wind speed (vb0) in m/s: "))
        self.altitude = 2     #"Enter the altitude of the site: "))
        self.s_g = 1          #"Enter the Characteristic value of snow load (s.g): "))


    # Functions from the first code
    def calculate_kr(self, z0):
        z0_II = 0.05  # Fixed reference roughness length in meters
        return 0.19 * (z0 / z0_II)**0.07

    def calculate_cr(self, kr, z, z0):
        return kr * math.log(z / z0)

    def calculate_turbulence_intensity(self, k1, c0, z, z0):
        if z0 <= 0 or z <= z0:
            raise ValueError("z must be greater than z0 and z0 must be positive")
        return k1 / (c0 * math.log(z / z0))

    def calculate_mean_wind_velocity(self, kr, c0, vb0, z, z0):
        cr = self.calculate_cr(kr, z, z0)
        return cr * c0 * vb0

    def calculate_peak_wind_velocity_pressure(self, Iv, rho, vm):
        qp = ((1 + 7 * Iv) * 0.5 * rho * vm ** 2)/1000
        return qp

    def calculate_wind_pressure(self, qp, b, d, h):
        e = min(b, 2 * h)
        if e > 5 * d:
            A_width = d
            B_width = 0
            C_width = 0
        elif e > d:
            A_width = e / 5
            B_width = (d - e) / 5
            C_width = 0
        else:
            A_width = e / 5
            B_width = e * (4 / 5)
            C_width = d - e

        h_d_ratio = h / d
        if h_d_ratio >= 5:
            cpe_values = {'A': -1.2, 'B': -0.8, 'C': -0.5, 'D': 0.8, 'E': -0.7}
        elif 1 <= h_d_ratio < 5:
            cpe_values = {'A': -1.2, 'B': -0.8, 'C': -0.5, 'D': 0.8, 'E': -0.5}
        elif 0.25 <= h_d_ratio < 1:
            cpe_values = {'A': -1.2, 'B': -0.8, 'C': -0.5, 'D': 0.7, 'E': -0.3}
        else:
            raise ValueError("h/d ratio out of range for defined cpe values")

        We_results = {}
        areas = ['A', 'B', 'C', 'D', 'E']
        for area in areas:
            We_results[area] = qp * cpe_values[area]

        return We_results, {'A_width': A_width, 'B_width': B_width, 'C_width': C_width}

    def calculate_loads(self, We_direct, We_side, widths, h, d, n):
        max_pressures = {}
        areas = ['A', 'B', 'C', 'D', 'E']
        for area in areas:
            max_pressures[area] = max(We_direct[area], We_side[area])
        
        load_on_beam = (max(max_pressures.values()) * h) / 2
        load_on_column = max(
            max_pressures['A'] * widths['A_width'],
            max_pressures['B'] * widths['B_width'],
            max_pressures['C'] * widths['C_width'],
            max_pressures['D'] * d,
            max_pressures['E'] * d
        ) / (n / 2)

        return load_on_beam

    def calculate_loads_clm(self, We_direct, We_side, widths, h, d, n):
        max_pressures = {}
        areas = ['A', 'B', 'C', 'D', 'E']
        for area in areas:
            max_pressures[area] = max(We_direct[area], We_side[area])
        
        load_on_column = max(
            max_pressures['A'] * widths['A_width'],
            max_pressures['B'] * widths['B_width'],
            max_pressures['C'] * widths['C_width'],
            max_pressures['D'] * d,
            max_pressures['E'] * d
        ) / (n / 2)

        return load_on_column

    def calculate_dead_load(self, rho, T_sl, W_sl, L_sl):
        volume = W_sl * L_sl * T_sl
        mass = volume * rho
        g = 9.81
        weight = mass * g
        
        dead_load_per_meter = (weight / L_sl) / 2 / 1000
        
        return dead_load_per_meter

    def calculate_dead_load_clm(self, rho, T_sl, W_sl, L_sl, n):
        volume = W_sl * L_sl * T_sl
        mass = volume * rho
        g = 9.81
        weight = mass * g
        
        dead_load_per_meter_clm= (weight / n)  / 1000
        
        return dead_load_per_meter_clm

    def calculate_Live_load(self, W_sl, L_sl):
        Live_load = (1.5)* (W_sl * L_sl)  # Assume a live load of 1.5 kN/m²
        qk = (Live_load / L_sl) / 2 / 1000
        return qk

    def calculate_Live_load_clm(self, W_sl, L_sl,n):
        Live_load = (1.5)* (W_sl * L_sl)  # Assume a live load of 1.5 kN/m²
        qk_clm = (Live_load / n) / 1000
        return qk_clm

    def calculate_snow_load(self, W_sl,L_sl):
        M_i = 0.8  # Snow load shape coefficient
        Ce = 1.0   # Exposure coefficient
        Ct = 1.0   # Thermal coefficient

        snow_load = ((M_i * Ce * Ct * self.s_g)*(W_sl * L_sl))
        sk= ((snow_load)/ L_sl)/2
        return sk

    def calculate_snow_load_clm(self, W_sl,L_sl,n):
        M_i = 0.8  # Snow load shape coefficient
        Ce = 1.0   # Exposure coefficient
        Ct = 1.0   # Thermal coefficient

        snow_load = ((M_i * Ce * Ct * self.s_g)*(W_sl * L_sl))
        sk_clm= ((snow_load)/ n)
        return sk_clm
        
    ########################################calculating results########################################
    
    def Beam_load_combinations(self):
        # Constants
        γ_g = 1.35
        γ_q = 1.5
        Ψ_0_q = 0
        Ψ_0_w = 0.6

        

        if self.altitude > 1000:
            height = 2
        else:
            height = 1

        if height == 1:
            Ψ_0_s = 0.7 
        else:
            Ψ_0_s = 0.5 


        gk = 2.3*self.calculate_dead_load(self.rho, self.T_sl, self.W_sl, self.L_sl)
        

        qk = self.calculate_Live_load(self.W_sl, self.L_sl)
        


        sk= 3.5*self.calculate_snow_load(self.W_sl, self.L_sl)

        # Get the wind load inputs
        z = self.h       #input("Enter the height at which the wind speed is considered (z) in (m)
        b = self.W_sl    #input("Enter the width of the building b (m)
        d = self.L_sl    #input("Enter the length of the building d (m)
    

        # Calculating kr, Iv, Vm, and qp using the first code's functions
        kr = self.calculate_kr(self.z0)
        Iv = self.calculate_turbulence_intensity(1, self.c0, z, self.z0)
        vm = self.calculate_mean_wind_velocity(kr, self.c0, self.vb0, z, self.z0)
        qp = self.calculate_peak_wind_velocity_pressure(Iv, 1.25, vm)  # rho is 1.25 kg/m^3
        

        # Calculate for direct wind
        We_direct, widths_direct = self.calculate_wind_pressure(qp, b, d, self.h)
        

        # Calculate for side wind (just swapping b and d)
        We_side, widths_side = self.calculate_wind_pressure(qp, d, b, self.h)
        

        # Calculate wind loads
        wk = (5*self.calculate_loads(We_direct, We_side, widths_direct, self.h, d, self.n))
        
        

        ULS_category1 = [γ_g * gk]
        ULS_category2 = [
            (γ_g * gk) + (γ_q * qk),
            (γ_g * gk) + (γ_q * qk) + (Ψ_0_s * γ_q * sk),
            (γ_g * gk) + (γ_q * qk) + (Ψ_0_w * γ_q * wk)
        ]
        ULS_category3 = [
            (γ_g * gk) + (γ_q * qk) + (Ψ_0_s * γ_q * sk) + (Ψ_0_w * γ_q * wk),
            (γ_g * gk) + (Ψ_0_q * γ_q * qk) + (γ_q * sk) + (Ψ_0_w * γ_q * wk),
            (γ_g * gk) + (Ψ_0_q * γ_q * qk) + (Ψ_0_s * γ_q * sk) + (γ_q * wk),
            (γ_g * gk) + (γ_q * sk),
            (γ_g * gk) + (γ_q * wk),
            (γ_g * gk) + (γ_q * sk) + (Ψ_0_w * γ_q * wk),
            (γ_g * gk) + (γ_q * wk) + (Ψ_0_s * γ_q * sk),
            (γ_g * gk) + (Ψ_0_q * γ_q * qk) + (γ_q * sk),
            (γ_g * gk) + (Ψ_0_q * γ_q * qk) + (γ_q * wk)
        ]
        max_category1 = max(ULS_category1)
        max_category2 = max(ULS_category2)
        max_category3 = max(ULS_category3)
        
        SLS_combinations = [
            gk,
            gk + qk,
            gk + qk + Ψ_0_s * sk,
            gk + qk + Ψ_0_w * wk,
            gk + qk + Ψ_0_s * sk + Ψ_0_w * wk,
            gk + Ψ_0_q * qk + sk + Ψ_0_w * wk,
            gk + Ψ_0_q * qk + Ψ_0_s * sk + wk,
            gk + sk,
            gk + wk,
            gk + sk + Ψ_0_w * wk,
            gk + wk + Ψ_0_s * sk,
            gk + Ψ_0_q * qk + sk,
            gk + Ψ_0_q * qk + wk
        ]
        max_SLS = max(SLS_combinations)
        
        Lead_varbl = max(qk, sk, wk)
        
        if Lead_varbl == qk:
            psi_lead = 0
        elif Lead_varbl == sk:
            if height == 1:
                psi_lead = 0.2
            else:
                psi_lead = 0.5
        elif Lead_varbl == wk:
            psi_lead = 0.2

        values = [qk, sk, wk]
        values.remove(Lead_varbl)
        acmp_varbl = max(values)

        if acmp_varbl == qk:
            psi_acmp = 0
        elif acmp_varbl == sk:
            if height == 1:
                psi_acmp = 0
            else:
                psi_acmp = 0.2
        elif acmp_varbl == wk:
            psi_acmp = 0


        ########################################calculated results########################################
        results = {
            "P_L": {
                'print_value': f"Maximum load for ULS Category 1 (Permanent): {max_category1:.2f} kN/m",
                'value': round(max_category1, 2)
            },
            "M_L": {
                'print_value': f"Maximum load for ULS Category 2 (Medium-term): {max_category2:.2f} kN/m",
                'value': round(max_category2, 2)
            },
            "I_L": {
                'print_value': f"Maximum load for ULS Category 3 (Instantaneous): {max_category3:.2f} kN/m",
                'value': round(max_category3, 2)
            },
            "SLS_L": {
                'print_value': f"Maximum load for SLS: {max_SLS:.2f} kN/m",
                'value': round(max_SLS, 2)
            },
            "g_lead": {
                'print_value': f"Leading variable action: {Lead_varbl:.2f} kN/m",
                'value': round(Lead_varbl, 2)
            },
            "g_acmp": {
                'print_value': f"Accompanying variable action: {acmp_varbl:.2f} kN/m",
                'value': round(acmp_varbl, 2)
            },
            "psi_lead": {
                'print_value': f"psi_lead: {psi_lead:.2f}",
                'value': round(psi_lead, 2)
            },
            "psi_acmp": {
                'print_value': f"psi_acmp: {psi_acmp:.2f}",
                'value': round(psi_acmp, 2)
            },
            "gk": {
                'print_value': f"The calculated dead load on the beam (gk) is {gk:.2f} kN/m",
                'value': round(gk, 2)
            },
            "qp": {
                'print_value': f"Calculated peak velocity pressure qp: {qp:.2f} kN/m²",
                'value': round(qp, 2)
            },
            "wk": {
                'print_value': f"Wind load on the beam (wk): {wk:.2f} kN/m",
                'value': round(wk, 2)
            }
        }

        wind_side_results = {'wind_side' : self.print_results(We_side, "wind_side")}
        wind_direct_results = {'wind_direct' : self.print_results(We_direct, "wind_direct")}
        
        return results | wind_side_results | wind_direct_results

    def column_load_combinations(self):
        # Constants
        γ_g = 1.35
        γ_q = 1.5
        Ψ_0_q = 0
        Ψ_0_w = 0.6

        if self.altitude > 1000:
            height = 2
        else:
            height = 1

        if height == 1:
            Ψ_0_s = 0.7 
        else:
            Ψ_0_s = 0.5 

        # Inputs for dead load calculation

        gk_clm = 3*self.calculate_dead_load_clm(self.rho, self.T_sl, self.W_sl, self.L_sl, self.n)
        
        qk_clm = 3*self.calculate_Live_load_clm(self.W_sl, self.L_sl,self.n)
        
        sk_clm= self.calculate_snow_load_clm(self.W_sl,self.L_sl,self.n)

        # Get the wind load inputs
        z = self.h       #input("Enter the height at which the wind speed is considered (z) in (m)
        b = self.W_sl    #input("Enter the width of the building b (m)
        d = self.L_sl    #input("Enter the length of the building d (m)
        

        # Calculating kr, Iv, Vm, and qp using the first code's functions
        kr = self.calculate_kr(self.z0)
        Iv = self.calculate_turbulence_intensity(1, self.c0, z, self.z0)
        vm = self.calculate_mean_wind_velocity(kr, self.c0, self.vb0, z, self.z0)
        qp = self.calculate_peak_wind_velocity_pressure(Iv, 1.25, vm)  # rho is 1.25 kg/m^3

        # Calculate for direct wind
        We_direct, widths_direct = self.calculate_wind_pressure(qp, b, d, self.h)

        # Calculate for side wind (just swapping b and d)
        We_side, widths_side =  self.calculate_wind_pressure(qp, d, b, self.h)

        # Calculate wind loads
        wk_clm = 3* self.calculate_loads_clm(We_direct, We_side, widths_direct, self.h, d, self.n)
    
        

        ULS_category1 = [γ_g * gk_clm]
        ULS_category2 = [
            (γ_g * gk_clm) + (γ_q * qk_clm),
            (γ_g * gk_clm) + (γ_q * qk_clm) + (Ψ_0_s * γ_q * sk_clm),
            (γ_g * gk_clm) + (γ_q * qk_clm) + (Ψ_0_w * γ_q * wk_clm)
        ]
        ULS_category3 = [
            (γ_g * gk_clm) + (γ_q * qk_clm) + (Ψ_0_s * γ_q * sk_clm) + (Ψ_0_w * γ_q * wk_clm),
            (γ_g * gk_clm) + (Ψ_0_q * γ_q * qk_clm) + (γ_q * sk_clm) + (Ψ_0_w * γ_q * wk_clm),
            (γ_g * gk_clm) + (Ψ_0_q * γ_q * qk_clm) + (Ψ_0_s * γ_q * sk_clm) + (γ_q * wk_clm),
            (γ_g * gk_clm) + (γ_q * sk_clm),
            (γ_g * gk_clm) + (γ_q * wk_clm),
            (γ_g * gk_clm) + (γ_q * sk_clm) + (Ψ_0_w * γ_q * wk_clm),
            (γ_g * gk_clm) + (γ_q * wk_clm) + (Ψ_0_s * γ_q * sk_clm),
            (γ_g * gk_clm) + (Ψ_0_q * γ_q * qk_clm) + (γ_q * sk_clm),
            (γ_g * gk_clm) + (Ψ_0_q * γ_q * qk_clm) + (γ_q * wk_clm)
        ]
        max_category1_clm = max(ULS_category1)
        max_category2_clm = max(ULS_category2)
        max_category3_clm = max(ULS_category3)
        
        ########################################calculated results########################################
        
        results = {
            "P_clm": {
                'print_value': f"Maximum load for ULS Category 1 (Permanent) for column: {max_category1_clm:.2f} kN",
                'value': round(max_category1_clm, 2)
            },
            "M_clm": {
                'print_value': f"Maximum load for ULS Category 2 (Medium-term) for column: {max_category2_clm:.2f} kN",
                'value': round(max_category2_clm, 2)
            },
            "I_clm": {
                'print_value': f"Maximum load for ULS Category 3 (Instantaneous) for column: {max_category3_clm:.2f} kN",
                'value': round(max_category3_clm, 2)
            },
            "sk_clm": {
                'print_value': f"sk_column: {sk_clm:.2f}",
                'value': round(sk_clm, 2)
            },
            "wk_clm": {
                'print_value': f"wk_column: {wk_clm:.2f}",
                'value': round(wk_clm, 2)
            },
            "qk_clm": {
                'print_value': f"qk_column: {qk_clm:.2f}",
                'value': round(qk_clm, 2)
            }
        }
        
        return results

    def print_results(self, We_results, wind_direction):
        output = {}
        
        for area, pressure in We_results.items():
            output = output | {area: {
                    'print_value': f"We for area {area} for {wind_direction}: {pressure:.2f} kN/mˆ2",
                    'value': round(pressure, 2)
                }}
            
        return output
    
    def calculator(self):
        # Call the function to run the combined code
        beam_load_combinations = self.Beam_load_combinations()

        # Call the function to run the combined code
        column_load_combinations = self.column_load_combinations()
        
        return beam_load_combinations | column_load_combinations