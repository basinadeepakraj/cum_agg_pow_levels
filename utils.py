# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 18:53:39 2024

@author: SRMAP
"""
import scipy.stats as ss
import numpy as np
import pandas as pd

def compute_tariff_probs(tariffs, cat_mu_tar, sd):
    """
    Compute probabilities of tariffs for all categories

    Parameters
    ----------
    tariffs : list
        list of tariffs.
    cat_mu_tar : list
        list of tariff mean w.r.t category.
    sd : int
        standard deviation.

    Returns
    -------
    prob : List of lists
        tariff probabilities for all categories. 
        The dimension is (#cat x #tariffs) .

    """
    prob = []
    tL, tU = tariffs - 0.5, tariffs + 0.5
    for cat in range(5):
        pr = ss.norm.cdf(tU, loc=cat_mu_tar[cat], scale=sd) - \
                ss.norm.cdf(tL, loc=cat_mu_tar[cat], scale=sd)
        pr = pr/sum(pr)
        prob.append(pr)
    return prob       

def gen_appl_data(ll: int, ul: int, tariffs, prob)-> None:
    """
    Takes a lower (ll) and an upper limit (ul) on total power consumption 
    (in watts) and generates a list of appliances (lst_appl) in the house
    Args
        ll: lower limit on the total consumption of the household
        ul: upper limit on the total consumption of the household
        
    Returns
    -------
    A list of appliances, each appliance has a name, rated power, category, and
    a tariff subscription. Tariff subscription is randomly drawn from a 
    distribution where the probabilities for each tariff rate is given.

    """
    appl_data = pd.read_csv("appliance_data.csv") #appliance data
    appls = []
    tot_pow = 0
    while(1):
        ind = np.random.choice(range(len(appl_data)))
        name, cat, rpow = appl_data.iloc[ind].tolist()
        if tot_pow+rpow > ul:
            break;
        #Randomly subscribe the appliance to a tariff
        tar = np.random.choice(tariffs, size = 1, p = prob[cat])[0]
        appls.append([name, rpow, cat, tar])
        tot_pow+=rpow
    return appls

def consolidated_power_demand_levels(subarea_df):
    """
    For a given subareas appliance dataframe, groupby appliance demands using 
    tariff as the key.
    For each tariff group in descending order, calculate,
          i) aggregate power demand,
          ii) aggregate revenue for the power demand
          iii) Find cumulative power demands from the highest tariff rate
          iv) find the associated revenue.
    
    Parameters
    ----------
    subarea_df : Pandas DataFrame
        Its columns are 'hid': House ID, 
                        'type': Type of the house (I or II or ... V), 
                        'name': Name of the appliance, 
                        'pow': Rated power of the appliance, 
                        'cat': Category of the appliance (Cat 1, Cat 2 or ... Cat 5), 
                        'tar': Subscribed Tariff rate.

    Returns
    -------
    consol_df : Pandas DataFrame
        Returns cumulative aggregate power demands and associated (cumulative 
        aggregate) revenues.

    """
    groupby_tar = subarea_df.groupby('tar').sum()
    groupby_tar = groupby_tar.sort_index(ascending=False)
    consol_df = pd.DataFrame(index= groupby_tar.index, columns=['agg_p', 'agg_r', 
                                      'consol_P', 'consol_R'])
    consol_df['agg_p'] = groupby_tar['pow']
    # As aggregate power is in watts, divide aggregate revenue values by 1000 as rate of tariff is for 1 kW, 
    consol_df['agg_r'] = groupby_tar['pow']*groupby_tar.index/1000
    consol_df['consol_P'] = consol_df.agg_p.cumsum()
    consol_df['consol_R'] = consol_df.agg_r.cumsum()
    return consol_df