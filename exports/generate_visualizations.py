import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.graph_objects as go
from pathlib import Path

def main():
    base_dir = Path(r"D:\My files\courses\Courses\Tableau & PowerBI\Tableau Full course-20200617T142315Z-001\Tableau Full course")
    ball_csv = base_dir / "Ball_by_Ball.csv"
    player_csv = base_dir / "Player.csv"
    out_dir = Path(r"D:\Mega Projects\LearnAIAgent\exports")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading Ball_by_Ball.csv...")
    df = pd.read_csv(ball_csv)
    players = pd.read_csv(player_csv)

    # 1. Clean data: Parse Batsman_Scored
    df['Runs'] = pd.to_numeric(
        df['Batsman_Scored'].astype(str).str.strip().replace({'Do_nothing': 0, '': 0}),
        errors='coerce'
    ).fillna(0).astype(int)

    # Group by Striker_Id
    top_batsmen = df.groupby('Striker_Id')['Runs'].agg(
        Total_Runs='sum',
        Balls_Faced='count'
    ).reset_index()

    # Merge metadata
    merged = top_batsmen.merge(
        players[['Player_Id', 'Player_Name']],
        left_on='Striker_Id',
        right_on='Player_Id',
        how='left'
    )
    merged['Player_Name'] = merged['Player_Name'].fillna('Player ID ' + merged['Striker_Id'].astype(str))
    merged['Strike_Rate'] = (merged['Total_Runs'] / merged['Balls_Faced'] * 100).round(2)

    top10_desc = merged.sort_values('Total_Runs', ascending=False).head(10).copy()
    top10_asc = top10_desc.sort_values('Total_Runs', ascending=True).reset_index(drop=True)

    # 2. Publication-Quality Matplotlib Bar Chart (300 DPI & SVG)
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)

    highlight_color = '#1A73E8'  # Google Blue for #1
    regular_color = '#607D8B'    # Restrained slate steel for contenders
    colors = [highlight_color if name == 'SK Raina' else regular_color for name in top10_asc['Player_Name']]

    y_pos = np.arange(len(top10_asc))
    bars = ax.barh(y_pos, top10_asc['Total_Runs'], height=0.62, color=colors, edgecolor='none', zorder=3)

    for bar in bars:
        width = bar.get_width()
        is_top = (width == top10_asc['Total_Runs'].max())
        label_color = highlight_color if is_top else '#202124'
        weight = 'bold' if is_top else 'normal'
        ax.text(
            width + 45,
            bar.get_y() + bar.get_height() / 2,
            f"{width:,} runs",
            ha='left',
            va='center',
            fontsize=10.5,
            fontweight=weight,
            color=label_color,
            zorder=4
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(top10_asc['Player_Name'], fontsize=11, fontweight='500', color='#202124')
    ax.set_xlim(0, 4800)
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_xlabel('Cumulative Runs Scored', fontsize=11, fontweight='bold', color='#3C4043', labelpad=12)

    ax.xaxis.grid(True, linestyle='--', alpha=0.35, color='#B0BEC5', zorder=0)
    ax.yaxis.grid(False)

    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#CFD8DC')
    ax.spines['bottom'].set_linewidth(1.0)
    ax.tick_params(axis='both', which='both', length=0, labelsize=10.5, colors='#5F6368')

    plt.title(
        'Top 10 All-Time Run Scorers in Indian Premier League (2008 – 2016)',
        fontsize=15,
        fontweight='bold',
        color='#202124',
        loc='left',
        pad=24
    )

    ax.text(
        0.0, 1.025,
        'Suresh Raina leads the all-time leaderboard with 4,106 runs, edging Virat Kohli (4,105 runs) by a historic single run.',
        transform=ax.transAxes,
        fontsize=10.5,
        color='#5F6368',
        ha='left'
    )

    ax.annotate(
        'Raina edges Kohli\nby exactly 1 run (4,106 vs 4,105)',
        xy=(4106, y_pos[-1]),
        xytext=(3400, y_pos[-2] - 0.4),
        arrowprops=dict(arrowstyle='->', color='#1A73E8', lw=1.2, connectionstyle='arc3,rad=-0.2'),
        fontsize=9.5,
        fontweight='500',
        color='#1A73E8',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#E8F0FE', edgecolor='#D2E3FC', alpha=0.9),
        zorder=5
    )

    plt.figtext(
        0.08, 0.015,
        'Source: IPL Ball_by_Ball Delivery-Level Dataset (136,590 deliveries) | Metric: Cumulative Batsman Runs Scored',
        fontsize=8.5,
        color='#80868B',
        ha='left'
    )

    plt.tight_layout(rect=[0.05, 0.04, 0.98, 0.96])

    png_path = out_dir / 'ipl_top_run_scorers_barchart.png'
    svg_path = out_dir / 'ipl_top_run_scorers_barchart.svg'

    fig.savefig(png_path, dpi=300, facecolor='#FFFFFF', edgecolor='none')
    fig.savefig(svg_path, format='svg', facecolor='#FFFFFF', edgecolor='none')
    plt.close(fig)

    # 3. Interactive Plotly Figure
    plotly_colors = ['#1A73E8' if name == 'SK Raina' else '#5F6368' for name in top10_asc['Player_Name']]
    plotly_fig = go.Figure(go.Bar(
        x=top10_asc['Total_Runs'],
        y=top10_asc['Player_Name'],
        orientation='h',
        marker=dict(color=plotly_colors, line=dict(width=0)),
        text=[f"{r:,} runs" for r in top10_asc['Total_Runs']],
        textposition='outside',
        customdata=top10_asc[['Balls_Faced', 'Strike_Rate']],
        hovertemplate='<b>%{y}</b><br>Runs: %{x:,}<br>Balls: %{customdata[0]:,}<br>Strike Rate: %{customdata[1]}<extra></extra>'
    ))

    plotly_fig.update_layout(
        title=dict(
            text='<b>Top 10 All-Time Run Scorers in Indian Premier League (2008 – 2016)</b>',
            x=0.02,
            font=dict(family='Inter, Roboto, sans-serif', size=18, color='#202124')
        ),
        xaxis=dict(
            title='<b>Cumulative Runs Scored</b>',
            showgrid=True,
            gridcolor='#F1F3F4',
            zeroline=False,
            range=[0, 4800],
            tickformat=','
        ),
        yaxis=dict(
            title='',
            showgrid=False
        ),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        margin=dict(l=140, r=60, t=80, b=50),
        font=dict(family='Inter, Roboto, sans-serif')
    )

    html_path = out_dir / 'ipl_top_run_scorers_interactive.html'
    json_path = out_dir / 'ipl_top_run_scorers.json'
    plotly_fig.write_html(str(html_path))
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(plotly_fig.to_json())

    print("All exports generated successfully:")
    print(f" - PNG (300 DPI): {png_path}")
    print(f" - SVG: {svg_path}")
    print(f" - Interactive HTML: {html_path}")
    print(f" - Plotly JSON: {json_path}")

if __name__ == '__main__':
    main()

