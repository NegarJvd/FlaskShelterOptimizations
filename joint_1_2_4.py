
#inputs: w_b: Column width., t_b: Column height., t_t: Tiebeam height., H_F: Height of the footprint, b_s= Bottom sill width

class Joints:
    def __init__(self, footprint, cross_section):
        self.footprint = footprint
        self.cross_section = cross_section
        
        self.w_b = self.cross_section.get('column_w') or 85
        self.t_b = self.cross_section.get('column_h') or 127
        self.t_t = self.cross_section.get('tie_beam_h') or 190
        self.b_s = self.cross_section.get('bottom_sill_w') or 158
        self.H_F = self.footprint.get('height') or 2
            
    def calculate_joint_1(self):                #Joint_1_Tenon_joint
        b_clm = self.w_b
        ttl_clm= self.t_b * (1/3) 
        btl_clm = self.w_b * (1/3)
        dtt_clm = self.b_s * (1/6)
        dtj_clm = self.b_s * (3/5)
        dtl_clm = self.b_s * (1/3)  

        return {
            "b_clm": {
                'print_value': f"b_clm = {b_clm:.2f}",
                'value': round(b_clm, 2)
            },
            "ttl_clm": {
                'print_value': f"ttl_clm = {ttl_clm:.2f}",
                'value': round(ttl_clm, 2)
            },
            "btl_clm": {
                'print_value': f"btl_clm = {btl_clm:.2f}",
                'value': round(btl_clm, 2)
            },
            "dtt_clm": {
                'print_value': f"dtt_clm = {dtt_clm:.2f}",
                'value': round(dtt_clm, 2)
            },
            "dtj_clm": {
                'print_value': f"dtj_clm = {dtj_clm:.2f}",
                'value': round(dtj_clm, 2)
            },
            "dtl_clm": {
                'print_value': f"dtl_clm = {dtl_clm:.2f}",
                'value': round(dtl_clm, 2)
            },
        } 
        

    def calculate_joint_2(self):                #Joint_2_gooseneck_joint
        jc1 = self.t_t * (1/3)
        jc2 = self.t_t * (1/6)
        jc3 = self.t_b
        jc4 = self.t_b * (1/2)
        jc5 = self.H_F * (1/5) * 100
        jc6 = self.t_t
        jc7 = self.t_b * (1/6)

        return {
            "jc1": {
                'print_value': f"jc1 = {jc1:.2f}",
                'value': round(jc1, 2)
            },
            "jc2": {
                'print_value': f"jc2 = {jc2:.2f}",
                'value': round(jc2, 2)
            },
            "jc3": {
                'print_value': f"jc3 = {jc3:.2f}",
                'value': round(jc3, 2)
            },
            "jc4": {
                'print_value': f"jc4 = {jc4:.2f}",
                'value': round(jc4, 2)
            },
            "jc5": {
                'print_value': f"jc5 = {jc5:.2f}",
                'value': round(jc5, 2)
            },
            "jc6": {
                'print_value': f"jc6 = {jc6:.2f}",
                'value': round(jc6, 2)
            },
            "jc7": {
                'print_value': f"jc7 = {jc7:.2f}",
                'value': round(jc7, 2)
            },
        } 


    def calculate_joint_4(self):            #Joint_4_scarf_joint
        e_sb = self.t_b / 6
        gl_s_b = self.t_b / 6
        l_scr = 3 * self.t_b / 6
        ttu_clm = self.t_b / 2
        btu_clm = self.w_b / 2
        leu_s_b = self.t_b / 4
        lsu_s_b = self.t_b / 2
        D = self.t_b / 6

        return {
            "w_b": {
                'print_value': f"w_b = {self.w_b:.2f}",
                'value': round(self.w_b, 2)
            },
            "t_b": {
                'print_value': f"t_b = {self.t_b:.2f}",
                'value': round(self.t_b, 2)
            },
            "e_sb": {
                'print_value': f"e_sb = {e_sb:.2f}",
                'value': round(e_sb, 2)
            },
            "gl_s_b": {
                'print_value': f"gl_s_b = {gl_s_b:.2f}",
                'value': round(gl_s_b, 2)
            },
            "l_scr": {
                'print_value': f"l_scr = {l_scr:.2f}",
                'value': round(l_scr, 2)
            },
            "ttu_clm": {
                'print_value': f"ttu_clm = {ttu_clm:.2f}",
                'value': round(ttu_clm, 2)
            },
            "btu_clm": {
                'print_value': f"btu_clm = {btu_clm:.2f}",
                'value': round(btu_clm, 2)
            },
            "leu_s_b": {
                'print_value': f"leu_s_b = {leu_s_b:.2f}",
                'value': round(leu_s_b, 2)
            },
            "lsu_s_b": {
                'print_value': f"lsu_s_b = {lsu_s_b:.2f}",
                'value': round(lsu_s_b, 2)
            },
            "D": {
                'print_value': f"D = {D:.2f}",
                'value': round(D, 2)
            },
        }

