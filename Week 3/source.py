# Use the following data for this assignment:
%matplotlib notebook

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as stats

def get_df(seed_no, index):
    np.random.seed(seed_no)

    df = pd.DataFrame([np.random.normal(32000,200000,3650), 
                       np.random.normal(43000,100000,3650), 
                       np.random.normal(43500,140000,3650), 
                       np.random.normal(48000,70000,3650)], 
                      index=index)
    return df
    
def get_em95(df):
    
    df_de = df.describe()
    leng = len(df)
    
    # SEM = std. err. of the mean
    sem = stats.sem(df)
    
    # confidence interval = 95% = 0.95
    # calculate the t value
    t = -(stats.t.ppf((1-0.95)/2, leng-1))

    # error of the mean at 95% CI
    return (t * sem)

def plot():
    df = get_df(seed, index).T
    em95 = get_em95(df)
    fig, ax = plt.subplots()
    
    df_de = df.describe()
    err_range = pd.DataFrame([df_de.loc['mean']+em95, df_de.loc['mean']-em95])
    return fig, ax, df, em95, err_range

def update(color = ['lightgray' for _ in range(4)]):
    ax.bar(range(1,5,1),
           [df[i].mean() for i in index],
           width=0.95,
           yerr=em95,
           error_kw=dict(ecolor='black', lw=1, capsize=10, capthick=1),
           color=color)
    plt.xticks(range(1,5,1), index)

seed = 12345
index = [1992,1993,1994,1995]
click_count = 0

fig, ax, df, em95, err_range = plot()
    
update()
plt.gca().set_title('Please click on the plot.')

def onclick(event):
    plt.cla()
    update()
        
    global click_count
    global prev, level, y_range
    
    level = event.ydata
    plt.axhline(level, lw=1, c='gray')
    
    plt.gca().set_title('y = {}\nSelect a second point.'.format(event.ydata))
    
    if click_count == 0:
        click_count += 1
        
        # store the event.ydata
        prev = level
    else:
        y_range = pd.Series([prev, level])
        plt.gca().set_title('Selected range =\n[{}, {}]'.format(y_range[0], y_range[1]))
        click_count = 0
        recolor(y_range)
        plt.axhspan(prev, level, alpha=0.3, color='gray')

# do a t-test to check if selected range is similar to the 95%CI range of each mean 
def recolor(y_range):
    color = []
    for item in err_range:
        s, p = stats.ttest_ind(err_range[item], y_range)
        color.append(((1-p), 0, p, 0.9))
    update(color)
        
# tell mpl_connect we want to pass a 'button_press_event' into onclick when the event is detected
plt.gcf().canvas.mpl_connect('button_press_event', onclick)