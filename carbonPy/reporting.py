# carbon_py/reporting.py
import json
import csv
import os
from datetime import datetime
from typing import Dict, Any


class Reporter:
    """
    Класс для генерации отчетов в различных форматах (консоль, JSON, CSV).
    """

    def __init__(
        self,
        data: Dict[str, Any],
        output_file: str = None,
        output_format: str = "console",
        csv_summary_only: bool = False,
        silent: bool = False,
    ):
        self.data = data
        self.output_file = output_file
        self.output_format = output_format
        self.csv_summary_only = csv_summary_only
        self.silent = silent

    def report(self):
        """Главный метод, который вызывает нужный формат вывода."""
        if self.output_file:
            self._report_to_file()
        else:
            self.to_console()

    def to_console(self):
        """Выводит отчет в консоль."""
        if self.silent:
            return
        summary = self.data["summary"]
        print("\n" + "=" * 30 + " CarbonPy Report " + "=" * 30)
        print(f"Start Time: {summary.get('start_time', 'N/A')}")
        print(f"End Time: {summary.get('end_time', 'N/A')}")
        print(f"Duration: {summary.get('duration_seconds', 'N/A')} seconds")
        print(f"Total Energy Consumed: {summary['total_energy_kwh']:.6f} кВт*ч")
        print(
            f"Carbon Intensity ({summary['region']}): {summary['carbon_intensity_gco2_per_kwh']} гCO₂экв/кВт*ч"
        )
        print(f"Total CO₂ Emissions: {summary['emissions_gco2eq']:.4f} гCO₂экв")
        print(f"Number of measurements: {len(self.data['measurements'])}")
        print("=" * 80 + "\n")

    def _report_to_file(self):
        """Вызывает метод для сохранения отчета в файл в зависимости от формата."""
        if self.output_format == "json":
            self._to_json()
        elif self.output_format == "csv":
            self._to_csv()
        elif self.output_format == "html":
            self._to_html()
        elif not self.silent:
            print(
                f"Warning: Unsupported file format '{self.output_format}'. Defaulting to console output."
            )
            self.to_console()

    def _to_json(self):
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        if not self.silent:
            print(f"Report saved to {self.output_file}")

    def _to_csv(self):
        if self.csv_summary_only:
            rows = [self.data.get("summary", {})]
            if not rows:
                if not self.silent:
                    print("No summary data to save to CSV.")
                return
        else:
            measurements = self.data.get("measurements", [])
            if not measurements:
                if not self.silent:
                    print("No measurements to save to CSV.")
                return
            rows = measurements

        with open(self.output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        if not self.silent:
            print(f"Report saved to {self.output_file}")

    def _to_html(self):
        summary = self.data["summary"]
        # Средние выбросы легкового автомобиля: ~120 гCO2/км.
        # Источник: European Environment Agency
        car_emissions_per_km = 120
        equivalent_km = summary["emissions_gco2eq"] / car_emissions_per_km

        # Средняя емкость аккумулятора смартфона ~15 Вт*ч = 0.015 кВт*ч
        smartphone_charge_kwh = 0.015
        equivalent_charges = (
            summary["total_energy_kwh"] / smartphone_charge_kwh
            if smartphone_charge_kwh > 0
            else 0
        )

        start_time = (
            datetime.fromisoformat(summary["start_time"])
            if summary.get("start_time")
            else None
        )
        report_id = (
            f"CP-PY-{(start_time.strftime('%Y%m%d-%H%M%S'))}" if start_time else "N/A"
        )
        issue_date = datetime.now().strftime("%d.%m.%Y")
        duration_str = f"{summary.get('duration_seconds', 0):.2f} сек"
        start_time_str = (
            start_time.strftime("%d.%m.%Y %H:%M:%S") if start_time else "N/A"
        )

        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Сертификат Углеродного Следа</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 40px; background-color: #e9ecef; color: #343a40; }}
                .certificate {{ max-width: 800px; margin: auto; background: white; padding: 40px; border: 10px solid #343a40; box-shadow: 0 0 20px rgba(0,0,0,0.15); position: relative; }}
                .header {{ text-align: center; border-bottom: 2px solid #dee2e6; padding-bottom: 20px; margin-bottom: 20px; }}
                .header h1 {{ font-size: 28px; color: #343a40; margin: 0; }}
                .header p {{ font-size: 14px; color: #6c757d; }}
                .main-results {{ text-align: center; margin: 40px 0; }}
                .main-results h2 {{ font-size: 16px; color: #6c757d; text-transform: uppercase; margin-bottom: 10px; }}
                .main-results .value {{ font-size: 48px; font-weight: bold; color: #2a9d8f; }}
                .details-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 30px; }}
                .card {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; }}
                .card h3 {{ margin-top: 0; font-size: 16px; color: #495057; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; margin-bottom: 15px;}}
                .card p {{ font-size: 22px; font-weight: bold; margin: 0; color: #343a40; }}
                .card small {{ color: #6c757d; font-size: 12px; }}
                .methodology {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d; text-align: justify; }}
                .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #adb5bd; }}
                .seal {{ position: absolute; bottom: 30px; right: 30px; width: 90px; height: 90px; background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="48" fill="%23343a40"/><path d="M50,15 L61.8,38.2 L87.5,42.5 L68.8,60.8 L73.6,86 L50,73.8 L26.4,86 L31.2,60.8 L12.5,42.5 L38.2,38.2 Z" fill="%23e9ecef"/><text x="50" y="55" font-family="Arial" font-size="10" fill="%23343a40" text-anchor="middle" font-weight="bold">CarbonPy</text></svg>'); }}
            </style>
        </head>
        <body>
            <div class="certificate">
                <div class="header">
                    <h1>Сертификат Углеродного Следа</h1>
                    <p>ID отчета: {report_id}  |  Дата выдачи: {issue_date}</p>
                </div>

                <div class="main-results">
                    <h2>Итоговые выбросы CO₂</h2>
                    <p class="value">{summary['emissions_gco2eq']:.4f} гCO₂экв</p>
                </div>

                <div class="details-grid">
                    <div class="card">
                        <h3>Общее энергопотребление</h3>
                        <p>{summary['total_energy_kwh']:.6f} кВт*ч</p>
                    </div>
                    <div class="card">
                        <h3>Продолжительность анализа</h3>
                        <p>{duration_str}</p>
                        <small>Начало: {start_time_str}</small>
                    </div>
                </div>

                <div class="details-grid">
                    <div class="card">
                        <h3>Интенсивность выбросов ({summary['region']})</h3>
                        <p>{summary['carbon_intensity_gco2_per_kwh']} г/кВт*ч</p>
                        <small>Количество CO₂, выбрасываемого при генерации 1 кВт*ч энергии в данном регионе.</small>
                    </div>
                     <div class="card">
                        <h3>Эквиваленты</h3>
                        <p>~{equivalent_km:.2f} км</p>
                        <small>пробега легкового автомобиля</small>
                        <p style="margin-top: 10px;">~{equivalent_charges:.0f}</p>
                        <small>полных зарядок смартфона</small>
                    </div>
                </div>

                <div class="methodology">
                    <h3>Методология</h3>
                    <p>
                        Оценка выбросов произведена библиотекой CarbonPy. Расчет основан на измерении энергопотребления CPU. Для систем Linux с процессорами Intel может использоваться технология Intel RAPL для более точных измерений. В остальных случаях используется модель на основе Thermal Design Power (TDP) и текущей загрузки процессора. Полученное энергопотребление умножается на коэффициент углеродной интенсивности для региона '{summary['region']}'. Данные являются оценочными и предназначены для сравнительного анализа.
                    </p>
                </div>

                <div class="footer">
                    Сгенерировано с помощью CarbonPy
                </div>

                <div class="seal"></div>
            </div>
        </body>
        </html>
        """
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        if not self.silent:
            print(f"Report saved to {self.output_file}")
