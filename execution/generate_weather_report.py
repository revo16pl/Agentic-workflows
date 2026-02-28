#!/usr/bin/env python3
"""
Generate Weekly Weather Report for Poland
Uses Open-Meteo API (completely free, no API key required)
Generates PDF report matching template visual design exactly
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime
from typing import Dict, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Constants
BASE_URL = 'https://api.open-meteo.com/v1/forecast'
OUTPUT_DIR = '.tmp'

# Polish cities with coordinates
POLISH_CITIES = {
    'Warsaw': (52.2297, 21.0122),
    'Krakow': (50.0647, 19.9450),
    'Gdansk': (54.3520, 18.6466),
    'Wroclaw': (51.1079, 17.0385),
    'Poznan': (52.4064, 16.9252),
    'Lodz': (51.7592, 19.4560)
}

class WeatherReportGenerator:
    def __init__(self, cities: Dict[str, Tuple[float, float]]):
        self.cities = cities
        self.weather_data = {}

    def fetch_weather_data(self, city: str, lat: float, lon: float) -> Dict:
        """Fetch weather data from Open-Meteo API (free, no key required)"""
        try:
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
                'hourly': 'temperature_2m',
                'timezone': 'auto',
                'forecast_days': 7
            }

            response = requests.get(BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather for {city}: {e}", file=sys.stderr)
            return None

    def weather_code_to_description(self, code: int) -> str:
        """Convert WMO weather code to description"""
        weather_codes = {
            0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
            45: 'Foggy', 48: 'Foggy', 51: 'Light drizzle', 53: 'Drizzle',
            55: 'Heavy drizzle', 61: 'Light rain', 63: 'Rain', 65: 'Heavy rain',
            71: 'Light snow', 73: 'Snow', 75: 'Heavy snow', 80: 'Rain showers',
            81: 'Rain showers', 82: 'Heavy rain showers', 95: 'Thunderstorm',
            96: 'Thunderstorm with hail', 99: 'Heavy thunderstorm'
        }
        return weather_codes.get(code, 'Unknown')

    def categorize_weather(self, code: int) -> str:
        """Categorize weather into Sunny/Cloudy/Rainy/Snowy"""
        if code in [0, 1]:
            return 'Sunny'
        elif code in [2, 3, 45, 48]:
            return 'Cloudy'
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]:
            return 'Rainy'
        elif code in [71, 73, 75]:
            return 'Snowy'
        return 'Mixed'

    def collect_all_data(self):
        """Collect weather data for all cities"""
        for city, (lat, lon) in self.cities.items():
            print(f"Fetching data for {city}...")
            data = self.fetch_weather_data(city, lat, lon)
            if data:
                self.weather_data[city] = data

    def analyze_data(self) -> Dict:
        """Analyze collected weather data"""
        analysis = {
            'avg_temp': 0,
            'cities_summary': {},
            'weather_patterns': {'Sunny': 0, 'Cloudy': 0, 'Rainy': 0, 'Snowy': 0, 'Mixed': 0},
            'regional': {'north': [], 'south': []},
            'hourly_temps': {h: [] for h in range(24)}
        }

        temps = []
        total_days = 0

        for city, data in self.weather_data.items():
            if not data:
                continue

            current = data.get('current', {})
            daily = data.get('daily', {})
            hourly = data.get('hourly', {})

            city_summary = {
                'current_temp': current.get('temperature_2m', 0),
                'avg_temp': sum(daily.get('temperature_2m_max', [])) / 7 if daily.get('temperature_2m_max') else 0,
                'max_temp': max(daily.get('temperature_2m_max', [0])),
                'min_temp': min(daily.get('temperature_2m_min', [0])),
                'humidity': current.get('relative_humidity_2m', 0),
                'wind_speed': current.get('wind_speed_10m', 0),
                'weather_desc': self.weather_code_to_description(current.get('weather_code', 0))
            }

            for code in daily.get('weather_code', []):
                category = self.categorize_weather(code)
                analysis['weather_patterns'][category] += 1
                total_days += 1

            temps.append(city_summary['avg_temp'])
            analysis['cities_summary'][city] = city_summary

            lat = self.cities[city][0]
            if lat > 52:
                analysis['regional']['north'].append(city_summary['avg_temp'])
            else:
                analysis['regional']['south'].append(city_summary['avg_temp'])

            if hourly.get('temperature_2m'):
                for i, temp in enumerate(hourly['temperature_2m'][:168]):
                    hour = i % 24
                    analysis['hourly_temps'][hour].append(temp)

        analysis['avg_temp'] = sum(temps) / len(temps) if temps else 0
        analysis['regional']['north_avg'] = sum(analysis['regional']['north']) / len(analysis['regional']['north']) if analysis['regional']['north'] else 0
        analysis['regional']['south_avg'] = sum(analysis['regional']['south']) / len(analysis['regional']['south']) if analysis['regional']['south'] else 0

        time_periods = ['Morning', 'Afternoon', 'Evening', 'Midnight']
        time_ranges = [(6, 12), (12, 18), (18, 24), (0, 6)]

        analysis['time_periods'] = {}
        for period, (start, end) in zip(time_periods, time_ranges):
            temps_in_range = []
            for h in range(start, end):
                if analysis['hourly_temps'][h]:
                    temps_in_range.append(sum(analysis['hourly_temps'][h]) / len(analysis['hourly_temps'][h]))
            analysis['time_periods'][period] = sum(temps_in_range) / len(temps_in_range) if temps_in_range else 0

        if total_days > 0:
            for pattern in analysis['weather_patterns']:
                analysis['weather_patterns'][pattern] = (analysis['weather_patterns'][pattern] / total_days) * 100

        return analysis

    def generate_pdf_report(self, analysis: Dict) -> str:
        """Generate PDF report matching template design exactly"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"poland_weather_report_{timestamp}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter  # 612 x 792

        # Color scheme
        blue_bg = colors.HexColor('#2B5F9E')
        dark_blue = colors.HexColor('#1E4A7A')
        white = colors.white

        # ========== HEADER SECTION (full width blue) ==========
        # Blue gradient background
        c.setFillColor(blue_bg)
        c.rect(0, height - 180, width, 180, fill=1, stroke=0)

        # Title (white, bold)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 40)
        c.drawString(60, height - 80, "WEEKLY WEATHER")
        c.drawString(60, height - 130, "REPORT 2026")

        # Date box (white rounded rectangle)
        date_box_x = width - 250
        date_box_y = height - 110
        c.setFillColor(white)
        c.roundRect(date_box_x, date_box_y, 210, 40, 8, fill=1, stroke=0)
        c.setFillColor(blue_bg)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(date_box_x + 105, date_box_y + 14, "February - 7 days forecast")

        # ========== LEFT COLUMN (blue background, 1/3 width) ==========
        left_col_width = 250
        left_col_x = 30
        content_start_y = height - 200

        # Executive Summary section
        c.setFillColor(dark_blue)
        c.rect(left_col_x, content_start_y - 150, left_col_width, 40, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(left_col_x + 15, content_start_y - 125, "Executive Summary")

        # Summary text (white on blue background)
        c.setFillColor(blue_bg)
        c.rect(left_col_x, content_start_y - 320, left_col_width, 170, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica", 10)

        summary_text = [
            f"Poland's weather shows stable conditions",
            f"with average temperature of {analysis['avg_temp']:.1f}°C",
            f"across monitored regions. Northern areas",
            f"averaging {analysis['regional']['north_avg']:.1f}°C while southern",
            f"regions show {analysis['regional']['south_avg']:.1f}°C. Forecast",
            "indicates varied precipitation patterns",
            "expected over the next week."
        ]

        text_y = content_start_y - 170
        for line in summary_text:
            c.drawString(left_col_x + 15, text_y, line)
            text_y -= 14

        # Metric boxes (3 stacked vertically)
        metric_y = content_start_y - 350

        # Metric 1: Average Temperature
        c.setFillColor(dark_blue)
        c.rect(left_col_x, metric_y - 110, left_col_width, 110, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_col_x + 15, metric_y - 25, "Average")
        c.drawString(left_col_x + 15, metric_y - 42, "Temperature:")
        c.setFont("Helvetica-Bold", 48)
        c.drawString(left_col_x + 15, metric_y - 85, f"{analysis['avg_temp']:.1f}°C")
        c.setFont("Helvetica", 10)
        c.drawString(left_col_x + 15, metric_y - 102, "Target 5°C")

        metric_y -= 130

        # Metric 2: Total Sunny Days
        sunny_days = int(analysis['weather_patterns'].get('Sunny', 0) / 100 * len(self.weather_data) * 7)
        c.setFillColor(dark_blue)
        c.rect(left_col_x, metric_y - 110, left_col_width, 110, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_col_x + 15, metric_y - 25, "Total Sunny")
        c.drawString(left_col_x + 15, metric_y - 42, "Days:")
        c.setFont("Helvetica-Bold", 68)
        c.drawString(left_col_x + 15, metric_y - 90, str(sunny_days))
        c.setFont("Helvetica", 10)
        c.drawString(left_col_x + 15, metric_y - 102, "Target 20 days")

        metric_y -= 130

        # Metric 3: Cities Monitored
        c.setFillColor(dark_blue)
        c.rect(left_col_x, metric_y - 110, left_col_width, 110, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_col_x + 15, metric_y - 25, "Cities")
        c.drawString(left_col_x + 15, metric_y - 42, "Monitored:")
        c.setFont("Helvetica-Bold", 68)
        c.drawString(left_col_x + 15, metric_y - 90, str(len(self.weather_data)))
        c.setFont("Helvetica", 10)
        c.drawString(left_col_x + 15, metric_y - 102, "Target 6 cities")

        # ========== RIGHT COLUMN (white background, 2/3 width) ==========
        right_col_x = left_col_x + left_col_width + 20
        right_col_width = width - right_col_x - 30
        right_y = content_start_y - 150

        # Performance by City
        c.setFillColor(dark_blue)
        c.rect(right_col_x, right_y, right_col_width, 35, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(right_col_x + 15, right_y + 12, "Performance by City")

        # Table header
        right_y -= 35
        c.setFillColor(dark_blue)
        c.rect(right_col_x, right_y, right_col_width, 25, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)

        col_positions = [right_col_x + 15, right_col_x + 100, right_col_x + 180, right_col_x + 250]
        headers = ["City", "Avg Temp", "High", "Low"]
        for i, header in enumerate(headers):
            c.drawString(col_positions[i], right_y + 8, header)

        # Table rows
        c.setFont("Helvetica", 9)
        row_num = 0
        for city, summary in list(analysis['cities_summary'].items())[:4]:
            right_y -= 22
            if row_num % 2 == 0:
                c.setFillColor(colors.HexColor('#E8E8E8'))
                c.rect(right_col_x, right_y, right_col_width, 22, fill=1, stroke=0)

            c.setFillColor(colors.black)
            values = [city, f"{summary['avg_temp']:.1f}°C", f"{summary['max_temp']:.1f}°C", f"{summary['min_temp']:.1f}°C"]
            for i, val in enumerate(values):
                c.drawString(col_positions[i], right_y + 6, val)
            row_num += 1

        # Performance by Weather Type
        right_y -= 50
        c.setFillColor(dark_blue)
        c.rect(right_col_x, right_y, right_col_width, 35, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(right_col_x + 15, right_y + 12, "Performance by Weather Type")

        # Big percentages
        right_y -= 55
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 40)

        sorted_patterns = sorted(analysis['weather_patterns'].items(), key=lambda x: x[1], reverse=True)
        pattern_x = right_col_x + 15
        for pattern, percentage in sorted_patterns[:4]:
            if percentage > 0:
                c.drawString(pattern_x, right_y, f"{percentage:.0f}%")
                c.setFont("Helvetica", 10)
                c.drawString(pattern_x + 5, right_y - 18, pattern)
                c.setFont("Helvetica-Bold", 40)
                pattern_x += 85

        # Regional Analysis
        right_y -= 80
        c.setFillColor(dark_blue)
        c.rect(right_col_x, right_y, right_col_width, 35, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(right_col_x + 15, right_y + 12, "Regional Analysis")

        right_y -= 55
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 36)
        c.drawString(right_col_x + 15, right_y, f"{len(self.weather_data) * 7}k")
        c.setFont("Helvetica", 10)
        c.drawString(right_col_x + 15, right_y - 15, "Total Days")

        # N and S temperatures
        c.setFont("Helvetica-Bold", 24)
        c.drawString(right_col_x + 140, right_y + 5, "N")
        c.setFont("Helvetica-Bold", 18)
        c.drawString(right_col_x + 165, right_y + 5, f"{int(analysis['regional']['north_avg'])}°C")

        c.setFont("Helvetica-Bold", 24)
        c.drawString(right_col_x + 240, right_y + 5, "S")
        c.setFont("Helvetica-Bold", 18)
        c.drawString(right_col_x + 265, right_y + 5, f"{int(analysis['regional']['south_avg'])}°C")

        # Peak Temperature Time
        right_y -= 80
        c.setFillColor(dark_blue)
        c.rect(right_col_x, right_y, right_col_width, 35, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(right_col_x + 15, right_y + 12, "Peak Temperature Time:")

        # Time percentages
        right_y -= 60
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 32)

        time_x = right_col_x + 15
        for period, temp in analysis['time_periods'].items():
            max_temp = max(analysis['time_periods'].values()) if analysis['time_periods'].values() else 1
            percentage = (temp / max_temp * 100) if max_temp > 0 else 0
            c.drawString(time_x, right_y, f"{int(percentage)}%")
            c.setFont("Helvetica", 9)
            c.drawString(time_x, right_y - 15, period)
            c.setFont("Helvetica-Bold", 32)
            time_x += 80

        c.save()
        return filepath

def main():
    parser = argparse.ArgumentParser(description='Generate weekly weather report for Poland')
    parser.add_argument('--cities', type=str, help='Comma-separated list of cities',
                       default=','.join(POLISH_CITIES.keys()))
    parser.add_argument('--output', type=str, choices=['pdf', 'json'], default='pdf')

    args = parser.parse_args()
    requested_cities = [city.strip() for city in args.cities.split(',')]
    cities_to_fetch = {city: coords for city, coords in POLISH_CITIES.items() if city in requested_cities}

    if not cities_to_fetch:
        print("Error: No valid cities specified.", file=sys.stderr)
        return 1

    try:
        generator = WeatherReportGenerator(cities_to_fetch)
        generator.collect_all_data()

        if not generator.weather_data:
            print("Error: Failed to fetch weather data", file=sys.stderr)
            return 1

        if args.output == 'json':
            analysis = generator.analyze_data()
            filepath = os.path.join(OUTPUT_DIR, f"weather_data_{datetime.now().strftime('%Y-%m-%d')}.json")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump({'raw_data': generator.weather_data, 'analysis': analysis}, f, indent=2)
            print(f"\n✓ Data saved: {filepath}")
        else:
            analysis = generator.analyze_data()
            filepath = generator.generate_pdf_report(analysis)
            print(f"\n✓ Report generated successfully: {filepath}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
