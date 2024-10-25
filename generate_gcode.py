class GCodeGanarator:
    def generate_gcode(
        self,
        mortise_width,
        mortise_height,
        mortise_depth,
        tenon_width,
        tenon_height,
        tenon_length,
        peg_diameter,
        peg_depth,
        tool_diameter,
        feed_rate,
        spindle_speed,
        safe_z,
        step_down=2,  # Added step-down parameter
    ):
        """Generates G-code for a Lock n Load joint (a variation of pegged mortise and tenon)."""

        gcode = ""

        # Setup
        gcode += "G21\n"  # Set units to millimeters
        gcode += "G17\n"  # Set XY plane
        gcode += "G90\n"  # Set to absolute coordinates
        gcode += f"F{feed_rate}\n"
        gcode += f"S{spindle_speed}\n"

        # Mortise
        # Assumption: Mortise starts at X0 Y0
        gcode += self.mill_pocket(
            0, 0, -mortise_depth, mortise_width, mortise_height, tool_diameter, safe_z, step_down
        )

        # Tenon
        # Assumption: Tenon starts at X0 Y0
        gcode += self.mill_pocket(
            0,
            0,
            -tenon_length,
            tenon_width,
            tenon_height,
            tool_diameter,
            safe_z,
            step_down,
        )

        # Peg holes (through mortise and tenon)
        # Assumption: Pegs are centered on the mortise/tenon
        gcode += self.drill_hole(mortise_width / 2, mortise_height / 2, -peg_depth, peg_diameter, safe_z)
        gcode += self.drill_hole(mortise_width / 2, tenon_height / 2, -peg_depth, peg_diameter, safe_z)

        # End of program
        gcode += "M30\n"

        return gcode

    def mill_pocket(self, x_start, y_start, z_depth, width, height, tool_diameter, safe_z, step_down):
        """Generates G-code to mill a pocket."""

        gcode = ""
        current_z = 0
        while current_z > z_depth:
            current_z -= step_down
            gcode += f"G0 Z{safe_z}\n"
            gcode += f"G0 X{x_start + tool_diameter/2} Y{y_start + tool_diameter/2}\n"
            gcode += f"G1 Z{current_z}\n"
            gcode += f"G1 X{x_start + width - tool_diameter/2}\n"
            gcode += f"G1 Y{y_start + height - tool_diameter/2}\n"
            gcode += f"G1 X{x_start + tool_diameter/2}\n"
            gcode += f"G1 Y{y_start + tool_diameter/2}\n"
        gcode += f"G0 Z{safe_z}\n"
        return gcode

    def drill_hole(self, x_pos, y_pos, z_depth, diameter, safe_z):
        """Generates G-code to drill a hole."""

        gcode = ""
        gcode += f"G0 Z{safe_z}\n"
        gcode += f"G0 X{x_pos} Y{y_pos}\n"
        gcode += f"G1 Z{z_depth}\n"  # Use a drilling cycle (e.g., G81) if supported
        gcode += f"G0 Z{safe_z}\n"
        return gcode