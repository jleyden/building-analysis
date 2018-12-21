from get_greenbutton_id import get_greenbutton_id
from event_table import event_table
from random import shuffle
from calc_price import *
import pandas as pd
import math

def add_days(dt, days):
    date_time = (pd.to_datetime(dt) + pd.to_timedelta(days, unit='day'))
    result = str(date_time.date()) + 'T00:00:00Z'
    return result

def agg_tbl(table, event_start_hr, event_end_hr, tariff_opts):
    date = str(table.index[0].date())
    energy_baseline = power_15min_to_hourly_energy(table['baseline-demand'])
    energy_event = power_15min_to_hourly_energy(table['event-demand'])
    full_day_baseline = sum(energy_baseline)
    full_day_event = sum(energy_event)
    window_baseline = sum(energy_baseline[(energy_baseline.index >= event_start_hr) & (energy_baseline.index <= event_end_hr)])
    window_event = sum(energy_event[(energy_event.index >= event_start_hr) & (energy_event.index <= event_end_hr)])
    baseline_cost = calc_total_price(table['baseline-demand'], tariff_opts, table['event-demand'].index[0], table['event-demand'].index[-1])
    event_cost = calc_total_price(table['event-demand'], tariff_opts, table['event-demand'].index[0], table['event-demand'].index[-1])
    event_peak_temp = max(table['event-weather'])
    baseline_peak_temp = max(table['baseline-weather'])
    max_demand_baseline = max(table['baseline-demand'])
    max_demand_event = max(table['event-demand'])
    return {
        'date': date,
        'baseline_full': full_day_baseline,
        'event_full': full_day_event,
        'baseline_window': window_baseline,
        'event_window': window_event,
        'baseline_peak_demand': max_demand_baseline,
        'event_peak_demand': max_demand_event,
        'baseline_cost': baseline_cost,
        'event_cost': event_cost,
        'event_peak_temp': event_peak_temp,
        'baseline_peak_temp': baseline_peak_temp
    }

def main(sites):
    all_events_dict = {}
    for site in sites:
        print(site)
        tarrifs = pd.read_csv('tariffs.csv', index_col='meter_id')
        events = pd.read_json('pricing/openei_tariff/PDP_events.json')
        meter_id = get_greenbutton_id(site, "2018-01-01T10:00:00-07:00", "2018-08-12T10:00:00-07:00")[0]
        tariff = tarrifs.loc[meter_id]
        utility_events = events[events['utility_id'] == tariff.utility_id]

        tables = utility_events.apply(lambda r: event_table(site, r['start_date'][:-6], add_days(r['start_date'], -40), add_days(r['start_date'], 40), max_baseline=True, offset=2), axis=1)
        dfs = [t['df'] for t in tables]
        tariff = dict(tariff)
        # may have to change the line above
        if type(tariff['distrib_level_of_interest']) == str or math.isnan(tariff['distrib_level_of_interest']):
            tariff['distrib_level_of_interest'] = None
        ciee_events = [agg_tbl(df, 14, 18, tariff) for df in dfs]
        ciee_events = pd.DataFrame(ciee_events)[[
                'date',
                'baseline_full',
                'event_full',
                'baseline_window',
                'event_window',
                'baseline_peak_demand',
                'event_peak_demand',
                'baseline_cost',
                'event_cost',
                'event_peak_temp',
                'baseline_peak_temp',
            ]]
        ciee_events['savings'] = ciee_events['baseline_cost'] - ciee_events['event_cost']
        ciee_events['event_energy_savings'] = ciee_events['baseline_window'] - ciee_events['event_window']
        all_events_dict[site] = ciee_events
        ciee_events.to_csv('./' + site + '_events.csv')
    return all_events_dict

from sites import sites
main(sites)


