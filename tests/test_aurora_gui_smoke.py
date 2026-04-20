import unittest


class AuroraGuiSmokeTests(unittest.TestCase):
    def test_gui_application_constructs_without_analysis(self):
        from aurora_svmat_lab.gui import AuroraSvmatApp

        app = AuroraSvmatApp()
        try:
            self.assertEqual(app.title(), "Aurora SVMAT Lab")
        finally:
            app.destroy()

    def test_gui_renders_projection_detail_rows_for_selected_result(self):
        from aurora_svmat_lab.gui import AuroraSvmatApp
        from aurora_svmat_lab.metrics import calculate_plan_metrics
        from aurora_svmat_lab.models import AuroraAnalysisResult, AuroraBeam, AuroraControlPoint, AuroraPlanMetadata

        beam = AuroraBeam(
            beam_number=1,
            beam_name="Beam A",
            control_points=[
                AuroraControlPoint(
                    control_point_index=0,
                    gantry_angle_deg=0.0,
                    cumulative_meterset_weight=0.0,
                    axial_position_mm=0.0,
                    mlc_x1_positions_mm=(-5.0,),
                    mlc_x2_positions_mm=(5.0,),
                ),
                AuroraControlPoint(
                    control_point_index=1,
                    gantry_angle_deg=120.0,
                    cumulative_meterset_weight=0.5,
                    axial_position_mm=15.0,
                    mlc_x1_positions_mm=(-4.0,),
                    mlc_x2_positions_mm=(6.0,),
                ),
                AuroraControlPoint(
                    control_point_index=2,
                    gantry_angle_deg=240.0,
                    cumulative_meterset_weight=1.0,
                    axial_position_mm=30.0,
                    mlc_x1_positions_mm=(-3.0,),
                    mlc_x2_positions_mm=(7.0,),
                ),
            ],
        )
        result = AuroraAnalysisResult(
            source_path="synthetic/aurora_plan.dcm",
            metadata=AuroraPlanMetadata(plan_name="Aurora GUI Synthetic"),
            beams=[beam],
            supported=True,
            plan_metrics=calculate_plan_metrics([beam]),
        )

        app = AuroraSvmatApp()
        try:
            app.results = [result]
            app._render_results()
            projection_rows = app.projection_tree.get_children()
            self.assertEqual(len(projection_rows), 2)
            first_row = app.projection_tree.item(projection_rows[0], "values")
            self.assertEqual(first_row[0], "1")
            self.assertEqual(first_row[1], "0→1")
        finally:
            app.destroy()

    def test_gui_filters_projection_details_by_beam(self):
        from aurora_svmat_lab.gui import AuroraSvmatApp
        from aurora_svmat_lab.metrics import calculate_plan_metrics
        from aurora_svmat_lab.models import AuroraAnalysisResult, AuroraBeam, AuroraControlPoint, AuroraPlanMetadata

        beam_a = AuroraBeam(
            beam_number=1,
            beam_name="Beam A",
            control_points=[
                AuroraControlPoint(
                    control_point_index=0,
                    gantry_angle_deg=0.0,
                    cumulative_meterset_weight=0.0,
                    axial_position_mm=0.0,
                    mlc_x1_positions_mm=(-5.0,),
                    mlc_x2_positions_mm=(5.0,),
                ),
                AuroraControlPoint(
                    control_point_index=1,
                    gantry_angle_deg=120.0,
                    cumulative_meterset_weight=0.5,
                    axial_position_mm=15.0,
                    mlc_x1_positions_mm=(-4.0,),
                    mlc_x2_positions_mm=(6.0,),
                ),
            ],
        )
        beam_b = AuroraBeam(
            beam_number=2,
            beam_name="Beam B",
            control_points=[
                AuroraControlPoint(
                    control_point_index=0,
                    gantry_angle_deg=180.0,
                    cumulative_meterset_weight=0.0,
                    axial_position_mm=30.0,
                    mlc_x1_positions_mm=(-5.0,),
                    mlc_x2_positions_mm=(5.0,),
                ),
                AuroraControlPoint(
                    control_point_index=1,
                    gantry_angle_deg=240.0,
                    cumulative_meterset_weight=0.4,
                    axial_position_mm=45.0,
                    mlc_x1_positions_mm=(-4.0,),
                    mlc_x2_positions_mm=(4.0,),
                ),
                AuroraControlPoint(
                    control_point_index=2,
                    gantry_angle_deg=300.0,
                    cumulative_meterset_weight=1.0,
                    axial_position_mm=60.0,
                    mlc_x1_positions_mm=(-3.0,),
                    mlc_x2_positions_mm=(4.0,),
                ),
            ],
        )
        result = AuroraAnalysisResult(
            source_path="synthetic/aurora_two_beam_plan.dcm",
            metadata=AuroraPlanMetadata(plan_name="Aurora GUI Two Beam"),
            beams=[beam_a, beam_b],
            supported=True,
            plan_metrics=calculate_plan_metrics([beam_a, beam_b]),
        )

        app = AuroraSvmatApp()
        try:
            app.results = [result]
            app._render_results()
            self.assertEqual(app.beam_filter_var.get(), "All beams")
            self.assertEqual(tuple(app.beam_filter["values"]), ("All beams", "Beam 1", "Beam 2"))
            self.assertEqual(len(app.projection_tree.get_children()), 3)

            app.beam_filter_var.set("Beam 2")
            app._on_beam_filter_changed()

            projection_rows = app.projection_tree.get_children()
            self.assertEqual(len(projection_rows), 2)
            first_row = app.projection_tree.item(projection_rows[0], "values")
            self.assertEqual(first_row[0], "2")
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
