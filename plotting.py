# plotting.py

import plotly.graph_objects as go
import plotly.express as px


def create_pie_chart(labels, values, title):
    """Creates a Plotly pie chart."""
    if not labels or not values or sum(values) == 0:
        return None

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        textinfo='label+percent',
        insidetextorientation='radial',
        hole=.3,
        marker_colors=px.colors.qualitative.Pastel,
        # --- MODIFIED: Customize hover text to show only label and percentage ---
        hovertemplate='%{label}: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    return fig