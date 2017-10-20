import matplotlib.pyplot as plt
import mplleaflet
import pandas as pd
import matplotlib.dates as dates
# import matplotlib.ticker as ticker
import datetime

hashid = '9b8a3493628de4a545ca348012ca3563e0a85b955446eef6f8fdafb5'
filename = 'data/C2A2_data/BinnedCsvs_d25/9b8a3493628de4a545ca348012ca3563e0a85b955446eef6f8fdafb5.csv'

def leaflet_plot_stations(binsize, hashid):

    df = pd.read_csv('data/C2A2_data/BinSize_d{}.csv'.format(binsize))

    station_locations_by_hash = df[df['hash'] == hashid]

    lons = station_locations_by_hash['LONGITUDE'].tolist()
    lats = station_locations_by_hash['LATITUDE'].tolist()

    plt.figure(figsize=(8,8))

    plt.scatter(lons, lats, c='r', alpha=0.7, s=200)

    return mplleaflet.display()

# leaflet_plot_stations(25, hashid)

def get_weather_info(filename):
    
    df = pd.read_csv(filename)
    
    # 0.1 * Data_Value to normalize the unit to Celcius
    df['Data_Value'] = df['Data_Value'].map(lambda x: 0.1 * x)
    
    # get rid of leap days
    df = df.mask(df['Date'].str.contains('02-29')).dropna()
    
    # split into df_max, df_min
    df_max = df[df['Element'] == 'TMAX'].sort_values('Date')
    df_min = df[df['Element'] == 'TMIN'].sort_values('Date')
    
    t_max = df_max.mask(df_max['Date'].str.contains('2015')).dropna()
    t_min = df_min.mask(df_min['Date'].str.contains('2015')).dropna()
    
    f_max = df_max.where(df_max['Date'].str.contains('2015')).dropna()
    f_min = df_min.where(df_min['Date'].str.contains('2015')).dropna()
    
    return [t_max, t_min, f_max, f_min]

def condense(dfs):
    
    for i, df in enumerate(dfs):
        
        #df['Year'] = df['Date'].str[:4]
        df['Date'] = '2015-' + df['Date'].str[5:]
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        
        if (i%2 == 0):
            dfs[i] = df.groupby(['Date'])['Data_Value'].max()
        else:
            dfs[i] = df.groupby(['Date'])['Data_Value'].min()

    return dfs

def plot_graph():
    
    dfs = get_weather_info(filename)
    dfs = condense(dfs)
    
    # subplots, plot size
    fig, ax1 = plt.subplots(figsize=(30,15))
    
    # despine
    for spine in ax1.spines:
        ax1.spines[spine].set_visible(False)
    
    # grid
    ax1.grid(linestyle='--', linewidth=2, alpha=0.2, axis='x')
    # ax1.grid(linestyle='-', linewidth=2, alpha=1, axis='y', color='lightgrey')
    
    # ticks
    plt.tick_params(
        axis='both',
        which='both',
        bottom='off',
        top='off',
        labelbottom='off')
    
    # set x-axis limit
    ax1.set_xlim([datetime.date(2014, 12, 31), datetime.date(2016, 1, 1)])
    
    # set y-axis limit
    ax1.set_ylim([-4, 49.9])
    
    # plot title
    # plt.title('Daily Record High/Low temperature, South East Asia, Day by Day: 2015 vs 2005-2014', fontsize = 30)
    ax1.annotate('Record High & Low Temperature (°C), Day by Day'.upper(),
                 (datetime.date(2015,1,3), 47.5), fontsize=30, color='grey')
    ax1.annotate('South East Asia: 2015 vs 2005-2014'.upper(),
                 (datetime.date(2015,1,3), 45.5), fontsize=25, color='grey', weight='light')
    
    p5 = plt.scatter(dfs[0].index, dfs[0].values, alpha=0.5, color='lightgrey', s=10)
    p10 = plt.scatter(dfs[1].index, dfs[1].values, alpha=0.5, color='lightgrey', s=10)
    
    # fill the area between two lines
    p15 = plt.fill_between(dfs[0].index, dfs[0].values, dfs[1].values, alpha =0.3, color='lightgrey')
    
    # record highs/lows in 2015
    a_max = plt.scatter(dfs[2].index, dfs[2].values, alpha=1, color='lightsalmon', s=15, marker='D')
    a_min = plt.scatter(dfs[3].index, dfs[3].values, alpha=1, color='lightsteelblue', s=15, marker='D')
    
    # records in 2015 that broke old records
    broke_max = dfs[2].where(dfs[2].values > dfs[0].values).dropna()
    broke_min = dfs[3].where(dfs[3].values < dfs[1].values).dropna()
    
    # draw
    b_max = plt.scatter(broke_max.index, broke_max.values, alpha=0.8, color='orangered', marker='D', s=75)
    b_min = plt.scatter(broke_min.index, broke_min.values, alpha=0.8, color='dodgerblue', marker='D', s=75)
        
    # month locator
    ax1.xaxis.set_major_locator(dates.MonthLocator())
    ax1.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=15))
    ax1.xaxis.set_major_formatter(ticker.NullFormatter())
    ax1.xaxis.set_minor_formatter(dates.DateFormatter('%b'))

    month_anno = (('JAN', datetime.date(2015,1,16)),
                  ('FEB', datetime.date(2015,2,15)),
                  ('MAR', datetime.date(2015,3,16)),
                  ('APR', datetime.date(2015,4,16)),
                  ('MAY', datetime.date(2015,5,16)),
                  ('JUN', datetime.date(2015,6,16)),
                  ('JUL', datetime.date(2015,7,16)),
                  ('AUG', datetime.date(2015,8,16)),
                  ('SEP', datetime.date(2015,9,16)),
                  ('OCT', datetime.date(2015,10,16)),
                  ('NOV', datetime.date(2015,11,16)),
                  ('DEC', datetime.date(2015,12,16)))
    
    for name, x in month_anno:
        ax1.annotate(name, (x, 28.0), horizontalalignment='center', fontsize=25, color='grey', weight='light')
    
    legend1 = plt.legend([b_max, a_max, p5, b_min, a_min],
               ['All-Time Record High(2015)',  'Daily High(2015)', 'Past Record High/Low (2005-2014)', 'All-Time Record Low(2015)', 'Daily Low(2015)'],
               loc='upper right',
               labelspacing=1,
               frameon=False,
               ncol=2)
    
    plt.show()
        
plot_graph()