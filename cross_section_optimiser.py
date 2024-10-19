from itertools import groupby
import numpy as np
import math as mt

class CrossSectionOptimizer:
    def __init__(self, material, load, footprint):
        self.material = material
        self.load = load
        self.footprint = footprint

        self.widths = np.arange(0.065, 0.1, 0.002)  # Stop at 0.252 to include 0.25
        self.thicknesses = np.arange(0.055, 0.15, 0.002)  # Stop at 0.402 to include 0.4
        
    def optimizer(self):
        
        #material_inputs
        y_m = self.material.get('partial_factor') or 1.3  # Partial factor
        rho = self.material.get('density') or  610  # Density
        fm_k = self.material.get('bending_strength') or  91  # Bending strength
        fv_k = self.material.get('shear_strength') or  9  # Shear strength
        fc_k = self.material.get('compression_parallel') or  45  # Compression parallel strength
        E = self.material.get('e_modulus') or  11.2  # E-modulus
        E_0_G_05 = self.material.get('e_modulus_5') or  11.2  # E-modulus_5
        kmod_p = self.material.get('modification_factor_permanent_term') or  0.5  # Modification factor permanent term
        kmod_m = self.material.get('modification_factor_medium_term') or  0.65  # Modification factor medium term
        kmod_i = self.material.get('modification_factor_instantaneous_term') or  0.9  # Modification factor instantaneous term
        K_def = self.material.get('creep_factor') or  2  # Creep factor
        B_c = self.material.get('creep_factor_solid_timber') or  0.2  # Factor for solid timber
        
        # Calculated by load calculator
        P_L = self.load.get('P_L') or  2.96  
        M_L = self.load.get('M_L') or  7.44
        I_L = self.load.get('I_L') or  5.66
        SLS_L = self.load.get('SLS_L') or  5.18
        gk = self.load.get('gk') or  1.38
        g_lead = self.load.get('g_lead') or  2
        g_acmp = self.load.get('g_acmp') or  1.4
        psi_lead = self.load.get('psi_lead') or  0
        psi_acmp = self.load.get('psi_acmp') or  0.2
        P_clm = self.load.get('P_clm') or  3.7
        M_clm = self.load.get('M_clm') or  9.2
        I_clm = self.load.get('I_clm') or  7

        # Footprint
        L = self.footprint.get('beam_length') or  2  # BEAM_LENGTH
        L_clm = self.footprint.get('height') or  2  # Column_LENGTH = height in footprint
 

        ###################start calculation#######################

        # Derived design strength values
        fm_d_p = (kmod_p * fm_k) / y_m
        fm_d_m = (kmod_m * fm_k) / y_m
        fm_d_i = (kmod_i * fm_k) / y_m
        
        fv_d_p = (kmod_p * fv_k) / y_m
        fv_d_m = (kmod_m * fv_k) / y_m
        fv_d_i = (kmod_i * fv_k) / y_m

        fc_d_p = (kmod_p * fc_k) / y_m
        fc_d_m = (kmod_m * fc_k) / y_m
        fc_d_i = (kmod_i * fc_k) / y_m

        # Prepare to collect results
        results = []
        iteration = 0
        
        # Iteration over possible dimensions
        for W in self.widths:
            if iteration >= 10:
                break
                
            for T in self.thicknesses:    
                V = L * W * T
                Wt = rho * V
                I_y = (W * 1000) * ((T * 1000)**3) / 12  # Moment of inertia with correct units
                I_z = (T * 1000) * ((W * 1000)**3) / 12  # Moment of inertia with correct units

                # ULS Calculations for beam
                Md_1 = P_L * L**2 / 8
                Md_2 = M_L * L**2 / 8
                Md_3 = I_L * L**2 / 8

                h = T  # Total depth of the beam

                # Shear and Bending stresses for ULS beam
                tau_1 = 3/2 * (P_L * L / 2) / (W * h) / 1000
                tau_2 = 3/2 * (M_L * L / 2) / (W * h) / 1000
                tau_3 = 3/2 * (I_L * L / 2) / (W * h) / 1000

                util_bend = max((Md_1 / I_y) * (h * 1000 / 2) * (10**6) / fm_d_p,
                                (Md_2 / I_y) * (h * 1000 / 2) * (10**6) / fm_d_m,
                                (Md_3 / I_y) * (h * 1000 / 2) * (10**6) / fm_d_i) * 100
                util_shear = max(tau_1 / fv_d_p, tau_2 / fv_d_m, tau_3 / fv_d_i) * 100

                # SLS Calculations for deflection
                δ_inst = 5*(1e6) *(SLS_L * L**4) / (384 * E * I_y)
                δ_crp_g = 5*(1e6) *(gk * L**4) * K_def / (384 * E * I_y)
                δ_crp_lead = 5*(1e6) *(g_lead * L**4) * K_def * psi_lead / (384 * E * I_y)
                δ_crp_acmp = 5*(1e6) *(g_acmp * L**4) * K_def * psi_acmp / (384 * E * I_y)
                δ_fin = δ_inst + δ_crp_g + δ_crp_lead + δ_crp_acmp

                util_deflct_inst = δ_inst / (L / 300) * 100
                util_deflct_fin = δ_fin / (L / 150) * 100
                util_sls = max(util_deflct_inst, util_deflct_fin)


                # ULS Calculations for Column Compression
                Strs_c_1 = P_clm / ((W * T)*(1e3))
                Strs_c_2 = M_clm / ((W * T)*(1e3))
                Strs_c_3 = I_clm / ((W * T)*(1e3))

                util_cmprs = max(Strs_c_1 / fc_d_p , Strs_c_2 / fc_d_m , Strs_c_3/ fc_d_i ) * 100


                # ULS Calculations for Column Buckling
                L_y = L_clm     # Buckling lengths
                L_Z = L_clm 
                
                i_y = (I_y / (W * T* (1e12)))**(1/2) #Radius of inertia
                i_z = (I_z / (W * T* (1e12)))**(1/2)
                
                sln_rtio_y = L_y/i_y        #Slenderness ratio
                sln_rtio_z = L_Z/i_z 
                
                sln_rel_y = (((sln_rtio_y/ mt.pi)) * (((fc_k/ E_0_G_05 )*(10))**(1/2)))/100   #Relative slenderness ratio
                sln_rel_z = (((sln_rtio_z/ mt.pi)) * (((fc_k/ E_0_G_05 )*(10))**(1/2)))/100  

                k_y = 0.5 * (1 + B_c * (sln_rel_y - 0.3) + (sln_rel_y **2))   #Instability factor 
                k_z = 0.5 * (1 + B_c * (sln_rel_z - 0.3) + (sln_rel_z **2))

                k_c_y = 1 / (k_y + mt.sqrt((k_y**2) - (sln_rel_y **2)))      #Buckling reduction coefficient 
                k_c_z = 1 / (k_z + mt.sqrt((k_z**2) - (sln_rel_z **2)))

                util_buckl_y = (Strs_c_1/ ((k_c_y) * (fc_d_m))) * 100   #Utilization in plane
                util_buckl_z = (Strs_c_1/ ((k_c_z) * (fc_d_m) )) * 100  #Utilization out of plane


                # Acceptability checks
                bend_status = "Acceptable" if util_bend < 100 else "Unacceptable"
                shear_status = "Acceptable" if util_shear < 100 else "Unacceptable"
                sls_status = "Acceptable" if util_sls < 100 else "Unacceptable"
                Compression_status = "Acceptable" if util_cmprs < 100 else "Unacceptable"
                bkl_y_status = "Acceptable" if util_buckl_y < 100 else "Unacceptable"
                bkl_z_status = "Acceptable" if util_buckl_z < 100 else "Unacceptable"
                util_final = max(util_bend,util_shear, util_sls, util_cmprs, util_buckl_y, util_buckl_z)
                final_status = "Acceptable" if util_final < 100 else "Unacceptable"
                
                #added for limiting the results
                if (iteration == 0 and final_status == "Acceptable") or (iteration > 0 and iteration < 10):
                    results.append((Wt, W, T, L, util_bend, bend_status, util_shear, shear_status, util_sls, sls_status, util_cmprs, Compression_status, util_buckl_y, bkl_y_status, util_buckl_z, bkl_z_status, util_final, final_status ))
                    iteration += 1
                    
                if iteration >= 10:
                    break

        # Sort results by weight and print final summary
        results.sort()  # Default sort by first element which is weight
        
        output = []

        for result in results:
            result_dict = {
                "weight": {'print_value': f"{result[0]:.2f} kg", 'value': round(result[0], 2)},
                "width": {'print_value': f"{result[1]*1000:.0f} mm", 'value': round(result[1]*1000, 2)},
                "thickness": {'print_value': f"{result[2]*1000:.0f} mm", 'value': round(result[2]*1000, 2)},
                "length": {'print_value': f"{result[3]:.2f} m", 'value': round(result[3], 2)},
                "bending_utilisation": {'print_value': f"{result[4]:.2f}%", 'value': round(result[4], 2)},
                "bending_status": {'print_value': result[5], 'value': result[5] == 'Acceptable'},
                "shear_utilisation": {'print_value': f"{result[6]:.2f}%", 'value': round(result[6], 2)},
                "shear_status": {'print_value': result[7], 'value': result[7] == 'Acceptable'},
                "sls_utilisation": {'print_value': f"{result[8]:.2f}%", 'value': round(result[8], 2)},
                "sls_status": {'print_value': result[9], 'value': result[9] == 'Acceptable'},
                "compression_utilisation": {'print_value': f"{result[10]:.2f}%", 'value': round(result[10], 2)},
                "compression_status": {'print_value': result[11], 'value': result[11] == 'Acceptable'},
                "buckling_utilisation_in_plane": {'print_value': f"{result[12]:.2f}%", 'value': round(result[12], 2)},
                "buckling_status_in_plane": {'print_value': result[13], 'value': result[13] == 'Acceptable'},
                "buckling_utilisation_out_of_plane": {'print_value': f"{result[14]:.2f}%", 'value': round(result[14], 2)},
                "buckling_status_out_of_plane": {'print_value': result[15], 'value': result[15] == 'Acceptable'},
                "final_utilisation": {'print_value': f"{result[16]:.2f}%", 'value': round(result[16], 2)},
                "final_utilisation_status": {'print_value': result[17], 'value': result[17] == 'Acceptable'},
            }
            
            output.append(result_dict)

        return output


#Width beam= width
#Height beam= Thickness

#Width column= width
#Height column= Thickness

#Tie beam width = width
#Tie beam height = (3/2) Thickness

#Bottom sill width = (5/4) Thickness
#Bottom sill  height =  width
