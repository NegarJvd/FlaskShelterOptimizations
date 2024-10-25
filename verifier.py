import math as mt
from load_calculator import LoadCaluculator

class Verifier:
    def __init__(self, material, cross_section, footprint):
        self.material = material
        self.cross_section = cross_section
        self.footprint = footprint

        # Set specific dimensions for width and thickness
        self.W = self.cross_section.get('beam_w') or 100 / 1000                  # W= Width beam
        self.T = self.cross_section.get('beam_h') or 150 / 1000                  # T= Height beam 

        length = self.footprint.get('length')
        column_number = self.footprint.get('column_number')
        self.L = length / ((column_number / 2) - 1)                              # BEAM_LENGTH 
        self.L_clm = self.footprint.get('height')                                # Column_LENGTH
        
        self.y_m = self.material.get('partial_factor') or 1.3                              # Partial factor   
        self.rho = self.material.get('density') or 610
        self.fm_k = self.material.get('bending_strength') or 91                            # Bending strength
        self.fv_k = self.material.get('shear_strength') or 9                               # Shear strength
        self.fc_k = self.material.get('compression_parallel') or 45                        # Compression prallel strength
        self.E = self.material.get('e_modulus') or 11.2                                    # E-modulus
        self.E_0_G_05 = self.material.get('e_modulus_5') or 11.2                           # E-modulus_5
        self.kmod_p = self.material.get('modification_factor_permanent_term') or 0.5       # Modification_factor_permenant_term
        self.kmod_m = self.material.get('modification_factor_medium_term') or 0.65         # Modification_factor_medium_term
        self.kmod_i = self.material.get('modification_factor_instantaneous_term') or 0.9   # Modification_factor_instantaneous_term
        self.K_def = self.material.get('creep_factor') or 2                                # Creep factor
        self.B_c = self.material.get('creep_factor_solid_timber') or  0.2                  # Factor for solid timber

        # These_values_are_calculated_by_load_calculator
        load_calculation = LoadCaluculator(
           {
               'density': self.rho
           },{
                'slab_thickness': self.footprint.get('slab_thickness'),
                'width': self.footprint.get('width'),
                'length': length,
                'height': self.L_clm,
                'column_number': column_number
           }
        ).calculator()
        self.P_L = load_calculation.get('P_L').get('value') or 2.96                       
        self.M_L = load_calculation.get('M_L').get('value') or 7.44
        self.I_L = load_calculation.get('I_L').get('value') or 5.66
        self.SLS_L = load_calculation.get('SLS_L').get('value') or 5.18
        self.gk = load_calculation.get('gk').get('value') or 1.38
        self.g_lead = load_calculation.get('g_lead').get('value') or 2
        self.g_acmp = load_calculation.get('g_acmp').get('value') or 1.4
        self.psi_lead = load_calculation.get('psi_lead').get('value') or 0
        self.psi_acmp = load_calculation.get('psi_acmp').get('value') or 0.2
        self.P_clm = load_calculation.get('P_clm').get('value') or 3.7
        self.M_clm = load_calculation.get('M_clm').get('value') or 9.2
        self.I_clm = load_calculation.get('I_clm').get('value') or 7


    def verify_every_design(self):
        # Derived design strength values
        fm_d_p = (self.kmod_p * self.fm_k) / self.y_m
        fm_d_m = (self.kmod_m * self.fm_k) / self.y_m
        fm_d_i = (self.kmod_i * self.fm_k) / self.y_m
        
        fv_d_p = (self.kmod_p * self.fv_k) / self.y_m
        fv_d_m = (self.kmod_m * self.fv_k) / self.y_m
        fv_d_i = (self.kmod_i * self.fv_k) / self.y_m

        fc_d_p = (self.kmod_p * self.fc_k) / self.y_m
        fc_d_m = (self.kmod_m * self.fc_k) / self.y_m
        fc_d_i = (self.kmod_i * self.fc_k) / self.y_m

        # Volume and weight
        V = self.L * self.W * self.T
        Wt = self.rho * V
        I_y = (self.W * 1000) * ((self.T * 1000)**3) / 12  # Moment of inertia with correct units
        I_z = (self.T * 1000) * ((self.W * 1000)**3) / 12  # Moment of inertia with correct units

        # ULS Calculations for beam
        Md_1 = self.P_L * self.L**2 / 8
        Md_2 = self.M_L * self.L**2 / 8
        Md_3 = self.I_L * self.L**2 / 8

        h = self.T  # Total depth of the beam

        # Shear and Bending stresses for ULS beam
        tau_1 = 3/2 * (self.P_L * self.L / 2) / (self.W * h) / 1000
        tau_2 = 3/2 * (self.M_L * self.L / 2) / (self.W * h) / 1000
        tau_3 = 3/2 * (self.I_L * self.L / 2) / (self.W * h) / 1000

        util_bend = max((Md_1 / I_y) * (h * 1000 / 2) * (10**6) / fm_d_p,
                        (Md_2 / I_y) * (h * 1000 / 2) * (10**6) / fm_d_m,
                        (Md_3 / I_y) * (h * 1000 / 2) * (10**6) / fm_d_i) * 100
        util_shear = max(tau_1 / fv_d_p, tau_2 / fv_d_m, tau_3 / fv_d_i) * 100

        # SLS Calculations for deflection
        δ_inst = 5*(1e6)*(self.SLS_L * self.L**4) / (384 * self.E * I_y)
        δ_crp_g = 5*(1e6)*(self.gk * self.L**4) * self.K_def / (384 * self.E * I_y)
        δ_crp_lead = 5*(1e6)*(self.g_lead * self.L**4) * self.K_def * self.psi_lead / (384 * self.E * I_y)
        δ_crp_acmp = 5*(1e6)*(self.g_acmp * self.L**4) * self.K_def * self.psi_acmp / (384 * self.E * I_y)
        δ_fin = δ_inst + δ_crp_g + δ_crp_lead + δ_crp_acmp

        util_deflct_inst = δ_inst / (self.L / 300) * 100
        util_deflct_fin = δ_fin / (self.L / 150) * 100
        util_sls = max(util_deflct_inst, util_deflct_fin)

        # ULS Calculations for Column Compression
        Strs_c_1 = self.P_clm / ((self.W * self.T)*(1e3))
        Strs_c_2 = self.M_clm / ((self.W * self.T)*(1e3))
        Strs_c_3 = self.I_clm / ((self.W * self.T)*(1e3))

        util_cmprs = max(Strs_c_1 / fc_d_p , Strs_c_2 / fc_d_m , Strs_c_3 / fc_d_i ) * 100

        # ULS Calculations for Column Buckling
        L_y = self.L_clm     # Buckling lengths
        L_Z = self.L_clm 
                
        i_y = (I_y / (self.W * self.T* (1e12)))**(1/2) # Radius of inertia
        i_z = (I_z / (self.W * self.T* (1e12)))**(1/2)
                
        sln_rtio_y = L_y / i_y        # Slenderness ratio
        sln_rtio_z = L_Z / i_z 
                
        sln_rel_y = (((sln_rtio_y/ mt.pi)) * (((self.fc_k/ self.E_0_G_05 )*(10))**(1/2)))/100   # Relative slenderness ratio
        sln_rel_z = (((sln_rtio_z/ mt.pi)) * (((self.fc_k/ self.E_0_G_05 )*(10))**(1/2)))/100  

        k_y = 0.5 * (1 + self.B_c * (sln_rel_y - 0.3) + (sln_rel_y **2))   # Instability factor 
        k_z = 0.5 * (1 + self.B_c * (sln_rel_z - 0.3) + (sln_rel_z **2))

        k_c_y = 1 / (k_y + mt.sqrt((k_y**2) - (sln_rel_y **2)))      # Buckling reduction coefficient 
        k_c_z = 1 / (k_z + mt.sqrt((k_z**2) - (sln_rel_z **2)))

        util_buckl_y = (Strs_c_1/ ((k_c_y) * (fc_d_m))) * 100   # Utilization in plane
        util_buckl_z = (Strs_c_1/ ((k_c_z) * (fc_d_m) )) * 100  # Utilization out of plane

        # Final status check
        util_final = max(util_bend, util_shear, util_sls, util_cmprs, util_buckl_y, util_buckl_z)
        final_status = "Acceptable" if util_final < 100 else "Unacceptable"

        return final_status == "Acceptable"
