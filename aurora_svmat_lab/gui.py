from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .export import export_plan_rows, export_projection_rows, write_metric_rows_to_csv
from .notes import get_metric_notes
from .service import analyze_directory, analyze_plan_file


class AuroraSvmatApp(tk.Tk):
    def __init__(self, *, show: bool = False) -> None:
        super().__init__()
        self.title("Aurora SVMAT Lab")
        self.geometry("1180x760")
        self.path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Select an Aurora RTPLAN file or folder.")
        self.beam_filter_var = tk.StringVar(value="All beams")
        self.results = []
        self._result_item_to_index: dict[str, int] = {}
        self._selected_result: object | None = None
        self._current_projection_rows: list[dict[str, object]] = []

        self._build_ui()
        if not show:
            self.withdraw()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top_frame = ttk.Frame(self, padding=12)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        ttk.Label(top_frame, text="Input").grid(row=0, column=0, sticky="w")
        ttk.Entry(top_frame, textvariable=self.path_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(top_frame, text="File", command=self._browse_file).grid(row=0, column=2, padx=4)
        ttk.Button(top_frame, text="Folder", command=self._browse_dir).grid(row=0, column=3, padx=4)
        ttk.Button(top_frame, text="Run Analysis", command=self._run_analysis).grid(row=0, column=4, padx=4)
        ttk.Button(top_frame, text="Export CSV", command=self._export_csv).grid(row=0, column=5, padx=4)

        main_frame = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        left_frame = ttk.Frame(main_frame, padding=8)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=3)
        left_frame.rowconfigure(3, weight=2)
        main_frame.add(left_frame, weight=3)

        ttk.Label(left_frame, text="Analysis Results").grid(row=0, column=0, sticky="w")
        self.result_tree = ttk.Treeview(
            left_frame,
            columns=("status", "plan", "reason", "travel", "rotation", "pitch_cv"),
            show="headings",
            height=10,
        )
        for column, title, width in (
            ("status", "Status", 90),
            ("plan", "Plan", 260),
            ("reason", "Reason", 220),
            ("travel", "Travel / Rot", 110),
            ("rotation", "Rotation", 110),
            ("pitch_cv", "Pitch CV", 90),
        ):
            self.result_tree.heading(column, text=title)
            self.result_tree.column(column, width=width, anchor="center")
        self.result_tree.grid(row=1, column=0, sticky="nsew")
        self.result_tree.bind("<<TreeviewSelect>>", self._on_result_selected)

        projection_header = ttk.Frame(left_frame)
        projection_header.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        projection_header.columnconfigure(0, weight=1)
        ttk.Label(projection_header, text="Projection Details").grid(row=0, column=0, sticky="w")
        filter_frame = ttk.Frame(projection_header)
        filter_frame.grid(row=0, column=1, sticky="e")
        ttk.Label(filter_frame, text="Beam").grid(row=0, column=0, sticky="e", padx=(0, 6))
        self.beam_filter = ttk.Combobox(
            filter_frame,
            textvariable=self.beam_filter_var,
            state="readonly",
            width=14,
            values=("All beams",),
        )
        self.beam_filter.grid(row=0, column=1, sticky="e")
        self.beam_filter.bind("<<ComboboxSelected>>", self._on_beam_filter_changed)

        self.projection_tree = ttk.Treeview(
            left_frame,
            columns=("beam", "projection", "gantry", "axial", "pitch", "mu_density", "leaf_total", "leaf_x1", "leaf_x2"),
            show="headings",
            height=8,
        )
        for column, title, width in (
            ("beam", "Beam", 60),
            ("projection", "Projection", 90),
            ("gantry", "Delta Gantry", 90),
            ("axial", "Delta Axial", 90),
            ("pitch", "Pitch", 80),
            ("mu_density", "Weight/mm", 95),
            ("leaf_total", "Leaf/mm", 80),
            ("leaf_x1", "MLCX1/mm", 90),
            ("leaf_x2", "MLCX2/mm", 90),
        ):
            self.projection_tree.heading(column, text=title)
            self.projection_tree.column(column, width=width, anchor="center")
        self.projection_tree.grid(row=3, column=0, sticky="nsew")

        right_frame = ttk.Frame(main_frame, padding=8)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        right_frame.rowconfigure(3, weight=1)
        main_frame.add(right_frame, weight=2)

        ttk.Label(right_frame, text="Warnings").grid(row=0, column=0, sticky="w")
        self.warning_text = tk.Text(right_frame, height=8, wrap="word")
        self.warning_text.grid(row=1, column=0, sticky="nsew")

        ttk.Label(right_frame, text="Metric Notes").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.note_text = tk.Text(right_frame, height=14, wrap="word")
        self.note_text.grid(row=3, column=0, sticky="nsew")

        status_frame = ttk.Frame(self, padding=(12, 0, 12, 12))
        status_frame.grid(row=2, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        ttk.Label(
            status_frame,
            text="RESEARCH USE ONLY. CLINICAL USE IS STRONGLY FORBIDDEN.",
            foreground="#9b1c1c",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

    def _browse_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("DICOM RT Plan", "*.dcm"), ("All files", "*.*")])
        if path:
            self.path_var.set(path)

    def _browse_dir(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def _run_analysis(self) -> None:
        target_path = self.path_var.get().strip()
        if not target_path:
            self.status_var.set("Choose a file or folder first.")
            return

        path = Path(target_path)
        if path.is_dir():
            self.results = analyze_directory(path)
        else:
            self.results = [analyze_plan_file(path)]

        self._render_results()

    def _render_results(self) -> None:
        self.result_tree.delete(*self.result_tree.get_children())
        self._result_item_to_index = {}
        self._selected_result = None
        self._current_projection_rows = []
        self._clear_detail_panels()

        first_item: str | None = None
        for result in self.results:
            plan_name = result.metadata.plan_name or result.metadata.plan_label or Path(result.source_path).name
            item_id = self.result_tree.insert(
                "",
                "end",
                values=(
                    result.status,
                    plan_name,
                    result.reason,
                    _format_metric(result.plan_metrics.get("travel_per_rotation_mm")),
                    _format_metric(result.plan_metrics.get("total_rotation_deg")),
                    _format_metric(result.plan_metrics.get("projection_pitch_cv")),
                ),
            )
            self._result_item_to_index[item_id] = len(self._result_item_to_index)
            if first_item is None:
                first_item = item_id

        if first_item is not None:
            self.result_tree.selection_set(first_item)
            self.result_tree.focus(first_item)
            self._show_result_details(self.results[self._result_item_to_index[first_item]])

        self.status_var.set(f"Analyzed {len(self.results)} item(s).")

    def _on_result_selected(self, _event: object) -> None:
        selection = self.result_tree.selection()
        if not selection:
            return
        result_index = self._result_item_to_index.get(selection[0])
        if result_index is None:
            return
        self._show_result_details(self.results[result_index])

    def _on_beam_filter_changed(self, _event: object | None = None) -> None:
        self._render_projection_rows()

    def _show_result_details(self, result: object) -> None:
        self._selected_result = result
        self._current_projection_rows = export_projection_rows([result])
        self._refresh_beam_filter()
        self._render_projection_rows()

        warnings = list(getattr(result, "warnings", []) or [])
        for beam in getattr(result, "beams", []) or []:
            warnings.extend(getattr(beam, "warnings", []) or [])
        self.warning_text.delete("1.0", tk.END)
        self.warning_text.insert("1.0", "\n".join(warnings) if warnings else "No warnings.")

        plan_metrics = getattr(result, "plan_metrics", {}) or {}
        note_lines = [
            f"{metric_name}: {note}"
            for metric_name, note in get_metric_notes(tuple(plan_metrics.keys())).items()
        ]
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", "\n\n".join(note_lines) if note_lines else "No metric notes.")

    def _refresh_beam_filter(self) -> None:
        beam_values = ["All beams"]
        if self._selected_result is not None:
            for beam in getattr(self._selected_result, "beams", []) or []:
                beam_number = getattr(beam, "beam_number", None)
                if beam_number is None:
                    continue
                beam_label = f"Beam {beam_number}"
                if beam_label not in beam_values:
                    beam_values.append(beam_label)
        self.beam_filter.configure(values=tuple(beam_values))
        if self.beam_filter_var.get() not in beam_values:
            self.beam_filter_var.set("All beams")

    def _render_projection_rows(self) -> None:
        self.projection_tree.delete(*self.projection_tree.get_children())
        for projection_row in self._filtered_projection_rows(self.beam_filter_var.get() or "All beams"):
            self.projection_tree.insert(
                "",
                "end",
                values=(
                    projection_row.get("beam_number", ""),
                    projection_row.get("projection_label", ""),
                    _format_metric(projection_row.get("delta_gantry_deg")),
                    _format_metric(projection_row.get("delta_axial_mm")),
                    _format_metric(projection_row.get("projection_pitch")),
                    _format_metric(projection_row.get("projection_mu_density_proxy")),
                    _format_metric(projection_row.get("projection_leaf_travel")),
                    _format_metric(projection_row.get("projection_leaf_travel_mlcx1")),
                    _format_metric(projection_row.get("projection_leaf_travel_mlcx2")),
                ),
            )

    def _filtered_projection_rows(self, selected_filter: str) -> list[dict[str, object]]:
        if selected_filter == "All beams":
            return list(self._current_projection_rows)
        try:
            _, beam_number_text = selected_filter.split(" ", maxsplit=1)
            beam_number = int(beam_number_text)
        except (ValueError, AttributeError):
            return list(self._current_projection_rows)
        return [
            projection_row
            for projection_row in self._current_projection_rows
            if projection_row.get("beam_number") == beam_number
        ]

    def _clear_detail_panels(self) -> None:
        self.beam_filter.configure(values=("All beams",))
        self.beam_filter_var.set("All beams")
        self.projection_tree.delete(*self.projection_tree.get_children())
        self.warning_text.delete("1.0", tk.END)
        self.warning_text.insert("1.0", "No warnings.")
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", "No metric notes.")

    def _export_csv(self) -> None:
        if not self.results:
            self.status_var.set("Run an analysis before exporting.")
            return
        output_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not output_path:
            return
        write_metric_rows_to_csv(output_path, export_plan_rows(self.results))
        messagebox.showinfo("Aurora SVMAT Lab", f"Exported plan metrics to:\n{output_path}")


def _format_metric(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.4f}"


def main(*, run_loop: bool = True) -> None:
    app = AuroraSvmatApp(show=run_loop)
    if run_loop:
        app.mainloop()
    else:
        app.destroy()
    return None
