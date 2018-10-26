from pricing.cost_calculator.cost_calculator import CostCalculator
from pricing.openei_tariff.openei_tariff_analyzer import *
from pricing.cost_calculator.tariff_structure import *
import datetime as dtime

calculator = CostCalculator()

def calc_total_price(power_vector, tariff_options, start_datetime, end_datetime, interval='15min'):
    '''
    returns the total energy cost of power consumption over the given window
    the granularity is determined from the length of the vector and the time window
    TODO: Demand charges

    power_vector: a pandas series of power consumption (kW) over the given window
    tariff_options: a dictionary of the form {
        utility_id: '14328',
        sector: 'Commercial',
        tariff_rate_of_interest: 'A-1 Small General Service', 
        distrib_level_of_interest=None, #TODO: Figure out what this is
        phasewing='Single',
        tou=True
    }
    start_datetime: the datetime object representing the start time (starts )
    end_datetime: the datetime object representing the start time
    '''
    time_delta = end_datetime - start_datetime
    interval_15_min = (3600*24*time_delta.days + time_delta.seconds)/(60*15)
    if len(power_vector) == interval_15_min or interval == '15min':
        energy_vector = power_15min_to_hourly_energy(power_vector)
    else:
        energy_vector = power_vector
    tariff = OpenEI_tariff(tariff_options['utility_id'],
                  tariff_options['sector'],
                  tariff_options['tariff_rate_of_interest'], 
                  tariff_options['distrib_level_of_interest'],
                  tariff_options['phasewing'],
                  tariff_options['tou'])
    
    tariff.read_from_json()
    tariff_struct_from_openei_data(tariff, calculator, pdp_event_filenames='PDP_events.json')
    pd_prices, map_prices = calculator.get_electricity_price(timestep=TariffElemPeriod.HOURLY,
                                                        range_date=(start_datetime.replace(tzinfo=pytz.timezone('US/Pacific')),
                                                                    end_datetime.replace(tzinfo=pytz.timezone('US/Pacific'))))
    pd_prices = pd_prices.fillna(0)
    energyPrices = pd_prices.customer_energy_charge.values + pd_prices.pdp_non_event_energy_credit.values + pd_prices.pdp_event_energy_charge.values
    demandPrices = pd_prices.customer_demand_charge_season.values + pd_prices.pdp_non_event_demand_credit.values + pd_prices.customer_demand_charge_tou.values
    return energyPrices @ energy_vector

def power_15min_to_hourly_energy(power_vector):
    energy_kwh = power_vector / 4.0
    return energy_kwh.groupby(power_vector.index.hour).sum()