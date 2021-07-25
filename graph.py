import pandas as pd
import matplotlib
#Need this backend to annoying have the updated figure windows not pop to the foreground constantly
matplotlib.use("Qt5Agg")#https://stackoverflow.com/questions/45729092/make-interactive-matplotlib-window-not-pop-to-front-on-each-update-windows-7
#matplotlib.use('MACOSX')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DayLocator,DayLocator, HourLocator,MinuteLocator,SecondLocator, DateFormatter, drange, date2num
import seaborn as sns
import pdb
import matplotlib.ticker as ticker
import time, sys, getopt
from tqdm import tqdm

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

xlim_buf_frac_lft = 1.0
xlim_buf_frac_rght = 1.0
ylim_buffer_frac_top = 1.01
ylim_buffer_frac_bot = 0.99

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]
 
# Options
options = "hmo:"
 
# Long options
long_options = ["Help", "My_file", "Output ="]
 
try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
     
    # checking each argument
    for currentArgument, currentValue in arguments:
 
        if currentArgument in ("-h", "--Help"):
            print ("Displaying Help\n")
            print ("Simply enter a start and stop date-time in quotations!")
            print("For examples in the terminal: python3.9 graph.py -h \'2021-07-21 00:00:00\' \'2022-07-21 00:00:00\' \n\n")
            quit() 
        elif currentArgument in ("-m", "--My_file"):
            print ("Displaying file_name:", sys.argv[0])
             
        elif currentArgument in ("-o", "--Output"):
            print (("Enabling special output mode (% s)") % (currentValue))
             
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))
###############################################################################
plt.ion()
#Create Figure and axes here with shared x-axis
fig, (ax1, ax2, ax3) = plt.subplots(nrows=3,sharex=True,figsize=(20, 12))

while True:
    #Read in seperate files and change to a date format
    df = pd.read_csv('data.csv')
    df['Date-Time'] = pd.to_datetime(df['Date-Time'])

    df_bsc = pd.read_csv('data_bsc.csv')
    df_bsc['Date-Time'] = pd.to_datetime(df_bsc['Date-Time'])
    ###########################################################################
    # WARNING: This part was extremley confusing to troubleshoot to come up with graphable dataframe between two dates of interest!
    # It was absolutely needed because of the dataframes needing to be intersection merged (inner)and then annoying
    # since this removed all dates where there was no intersection, the data from those lost dates
    # needs to be recombined by concatinating the merged dataframe with a newly generated DF containing
    # data from the earlier dates  
    ###########################################################################
    # Need to combine Dfs based on closest timestamps down to the closest reasonable time (minutes)
    idk = df.merge(df_bsc, how='inner', on=['Month','Day','Hour','Minute'], suffixes=("","_BSC"))
    #Now need to create another dataframe that only contains data up until BSC starts recording
    lol = df[df['Date-Time'] <= df_bsc['Date-Time'].min()]
    #Now need to concat one on top of the other and then sort by Date-Time and make sure to fill in NAN and NAT's with zeros for later mathmatics
    df_new = pd.concat([idk,lol]).sort_values(by=['Date-Time']).fillna(0)
    ###############################################################################
    # WARNING:
    ###########################################################################
    #df_new = df.merge(df_bsc, how='outer', on=['Month','Day','Hour','Minute'], suffixes=("","_BSC")).fillna(0)
    #Create a new column for the new total column for holders and market cap
    
    df_new['Holders Total']=df_new['Holders']+df_new['Holders_BSC']
    df_new['Market Cap Total']=df_new['Market Cap']+df_new['Market Cap_BSC']
    df_new['Price Total']=df_new['Price']+df_new['Price_BSC']

    df_x_bound = df_new[(df_new['Date-Time'] >= sys.argv[1]) & (df_new['Date-Time']<= sys.argv[2])]
    
    x_start = df[df['Date-Time'] >= sys.argv[1]]['Date-Time'].min() #'2021-07-16 09:49:37']
    x_stop  = df[df['Date-Time'] <= sys.argv[2]]['Date-Time'].max()
    time_delta = (x_stop - x_start)
    
    linewidth=1
    alpha=0.5

    #First is just BSC
    ax1.plot(df['Date-Time'], df['Holders'], linewidth=linewidth, color='black', marker='.', markerfacecolor='red', markersize=4, markeredgecolor='black', markeredgewidth='.5')#plt.fill_between(ages, total_population)

    #ax1.scatter(df['Date-Time'], df['Holders'], marker='.',color='red')
    ax1.fill_between(df['Date-Time'], df['Holders'],label="EtherScan", color='blue', alpha=alpha)

    #Second is just BSC
    ax1.plot(df_bsc['Date-Time'], df_bsc['Holders'], linewidth=linewidth, color='black')# Graph just thse BSC Data
    ax1.fill_between(df_bsc['Date-Time'], df_bsc['Holders'],label="BSC", color='red', alpha=alpha)

    #Third is both EtherScan nd BSC
    ax1.plot(df_new['Date-Time'], df_new['Holders Total'], linewidth=linewidth, color='black')
    ax1.fill_between(df_new['Date-Time'], df_new['Holders Total'],label = "BSC and EtherScan", color='green', alpha=0.7)

    #Formating
    #ax1.set(title=f'Etherscan and BSC Webscrape MM Holders \n Start: {x_start} Stop: {x_stop}', xlabel='Date-Time', ylabel='Number of Holders')
    ax1.set(xlabel='Date-Time', ylabel='Number of Holders')
    ax1.set_title(f'Etherscan and BSC Webscrape MM Holders \n Start: {x_start} Stop: {x_stop}', fontsize=14,fontweight='bold')
    ax1.grid(color='black', linestyle='-', linewidth=linewidth, which='major', alpha=0.5)
    ax1.grid(color='grey', linestyle='-', linewidth=linewidth, which='minor', alpha=0.5)

    #Annotations
    max_hold = df_new[df_new['Holders Total'] == df_new['Holders Total'].max()].iloc[0]['Holders Total']
    max_hold_date = df_new[df_new['Holders Total'] == df_new['Holders Total'].max()].head(1)['Date-Time'].values #df[df['Holders'] == df['Holders'].max()].iloc[0]['Date-Time']
    ax1.annotate(f'BSC & EtherScan Holders ATH {max_hold:.0f}', xy=(max_hold_date,max_hold),
             xytext=(0,+40), xycoords='data', textcoords='offset pixels',arrowprops=dict(arrowstyle='-|>'),
              ha='center',fontsize=10, fontweight='bold')

    holders_most_recent_x = df_x_bound['Date-Time'].iloc[-1]
    holders_most_recent_y = df_x_bound['Holders Total'].iloc[-1]
    ax1.annotate(f'{holders_most_recent_y:.0f}', xy=(holders_most_recent_x,holders_most_recent_y),
             xytext=(-50,+50), xycoords='data', textcoords='offset pixels',arrowprops=dict(arrowstyle='-|>',connectionstyle="arc3,rad=-0.1"),
              ha='center',fontsize=10, fontweight='bold',bbox=dict(boxstyle="round4", fc="w"), alpha=0.5)

    ax1.set_xlim(left=x_start, right=x_stop)
    ax1.set_ylim(bottom=df_x_bound['Holders Total'].min()*ylim_buffer_frac_bot,
                 top=df_x_bound['Holders Total'].max()*ylim_buffer_frac_top)    
    ax1.legend(loc='lower right')
    ax1.set_facecolor('white')

    ###############################################################################
    ###############################################################################
    # First is just EtherScan
    ax2.plot(df['Date-Time'], df['Market Cap'], linewidth=linewidth, color='black')
    ax2.fill_between(df['Date-Time'], df['Market Cap'], label = "EtherScan",color='blue', alpha=alpha)

    #Second is just BSC
    ax2.plot(df_bsc['Date-Time'], df_bsc['Market Cap'], linewidth=linewidth, color='black')
    ax2.fill_between(df_bsc['Date-Time'], df_bsc['Market Cap'], label = "BSC",color='red', alpha=alpha)  

    #Third is both EtherScan and BSC
    ax2.plot(df_new['Date-Time'], df_new['Market Cap Total'], linewidth=linewidth, color='black')#Graph the BSC and EtherScape market cap dat
    ax2.fill_between(df_new['Date-Time'], df_new['Market Cap Total'], label = "BSC and EtherScan",color='green', alpha=alpha) 

    #Formating
    #ax2.set(title=f'Etherscan and BSC Webscrape MM Market Cap \n Start: {x_start} Stop: {x_stop}', xlabel='Date-Time', ylabel='Market Cap in Millions of Dollars')
    ax2.set(xlabel='Date-Time', ylabel='Market Cap in Millions of Dollars')
    ax2.set_title(f'Etherscan and BSC Webscrape MM Market Cap \n Start: {x_start} Stop: {x_stop}', fontsize=14,fontweight='bold')
    ax2.grid(color='black', linestyle='-', linewidth=1, which='major')
    ax2.grid(color='grey', linestyle='-', linewidth=linewidth, which='minor', alpha=0.25)

    #Annotations
    max_mc = df[df['Market Cap'] == df['Market Cap'].max()].iloc[0]['Market Cap']
    max_mc_date = df[df['Market Cap'] == df['Market Cap'].max()].head(1)['Date-Time'].values #df[df['Holders'] == df['Holders'].max()].iloc[0]['Date-Time']
    ax2.annotate(f'Market Cap ATH {max_mc}', xy=(max_mc_date,max_mc), xytext=(10,-100),
                textcoords='offset pixels', arrowprops=dict(arrowstyle='-|>'))
    
    mc_most_recent_x = df_x_bound['Date-Time'].iloc[-1]
    mc_most_recent_y = df_x_bound['Market Cap Total'].iloc[-1]
    ax2.annotate(f'{mc_most_recent_y:.0f}', xy=(mc_most_recent_x,mc_most_recent_y),
             xytext=(-50,+50), xycoords='data', textcoords='offset pixels',arrowprops=dict(arrowstyle='-|>',connectionstyle="arc3,rad=-0.1"),
              ha='center',fontsize=10, fontweight='bold',bbox=dict(boxstyle="round4", fc="w"), alpha=0.5)

    scale_y = 1e6
    ticks_y = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scale_y)) 
    ax2.set_xlim(left=x_start, right=x_stop)
    ax2.set_ylim(bottom=df_x_bound['Market Cap Total'].min()*ylim_buffer_frac_bot,
                 top=df_x_bound['Market Cap Total'].max()*ylim_buffer_frac_top)    
    ax2.legend(loc='lower right')
    ax2.set_facecolor('white')

    ##############################################################################
    # AXIS 3
    ##############################################################################
    ax3.plot(df['Date-Time'], df['Price'], linewidth=linewidth, color='black')
    ax3.fill_between(df['Date-Time'], df['Price'], label = "EtherScan",color='blue', alpha=alpha)

    #Formating
    #ax3.set(title=f'Etherscan and BSC Webscrape MM Price ($/MM) \n Start: {x_start} Stop: {x_stop}', xlabel='Date-Time', ylabel='Price in $/MM')
    ax3.set(xlabel='Date-Time', ylabel='Price in $/MM')
    ax3.set_title(f'Etherscan and BSC Webscrape MM Price ($/MM) \n Start: {x_start} Stop: {x_stop}', fontsize=14,fontweight='bold')
    ax3.grid(color='black', linestyle='-', linewidth=1, which='major')
    ax3.grid(color='grey', linestyle='-', linewidth=linewidth, which='minor', alpha=0.25)
    #Annotations
    max_price = df[df['Price'] == df['Price'].max()].iloc[0]['Price']
    max_price_date = df[df['Price'] == df['Price'].max()].head(1)['Date-Time'].values #df[df['Holders'] == df['Holders'].max()].iloc[0]['Date-Time']
    ax3.annotate(f'Price ATH {max_price}', xy=(max_price_date,max_price), xytext=(10,-100),
                textcoords='offset pixels', arrowprops=dict(arrowstyle='-|>'))
    
    price_most_recent_x = df_x_bound['Date-Time'].iloc[-1]
    price_most_recent_y = df_x_bound['Price Total'].iloc[-1]
    ax3.annotate(f'{price_most_recent_y:.0f}', xy=(price_most_recent_x,price_most_recent_y),
             xytext=(-50,+50), xycoords='data', textcoords='offset pixels',arrowprops=dict(arrowstyle='-|>',connectionstyle="arc3,rad=-0.1"),
              ha='center',fontsize=10, fontweight='bold',bbox=dict(boxstyle="round4", fc="w"), alpha=0.5)
    
    ax3.set_xlim(left=x_start, right=x_stop)
    ax3.set_ylim(bottom=df_x_bound['Price Total'].min()*ylim_buffer_frac_bot,
                 top=df_x_bound['Price Total'].max()*ylim_buffer_frac_top)    
    ax3.legend(loc='lower right')
    ax3.set_facecolor('white')

    #WARNING since the axes are shared, this formatting should only need to be applied once
    if time_delta.seconds < 1*60*60:
        print(f'The number of minutes are: {time_delta.seconds/60}')
        x_minor_lct = MinuteLocator(byminute = range(0,60+1,1))
        ax2.xaxis.set_minor_locator(x_minor_lct)
        ax2.xaxis.set_minor_formatter(mdates.DateFormatter("%M"))
        ax2.xaxis.set_major_locator(mdates.DayLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("\n%H")) 
    elif time_delta.days < 2:#This is done to better display ticks for the smaller date-time ranges
        x_minor_lct = HourLocator(byhour = range(0,24+1,1))
        ax2.xaxis.set_minor_locator(x_minor_lct)
        ax2.xaxis.set_minor_formatter(mdates.DateFormatter("%H"))
        ax2.xaxis.set_major_locator(mdates.DayLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("\n%D"))
    else:
        x_minor_lct = HourLocator(byhour = range(0,24+1,4))
        ax2.xaxis.set_minor_locator(x_minor_lct)
        ax2.xaxis.set_minor_formatter(mdates.DateFormatter("%H"))
        ax2.xaxis.set_major_locator(mdates.DayLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("\n%D"))

    
    
    ###############################################################################################
    # AXIS 4: Holder Rates
    ###############################################################################################
    # #pdb.set_trace()
    # date = pd.to_datetime('2021-07-16 09:44:36')
    # df_x_bound['Date-Time'].sub(date).abs().idxmin()#Returns index of timestamp
    # #The following will create a new column where 
    # def holder_rate(row):
    #     print(type(row))
    #     #print(row['Holders Total'])
    #     #pdb.set_trace()
    #     return(row+1)
    pdb.set_trace()
    # df_x_bound['Holder Rate'] = df_x_bound.apply(lambda row: holder_rate(row['Date-Time'], row['Holders']))
    # #df_x_bound['Holder Rate'] =  df_x_bound['Holders Total'].apply(lambda row: holder_rate(row))
    # pdb.set_trace()
    # df_x_bound['Holder Rate'] = df_x_bound['Holders Total'].apply(lambda x: (x - df_x_bound['Holders Total'].iloc[df_x_bound['Date-Time'].sub(date).abs().idxmin()])/((x['Date-Time']-date).seconds) )     ; df_x_bound
    # ##df_x_bound['Holders'].apply(lambda x: df_x_bound['Date-Time'].sub(date).abs().idxmin())
    
    
    
    fig.autofmt_xdate() # In this case, it just rotates the tick labels
    ax1.set_facecolor('white')
    plt.tight_layout()
    #plt.savefig(f'./graphs/MM_{time.ctime()}.png')
    
    print('Waiting to Update Graph')

    #https://stackoverflow.com/questions/45729092/make-interactive-matplotlib-window-not-pop-to-front-on-each-update-windows-7
    fig.canvas.draw_idle()#draw only if idle; defaults to draw but backends can overrride
    fig.canvas.start_event_loop(timeout=30)#Start an event loop. This is used to start a blocking event loop so that interactive functions, such as ginput and waitforbuttonpress, can wait for events. This should not be confused with the main GUI event loop, which is always running and has nothing to do with this.
    # The loading bar below works but while its running, you cannot move the graph and that kinda sucks
    # for i in tqdm (range (20), desc="Waiting for new data", ascii=False, ncols=100):
    #     time.sleep(1)
    fig.canvas.stop_event_loop()
    ax1.clear()
    ax2.clear()
    plt.cla()
    #time.sleep(2*60)
    #plt.draw()
    #plt.show()
    #time.sleep(10)
    #plt.pause(5)
    
    #plt.clf()
