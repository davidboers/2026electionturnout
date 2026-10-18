import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# TODO:
# * Median age
# * Turnout by method
# * Inactive
# * Regional breakdown


generations = pd.Series({
    '18-24': 'Gen Z',
    '25-29': 'Gen Z',
    '30-34': 'Millenials',
    '35-39': 'Millenials',
    '40-44': 'Millenials',
    '45-49': 'Gen X',
    '50-54': 'Gen X',
    '55-59': 'Gen X',
    '60-64': 'Boomers',
    '65-69': 'Boomers',
    '70-74': 'Boomers',
    '75-79': 'Boomers',
    '80-84': 'Silent',
    '85-89': 'Silent',
    '90-94': 'Silent',
    '95-99': 'Silent',
    '100+': 'Greatest'
})


sunday_counties = [
    'Bibb',
    'Chatham',
    'Clarke',
    'Clayton',
    'Cobb',
    'DeKalb',
    'Forsyth',
    'Fulton',
    'Gwinnett',
    'Henry',
    'Lamar',
    'Lowndes',
    'Muscogee',
    'Newton',
    'Rockdale',
    'Seminole'
]


df = pd.read_csv('export.csv')

def median_age(s: pd.Series) -> float:
    cumsum = s.cumsum()
    half = s.sum() / 2.0
    median_group = s[cumsum >= half].index[0]
    assert '-' in median_group
    [lower, upper] = median_group.split('-')
    [lower, upper] = [int(lower), int(upper)]
    group_ratio = 1 - ((cumsum[median_group] - half) / s[median_group])
    return median_group, lower + int(group_ratio * (upper - lower))


def age_group_sort(k):
    return k.map(lambda ki: 100 if ki == '100+' else int(ki[:2]))


def color_list(color: pd.Series | None, race: str, gender: str, default: str, age_groups):
    if color is None:
        return default
    
    lst = color[race, gender].sort_index(key=age_group_sort)
    return pd.Series(lst, index=age_groups).fillna('None')


def mk_tick(tick: int):
    if abs(tick) >= 2000:
        return f'{abs(int(tick / 1000)):,}k'

    elif abs(tick) >= 1000:
        z = tick / 1000
        return f'{abs(int(z) if int(z) == z else z):}k'

    else:
        return f'{abs(int(tick))}'


def mk_pyramids(df: pd.DataFrame, output_path: str, title: str, show_ex: bool = False, color: pd.Series | None = None, share_scale: bool = False, 
                pivot_path: str | None = None):
    fig, axes = plt.subplots(3, 2, figsize=(20, 14), squeeze=False)

    axes: list[plt.Axes] = [axes[0][0], axes[0][1], axes[1][0], axes[1][1], axes[2][0], axes[2][1]]

    pivot = df.pivot_table(values='Voter Count', index=['Race', 'Age Group'], columns=['Gender'], aggfunc='sum')

    if pivot_path is not None:
        pivot2 = pivot.copy()
        pivot2['Male'] = -pivot2['Male']
        pivot2.to_csv(f'./tabs/{pivot_path}')

    if share_scale:
        ylim = int(pivot.max().max() * 1.1)

    for race, ax in zip(['White', 'Black', 'Other/Unknown', 'Hispanic/Latino', 'Asian/Pacific Islander', 'American Indian or Alaskan Native'], axes):
        if race not in pivot.index:
            continue
        
        pivot_r = pivot.loc[race]
        pivot_r = pivot_r.sort_index(key=age_group_sort)

        if not share_scale:
            ylim = int(pivot_r.max().max() * 1.15)

        male_color = color_list(color, race, 'Male', 'skyblue', pivot_r.index)
        female_color = color_list(color, race, 'Female', 'lightcoral', pivot_r.index)
        other_color = color_list(color, race, 'Other', 'gray', pivot_r.index)

        male_ex = np.maximum(pivot_r['Male'] - pivot_r['Female'], 0) if show_ex else 0
        female_ex = np.maximum(pivot_r['Female'] - pivot_r['Male'], 0) if show_ex else 0

        ax.bar(pivot_r.index, -(pivot_r['Male'] - male_ex), color=male_color, label='Male')
        ax.bar(pivot_r.index, -male_ex, color='blue', label='Male - Excess', bottom=-(pivot_r['Male'] - male_ex)) if show_ex else None
        ax.bar(pivot_r.index, pivot_r['Female'] - female_ex, color=female_color, label='Female')
        ax.bar(pivot_r.index, female_ex, color='red', label='Female - Excess', bottom=pivot_r['Female'] - female_ex) if show_ex else None
        ax.bar(pivot_r.index, pivot_r['Other'], color=other_color, label='Other', bottom=-ylim)

        ax.set_title(race)

        ax.set_ylim(-ylim, ylim)

        # Left ticks
        ytick_eta = ylim // 4
        o = 10 ** (len(str(ytick_eta)) - 1)
        ytick_eta = (ytick_eta // o) * o
        ytick_lim = (ylim // ytick_eta) * ytick_eta
        yticks = np.arange(-ytick_lim, ytick_lim + ytick_eta, ytick_eta)
        ax.set_yticks(yticks)
        ax.set_yticklabels([mk_tick(tick) for tick in yticks])

        # Line
        ax.axhline(y=0, color='grey', linestyle='--')

        # Median annotations
        #male_mg, male_med = median_age(pivot_r['Male'])
        #female_mg, female_med = median_age(pivot_r['Female'])
        #ax.annotate(f'Median age: {male_med}', (male_mg, 0), (male_mg, -pivot_r.loc[male_mg, 'Male']),
        #            arrowprops={'arrowstyle': 'simple'})

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(f'./pics/{output_path}')


mk_pyramids(df, 'total.png', title='Georgia Registered Voters - 2026 general election', show_ex=True, pivot_path='total.csv')
mk_pyramids(df, 'total_same_scale.png', title='Georgia Registered Voters - 2026 general election', show_ex=True, share_scale=True)

# Primary
nullcolor = '#fff5f5'
party_color_dict = {
    'Republican': mcolors.LinearSegmentedColormap.from_list('Republicans', [nullcolor, 'crimson']),
    'Democratic': mcolors.LinearSegmentedColormap.from_list('Democrats', [nullcolor, 'royalblue']),
    'Nonpartisan': mcolors.LinearSegmentedColormap.from_list('Nonpartisan', [nullcolor, 'gold'])
}

min_scale = 0.4
scale = 1.0 / (1.0 - min_scale)

primary_df = pd.read_csv('primary2026.csv')
primary_vote_tallies = primary_df.pivot_table(values='Voter Count', index=['Race', 'Gender', 'Age Group'], columns='Party', aggfunc='sum').fillna(0)
primary_vote_shares = primary_vote_tallies.div(primary_vote_tallies.sum(axis=1), axis=0).fillna(0)
primary_party_colors = primary_vote_shares.apply(lambda s: party_color_dict[s.idxmax()]((s.max() - min_scale) * scale), axis=1)
mk_pyramids(primary_df, 'primary2026.png', title='2026 Primary Voters - Preferred Party', color=primary_party_colors)
mk_pyramids(primary_df, 'primary2026_same_scale.png', title='2026 Primary Voters - Preferred Party', color=primary_party_colors, share_scale=True)


print('Race/Gender disparity in vote share')
primary_vote_tallies = primary_vote_tallies.groupby(level=['Race', 'Gender']).agg(np.sum)
primary_vote_shares = primary_vote_tallies.div(primary_vote_tallies.sum(axis=1), axis=0).fillna(0) * 100
primary_margins = primary_vote_shares['Republican'] - primary_vote_shares['Democratic'] 
primary_margins = pd.DataFrame(primary_margins, columns=['Margin']).pivot_table(values='Margin', index=['Race'], columns=['Gender'])
print(primary_margins['Male'] - primary_margins['Female'])

mk_pyramids(primary_df[primary_df['Party'] == 'Democratic'], 'demprimary2026.png', title='2026 Democratic Primary Voters', show_ex=True, share_scale=True)
mk_pyramids(primary_df[primary_df['Party'] == 'Republican'], 'repprimary2026.png', title='2026 Republican Primary Voters', show_ex=True, share_scale=True)
