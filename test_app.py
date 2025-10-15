import pytest
from dash import Dash
from app_final import app  # 如果你的文件叫 app.py 就改成 from app import app

@pytest.fixture
def dash_duo(dash_duo):
    return dash_duo

def test_header_is_present(dash_duo):
    dash_duo.start_server(app)
    header = dash_duo.find_element("h1")
    assert header is not None
    assert "Pink Morsels" in header.text

def test_graph_is_present(dash_duo):
    dash_duo.start_server(app)
    graph = dash_duo.find_element("div.js-plotly-plot")
    assert graph is not None

def test_region_picker_is_present(dash_duo):
    dash_duo.start_server(app)
    radio = dash_duo.find_element("#region-selector")
    assert radio is not None