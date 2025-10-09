#!/usr/bin/env python3
"""Main entry point for the host local server."""
from flask import Flask, render_template, request, redirect, url_for, jsonify
from plotly.utils import PlotlyJSONEncoder

import json
from src.visualization_helpers import load_data, plot_timeseries, parse_header_info, load_range_data
from src.constants import TEMPLATE_FOLDER
from src.constants import TimeseriesKeys

app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
@app.route('/')
def index():
    """Render the main page with the timeseries plot."""
    # Load the data
    df = load_data()
    header_info = parse_header_info(df)

    # Create the plot for the temperature sensor
    timeseries_plot_temp = plot_timeseries(df, data_key=TimeseriesKeys.AMBIENT_TEMP, timestamp_key=TimeseriesKeys.AMBIENT_TEMP_TIMESTAMP)
    plot_json_temp = json.dumps(timeseries_plot_temp, cls=PlotlyJSONEncoder)
    
    # create the plot for the door state sensor
    timeseries_plot_door = plot_timeseries(df, data_key=TimeseriesKeys.DOOR_STATE, timestamp_key=TimeseriesKeys.DOOR_STATE_TIMESTAMP)
    plot_json_door = json.dumps(timeseries_plot_door, cls=PlotlyJSONEncoder)
    # Render the HTML template with the plot JSON
    return render_template(
        'index.html',
        plot_json_temp=plot_json_temp,
        plot_json_door=plot_json_door,
        header_info=header_info,
        current_start_time='2025-08-01T00:00',
        current_end_time='2025-08-02T00:00'
    )

@app.route('/api/update_plot', methods=['POST'])
def api_update_plot():
    """Function to update the plot data."""
    # This function can be expanded to fetch new data and update the plot
    start_time = request.form.get('start_time')+ ":00"
    end_time = request.form.get('end_time') + ":00"
    
    # get new data based on the provided time range
    timeseries_df = load_range_data(start_time, end_time)

    # Create the plot for the temperature sensor
    timeseries_plot_temp = plot_timeseries(timeseries_df, data_key=TimeseriesKeys.AMBIENT_TEMP, timestamp_key=TimeseriesKeys.AMBIENT_TEMP_TIMESTAMP)
    plot_json_temp = json.dumps(timeseries_plot_temp, cls=PlotlyJSONEncoder)
    
    # create the plot for the door state sensor
    timeseries_plot_door = plot_timeseries(timeseries_df, data_key=TimeseriesKeys.DOOR_STATE, timestamp_key=TimeseriesKeys.DOOR_STATE_TIMESTAMP)
    plot_json_door = json.dumps(timeseries_plot_door, cls=PlotlyJSONEncoder)
    # reloads the local server page data
    return jsonify({
        'plot_json_temp': plot_json_temp,
        'plot_json_door': plot_json_door,
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)