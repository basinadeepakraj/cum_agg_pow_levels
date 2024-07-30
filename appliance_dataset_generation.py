# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 11:06:11 2024

@author: SRMAP
"""

import numpy as np
np.random.seed(47)
# import matplotlib.pyplot as plt
import pandas as pd
from utils import compute_tariff_probs, \
                    gen_appl_data, \
                    consolidated_power_demand_levels

def compute_consolidated_levels(tariffs,
                                cat_mu_tar,
                                sd,
                                NSubs,
                                Min_NHouses,
                                Max_NHouses,
                                house_typ_limits):
    """
    Data Generation Framework
    Given, 1. NSubs number of subarea under the purview of an EDCo,
           2. Monotonically decreasing Tariff rates suggested by the EDCo
           3. Category wise mean tariff rate and standard deviation
           4. Different types of Houses with their upper and lower limits
           5. Minimum and Maximum number of houses per type of house in a 
               subarea,
    generate appliance dataset for each subarea through the following framework.
    For each subarea:
        For each type of house:
            *Randomly select a number from the range (Min_NHouses, Max_NHouses),
            representing the number of houses for the given type of house.
            
            *For each house of the given type, draw appliances randomly
            such that the total power do not exceed the upper and lower limits.
            
            *Each appliance is randomly subscibed to a tariff rate, where the
            mean of the probability distribution is set such that important 
            appliances are subscribed to higher tariff rates.

    Parameters
    ----------
    tariffs : List of integer
        List of tariff rates. Here we have considerd only integer rates
    cat_mu_tar : List of integers
        Mean tariff rate for each of the available categories.
    sd : float
        Standard deviation. Here we have considered it to be 2 (Fixed).
    NSubs : Integer
        Number of subareas under the purview of an EDCo.
    Min_NHouses : Integer
        Minimum number of houses of any particular type.
    Max_NHouses : Integer
        Maximum number of houses of any particular type.
    house_typ_limits : Dictionary
        Consists of five types of houses (I, II, ... V) each having a lower
        limit and upper limit.

    Returns
    -------
    consol_Ps : List of lists
        List of cumulative aggregate power demand bids (power values).
    consol_Rs : List of lists
        List of cumulative aggregate revenues associated with the cumulative
        aggregate power demand values.

    """
    
     
    
    prob = compute_tariff_probs(tariffs, cat_mu_tar, sd)
    
    appls_df = pd.DataFrame(columns=['subid', 'hid', 'type',
                                 'name', 'pow', 'cat','tar'])
    
    
    for s in range(NSubs):
        for typ in house_typ_limits.keys():
            for h in range(np.random.randint(Min_NHouses,Max_NHouses)):
                ll, ul = house_typ_limits[typ]
                appls = gen_appl_data(ll, ul, tariffs, prob)
                for app in appls:
                    appls_df.loc[len(appls_df)] = [s, h, typ] + app
                
    #After generating the appliance dataset for all the subareas, the appliance
    # demands are consolidated into cumulative aggregate power levels and their
    # associated revenue values.
    
    consol_Ps = []
    consol_Rs = []
    for subid, subarea_df in appls_df.groupby('subid'):
        df = consolidated_power_demand_levels(subarea_df)
        consol_Ps.append([round(num,2) for num in list(df.consol_P)])
        consol_Rs.append([round(num,2) for num in list(df.consol_R)])
        
    return consol_Ps, consol_Rs
        
if __name__=='__main__':
    house_typ_limits = {"I":(1000,2000), 
                        "II":(2000,4000), 
                        "III":(4000,6000), 
                        "IV":(6000, 8000), 
                        "V":(8000,10000)} #type (ll,ul) in watts

    tariffs = np.arange(8,0,-1) #say, 5, 4, 3, 2, 1 
    # tariffs are in monotonically decreaseing order

    #category wise mean tariffs and stddev as 2 
    #say, cat 0 appliance mean tariff is maximum 
    cat_mu_tar,  sd = [8, 6, 5, 4, 2], 2

    NSubs = 2
    Min_NHouses = 5
    Max_NHouses = 10
    consol_Ps, consol_Rs = compute_consolidated_levels(tariffs,
                                    cat_mu_tar,
                                    sd,
                                    NSubs,
                                    Min_NHouses,
                                    Max_NHouses,
                                    house_typ_limits)
    print(consol_Ps)
    print(consol_Rs)
