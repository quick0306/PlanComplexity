import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from DicomParse.utilities import retrieve_dcm_filenames
from ucomx_models import AnalysisMode
from ucomx_service import (
    analyze_filepaths,
    analyze_plan_file,
    build_metadata_rows,
    build_metric_rows,
    build_metric_reference_rows,
    export_results_to_csv,
    summarize_results,
)


class UCoMXApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PyUCoMX")
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self.results = []
        self._result_queue: "queue.Queue[tuple[str, object]]" = queue.Queue()
        self._worker_thread: threading.Thread | None = None
        self._is_running = False
        self._total_items = 0
        self._completed_items = 0
        self._build_style()
        self._build_layout()
        self._set_busy_state(False)

    def _build_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Header.TLabel", font=("Segoe UI", 17, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(header, text="PyUCoMX", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Python implementation of VMAT/IMRT and Tomo complexity analysis.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        sidebar = ttk.LabelFrame(container, text="Analysis Setup", padding=14)
        sidebar.grid(row=1, column=0, sticky="nsw", padx=(0, 16))
        sidebar.columnconfigure(0, weight=1)

        self.input_kind = tk.StringVar(value="file")
        self.mode_var = tk.StringVar(value=AnalysisMode.AUTO.value)
        self.recursive_var = tk.BooleanVar(value=True)
        self.path_var = tk.StringVar()

        ttk.Label(sidebar, text="Input Type").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(sidebar, text="Single RT Plan", variable=self.input_kind, value="file").grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(sidebar, text="Folder Batch", variable=self.input_kind, value="folder").grid(row=2, column=0, sticky="w", pady=(0, 8))

        ttk.Label(sidebar, text="Mode").grid(row=3, column=0, sticky="w")
        ttk.Combobox(
            sidebar,
            textvariable=self.mode_var,
            values=[mode.value for mode in AnalysisMode],
            state="readonly",
        ).grid(row=4, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(sidebar, text="Input Path").grid(row=5, column=0, sticky="w")
        ttk.Entry(sidebar, textvariable=self.path_var).grid(row=6, column=0, sticky="ew", pady=(4, 6))
        self.browse_button = ttk.Button(sidebar, text="Browse", command=self._browse_input)
        self.browse_button.grid(row=7, column=0, sticky="ew")
        ttk.Checkbutton(sidebar, text="Recursive folder scan", variable=self.recursive_var).grid(row=8, column=0, sticky="w", pady=(10, 12))
        self.run_button = ttk.Button(sidebar, text="Run Analysis", style="Accent.TButton", command=self._run_analysis)
        self.run_button.grid(row=9, column=0, sticky="ew")
        self.export_button = ttk.Button(sidebar, text="Export Current Results", command=self._export_results)
        self.export_button.grid(row=10, column=0, sticky="ew", pady=(8, 0))

        self.summary_var = tk.StringVar(value="No results yet.")
        ttk.Label(sidebar, text="Summary").grid(row=11, column=0, sticky="w", pady=(14, 4))
        ttk.Label(sidebar, textvariable=self.summary_var, wraplength=260, justify="left").grid(row=12, column=0, sticky="w")
        self.progress_var = tk.StringVar(value="Idle.")
        ttk.Label(sidebar, text="Progress").grid(row=13, column=0, sticky="w", pady=(12, 4))
        ttk.Label(sidebar, textvariable=self.progress_var, wraplength=260, justify="left").grid(row=14, column=0, sticky="w")
        self.progress_bar = ttk.Progressbar(sidebar, mode="determinate", maximum=1, value=0)
        self.progress_bar.grid(row=15, column=0, sticky="ew", pady=(6, 0))

        main = ttk.Frame(container)
        main.grid(row=1, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        results_frame = ttk.LabelFrame(main, text="Plans", padding=10)
        results_frame.grid(row=0, column=0, sticky="ew")
        results_frame.columnconfigure(0, weight=1)
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=("mode", "status", "reason", "plan", "patient", "machine"),
            show="headings",
            height=8,
        )
        for key, title, width in (
            ("mode", "Mode", 90),
            ("status", "Status", 100),
            ("reason", "Reason", 180),
            ("plan", "Plan", 220),
            ("patient", "Patient", 180),
            ("machine", "Machine", 160),
        ):
            self.results_tree.heading(key, text=title)
            self.results_tree.column(key, width=width, anchor="w")
        self.results_tree.grid(row=0, column=0, sticky="ew")
        self.results_tree.bind("<<TreeviewSelect>>", self._on_select_result)

        detail_pane = ttk.Panedwindow(main, orient=tk.HORIZONTAL)
        detail_pane.grid(row=1, column=0, sticky="nsew", pady=(12, 0))

        metadata_frame = ttk.LabelFrame(detail_pane, text="Metadata", padding=10)
        metrics_frame = ttk.LabelFrame(detail_pane, text="Metrics", padding=10)
        reference_frame = ttk.LabelFrame(detail_pane, text="Metric Notes", padding=10)
        detail_pane.add(metadata_frame, weight=1)
        detail_pane.add(metrics_frame, weight=2)
        detail_pane.add(reference_frame, weight=2)

        self.metadata_tree = ttk.Treeview(metadata_frame, columns=("name", "value"), show="headings")
        self.metadata_tree.heading("name", text="Field")
        self.metadata_tree.heading("value", text="Value")
        self.metadata_tree.column("name", width=180, anchor="w")
        self.metadata_tree.column("value", width=280, anchor="w")
        self.metadata_tree.pack(fill=tk.BOTH, expand=True)

        self.metrics_tree = ttk.Treeview(metrics_frame, columns=("metric", "value"), show="headings")
        self.metrics_tree.heading("metric", text="Metric (paper naming)")
        self.metrics_tree.heading("value", text="Value")
        self.metrics_tree.column("metric", width=260, anchor="w")
        self.metrics_tree.column("value", width=220, anchor="w")
        self.metrics_tree.pack(fill=tk.BOTH, expand=True)

        self.reference_tree = ttk.Treeview(reference_frame, columns=("metric", "note"), show="headings")
        self.reference_tree.heading("metric", text="Metric")
        self.reference_tree.heading("note", text="Definition / Notes")
        self.reference_tree.column("metric", width=240, anchor="w")
        self.reference_tree.column("note", width=480, anchor="w")
        self.reference_tree.pack(fill=tk.BOTH, expand=True)

        log_frame = ttk.LabelFrame(main, text="Warnings / Notes", padding=10)
        log_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        self.warnings_box = tk.Text(log_frame, height=6, wrap="word")
        self.warnings_box.pack(fill=tk.BOTH, expand=True)

        footer = ttk.Frame(container, padding=(0, 12, 0, 0))
        footer.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Label(
            footer,
            text="Jinyan Hu, Medical Physicist. RESEARCH USE ONLY. CLINICAL USE IS STRONGLY FORBIDDEN.",
            style="Sub.TLabel",
            anchor="center",
            justify="center",
        ).pack(fill=tk.X)

    def _browse_input(self) -> None:
        if self.input_kind.get() == "file":
            path = filedialog.askopenfilename(
                title="Select RT Plan DICOM file",
                filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")],
            )
        else:
            path = filedialog.askdirectory(title="Select folder containing RT Plan files")
        if path:
            self.path_var.set(path)

    def _run_analysis(self) -> None:
        if self._is_running:
            return
        path = self.path_var.get().strip()
        if not path:
            messagebox.showerror("Missing input", "Please choose a file or folder first.")
            return

        mode = AnalysisMode(self.mode_var.get())
        try:
            if self.input_kind.get() == "file":
                filepaths = [path]
            else:
                filepaths = retrieve_dcm_filenames(path, recursive=self.recursive_var.get())
        except Exception as exc:
            messagebox.showerror("Analysis failed", str(exc))
            return

        if not filepaths:
            messagebox.showerror("No RT Plan files found", "No .dcm RT Plan files were found for the selected input.")
            return

        self.results = []
        self._refresh_results_tree()
        self._clear_detail_views()
        self._total_items = len(filepaths)
        self._completed_items = 0
        self._is_running = True
        self.progress_bar.configure(maximum=max(self._total_items, 1), value=0)
        self.progress_var.set(f"Starting analysis: 0 / {self._total_items}")
        self.summary_var.set("Analysis in progress...")
        self._set_busy_state(True)
        self._worker_thread = threading.Thread(
            target=self._run_analysis_worker,
            args=(filepaths, mode),
            daemon=True,
        )
        self._worker_thread.start()
        self.after(100, self._poll_result_queue)

    def _run_analysis_worker(self, filepaths: list[str], mode: AnalysisMode) -> None:
        try:
            if len(filepaths) == 1:
                result = analyze_plan_file(filepaths[0], requested_mode=mode)
                self._result_queue.put(("result", result))
            else:
                for result in analyze_filepaths(filepaths, requested_mode=mode):
                    self._result_queue.put(("result", result))
        except Exception as exc:
            self._result_queue.put(("error", str(exc)))
        finally:
            self._result_queue.put(("done", None))

    def _poll_result_queue(self) -> None:
        saw_done = False
        while True:
            try:
                event, payload = self._result_queue.get_nowait()
            except queue.Empty:
                break

            if event == "result":
                self._append_result(payload)
            elif event == "error":
                messagebox.showerror("Analysis failed", str(payload))
            elif event == "done":
                saw_done = True

        if saw_done:
            self._finish_analysis()
            return

        if self._is_running:
            self.after(100, self._poll_result_queue)

    def _append_result(self, result) -> None:
        index = len(self.results)
        self.results.append(result)
        self._completed_items += 1
        self.results_tree.insert(
            "",
            "end",
            iid=str(index),
            values=(
                result.mode.value,
                result.status,
                result.reason_label,
                result.metadata.get("plan_name", ""),
                result.metadata.get("patient_name", ""),
                result.metadata.get("machine_id", ""),
            ),
        )
        self.progress_bar.configure(value=self._completed_items)
        self.progress_var.set(f"Analyzed {self._completed_items} / {self._total_items}")
        summary = summarize_results(self.results)
        self.summary_var.set(
            f"{summary['total']} plans analyzed, {summary['supported']} supported, {summary['unsupported']} flagged."
        )
        if index == 0:
            self._show_result(0)

    def _finish_analysis(self) -> None:
        self._is_running = False
        self._set_busy_state(False)
        self.progress_var.set(f"Completed: {self._completed_items} / {self._total_items}")

    def _set_busy_state(self, is_busy: bool) -> None:
        browse_state = "disabled" if is_busy else "normal"
        run_state = "disabled" if is_busy else "normal"
        export_state = "disabled" if is_busy or not self.results else "normal"
        self.browse_button.configure(state=browse_state)
        self.run_button.configure(state=run_state)
        self.export_button.configure(state=export_state)

    def _refresh_results_tree(self) -> None:
        self.results_tree.delete(*self.results_tree.get_children())
        for index, result in enumerate(self.results):
            metadata = result.metadata
            self.results_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    result.mode.value,
                    result.status,
                    result.reason_label,
                    metadata.get("plan_name", ""),
                    metadata.get("patient_name", ""),
                    metadata.get("machine_id", ""),
                ),
            )

    def _clear_detail_views(self) -> None:
        self.metadata_tree.delete(*self.metadata_tree.get_children())
        self.metrics_tree.delete(*self.metrics_tree.get_children())
        self.reference_tree.delete(*self.reference_tree.get_children())
        self.warnings_box.delete("1.0", tk.END)

    def _on_select_result(self, _event) -> None:
        selected = self.results_tree.selection()
        if not selected:
            return
        self._show_result(int(selected[0]))

    def _show_result(self, index: int) -> None:
        result = self.results[index]
        self.metadata_tree.delete(*self.metadata_tree.get_children())
        self.metrics_tree.delete(*self.metrics_tree.get_children())
        self.reference_tree.delete(*self.reference_tree.get_children())
        self.warnings_box.delete("1.0", tk.END)

        for name, value in build_metadata_rows(result):
            self.metadata_tree.insert("", "end", values=(name, value))
        for name, value in build_metric_rows(result):
            self.metrics_tree.insert("", "end", values=(name, value))
        for name, note in build_metric_reference_rows(result):
            self.reference_tree.insert("", "end", values=(name, note))

        notes = f"Reason: {result.reason_label}\n\n"
        notes += "\n".join(result.warnings) if result.warnings else "No warnings."
        self.warnings_box.insert("1.0", notes)

    def _export_results(self) -> None:
        if not self.results:
            messagebox.showerror("Nothing to export", "Run an analysis first.")
            return
        output_csv = filedialog.asksaveasfilename(
            title="Export results to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not output_csv:
            return
        try:
            export_results_to_csv(self.results, output_csv)
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))
            return
        reference_csv = os.path.splitext(output_csv)[0] + "_columns.csv"
        messagebox.showinfo(
            "Export complete",
            f"Results exported to:\n{output_csv}\n\nColumn reference exported to:\n{reference_csv}",
        )


def main() -> None:
    app = UCoMXApp()
    app.mainloop()


if __name__ == "__main__":
    main()
