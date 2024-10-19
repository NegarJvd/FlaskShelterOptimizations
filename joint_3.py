import math

class Joint_3:
    def __init__(self, material, cross_section):
        self.material = material
        self.cross_section = cross_section
        
        # Input parameters ( we are iterating over it D)
        self.w = self.cross_section.get('column_h') or 100        # 100 mm: Column height
        self.b = self.cross_section.get('column_w') or 112.5      # 112.5 mm: Column width
        self.wt = self.cross_section.get('tie_beam_h') or 152.4     # 152.4 mm: Tie beam height

        self.w_clmn = (self.w / 25.4)
        self.b_clmn = (self.b / 25.4)
        self.w_t = (self.wt / 25.4)

        self.tau_c = 1518           # fixed 
        self.F_ed = 2688            # fixed 
        self.F_em = 5488            # fixed 
        self.F_es = 2660            # fixed 
        self.required_load = 1000   # fixed 
        self.Ke = 0.625             # fixed 
        self.Re = 2.063             # fixed 
        self.k3 = 1.3               # fixed 

        # From material properties
        self.dtl_e = self.material.get('dtl_e') or 2              # end distance requirement 
        self.dtl_s = self.material.get('dtl_s') or 2.5            # peg spacing distance requirement 
        self.dtl_v = self.material.get('dtl_v') or 1.5            # edge distance requirement 
        self.dtl_g = self.material.get('dtl_g') or 1.5            # vertical edge distance requirement 
        self.n = 2                  # fixed 
        self.tm = (self.w_clmn / 3)
        self.ts = self.tm
        self.required_load_kN = self.required_load * 0.00444822

    # Calculate the capacity of the peg and spacing requirements 
    def calculate_capacity_and_status_for_graph(self):
            max_capacity = 0
            best_iteration = None
            
            # Iterate over D values, converting floats to ints
            for D in range(int(0.5 * 100), int((self.b_clmn / 4) * 100) + 1, int(0.02 * 100)): 
                D = D / 100  # Convert back to float for calculations

                # 1. Calculate Capacity Components
                PId = (self.n * D * self.tm * self.F_ed) / 2
                PIm = (self.n * D * self.tm * self.F_em) / 2
                PIs = self.n * D * self.ts * self.F_es
                PVd = (self.n * math.pi * (D ** 2) * self.tau_c) / 4

                # 2. Find Overall Capacity
                capacity = min(PId, PIm, PIs, PVd)

                # 3. Calculate Equivalent Steel Diameter Bolt
                Z = capacity 
                d_im = (4 * self.Ke * Z) / (self.tm * self.F_em)
                d_is = (2 * self.Ke * Z) / (self.ts * self.F_es)
                d_iiis = (1.6 * self.Ke * Z * (2 + self.Re)) / (self.k3 * self.ts * self.F_em)
                d_iv = (math.sqrt((1.6 * self.Ke * Z * math.sqrt(3 * (1 + self.Re))) / math.sqrt(2 * self.F_em * self.F_es))) / 2  

                d_eq = max(d_im, d_is, d_iiis, d_iv)

                # 4. Calculate Limits for Placement of the Dowel
                lim_e = self.dtl_e * d_eq
                lim_s = self.dtl_s * d_eq
                lim_v = self.dtl_v * d_eq
                lim_g = self.dtl_g * d_eq

                # 5. Check if the Joint is Strong Enough
                if capacity >= self.required_load and lim_v + lim_e < self.b_clmn and (2 * lim_g) + lim_s < self.w_t:
                    status = "Acceptable"
                else:
                    status = "Not Acceptable"

                # 6. If the status is acceptable and capacity is higher, store the iteration
                if status == "Acceptable" and capacity > max_capacity:
                    max_capacity = capacity
                    best_iteration = {
                        "D_mm": D * 25.4,
                        "lim_e_mm": lim_e * 25.4,
                        "lim_s_mm": lim_s * 25.4,
                        "lim_v_mm": lim_v * 25.4,
                        "lim_g_mm": lim_g * 25.4,
                        "capacity_kN": capacity * 0.00444822,
                        "status": status
                    }

            # Print the best iteration (if any acceptable iteration found)
            if best_iteration:
                return {
                    "d": {
                        'print_value': f"{best_iteration['D_mm']:.2f} mm",
                        'value': round(best_iteration['D_mm'], 2)
                    },
                    "lim_e": {
                        'print_value': f"{best_iteration['lim_e_mm']:.2f} mm",
                        'value': round(best_iteration['lim_e_mm'], 2)
                    },
                    "lim_s": {
                        'print_value': f"{best_iteration['lim_s_mm']:.2f} mm",
                        'value': round(best_iteration['lim_s_mm'], 2)
                    },
                    "lim_v": {
                        'print_value': f"{best_iteration['lim_v_mm']:.2f} mm",
                        'value': round(best_iteration['lim_v_mm'], 2)
                    },
                    "lim_g": {
                        'print_value': f"{best_iteration['lim_g_mm']:.2f} mm",
                        'value': round(best_iteration['lim_g_mm'], 2)
                    },
                    "capacity_kN": {
                        'print_value': f"{best_iteration['capacity_kN']:.2f} kN",
                        'value': round(best_iteration['capacity_kN'], 2)
                    },
                    "status": {
                        'print_value': f"{best_iteration['status']}",
                        'value': best_iteration['status'] == "Acceptable"
                    }
                }

            else:
                return {}

