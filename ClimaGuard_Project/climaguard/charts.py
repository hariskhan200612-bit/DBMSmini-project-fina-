"""Shared Plotly formatting helpers."""
def plot_style(fig, height=270):
    fig.update_layout(
        template="plotly_dark", height=height,
        margin=dict(l=35, r=15, t=35, b=35),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe5ea", size=10),
        title_font=dict(size=12, color="#e9eef1"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
        xaxis=dict(gridcolor="rgba(255,255,255,.07)", zerolinecolor="rgba(255,255,255,.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,.07)", zerolinecolor="rgba(255,255,255,.08)"),
    )
    return fig
