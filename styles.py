def get_custom_css():
    """Returns a string containing custom CSS for the Streamlit app."""
    return """
    <style>
        /* Global page background */
        .stApp {
            background-color: #FFFEF4;
        }

        /* Main title "岗位&渠道数据展示面板" */
        .main-title-container {
            background-color: #EAEAEA; /* Light gray */
            padding: 10px 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .main-title-container h2 {
            margin: 0;
            color: #333;
        }

        /* Data type selector container */
        .data-type-container {
            background-color: #EAEAEA; /* Light gray */
            padding: 8px 15px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 300px; /* Limit width */
        }
        .data-type-container .stSelectbox > div[data-baseweb="select"] > div {
            background-color: #F8F9FA;
        }


        /* Filter section styling */
        .filter-section-title {
            font-weight: bold;
            font-size: 1.1em;
            color: #555;
            padding: 8px 15px;
            background-color: #F0F0F0;
            border-radius: 6px;
            display: inline-block; /* Make background fit content */
            margin-right: 10px; /* Space between title and widgets */
        }

        .stMultiSelect > div[data-baseweb="select"] > div {
             background-color: #F8F9FA; /* Light background for multiselect */
        }
        .stSlider > div[data-testid="stTickBar"] > div {
            background-color: #D0D0D0; /* Slider track color */
        }


        /* Channel contribution title "渠道入职贡献率" */
        .channel-main-title {
            color: #0056b3; /* Darker Blue */
            text-align: center;
            font-size: 26px;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 20px;
        }

        /* Channel header box (e.g., "媒体 百分比") */
        .channel-header-box {
            background-color: #FFFBEA; /* Light Yellowish */
            padding: 12px;
            border-radius: 8px 8px 0 0; /* Rounded top corners */
            text-align: center;
            border: 1px solid #E0E0E0;
            border-bottom: none; /* Join with detail box */
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .channel-header-box h5 { /* Channel name */
            margin-bottom: 4px;
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }
        .channel-header-box p { /* Percentage */
            margin-bottom: 0;
            font-size: 1.2em;
            font-weight: bold;
            color: #007bff;
        }

        /* Channel detail box (alternating colors) */
        .channel-detail-box {
            padding: 15px;
            border-radius: 0 0 8px 8px; /* Rounded bottom corners */
            min-height: 180px; /* Ensure consistent height */
            border: 1px solid #E0E0E0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 15px; /* Space below detail box */
            font-size: 0.95em;
        }
        .channel-detail-box-white {
            background-color: #FFFFFF;
        }
        .channel-detail-box-gray {
            background-color: #F7F7F7; /* Lighter gray than F0F0F0 */
        }
        .channel-detail-box ul {
            padding-left: 20px;
            margin-bottom: 0;
            list-style-type: none; /* Remove default bullets */
        }
        .channel-detail-box li {
            margin-bottom: 5px;
            position: relative;
            padding-left: 15px; /* Space for custom bullet */
        }
        .channel-detail-box li::before {
            content: "-"; /* Custom bullet */
            position: absolute;
            left: 0;
            color: #007bff;
            font-weight: bold;
        }
        .channel-detail-box .internal-team-text {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            font-weight: bold;
            font-size: 1.1em;
            color: #555;
        }


        /* Pie chart container */
        .pie-chart-container {
            text-align: center;
            min-height: 0px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 0px;
            margin-bottom: 15px;
        }
        .pie-chart-title {
            text-align: center;
            font-weight: bold;
            color: #495057;
            margin-bottom: 0px;
            font-size: 1.1em;
        }

        /* File Uploader */
        .stFileUploader {
            border: 2px dashed #007bff;
            border-radius: 8px;
            padding: 20px;
            background-color: #F8F9FA;
            text-align: center;
        }
        .stFileUploader label { /* "Drag and drop file here..." or "Browse files"*/
            font-weight: bold !important;
            color: #007bff !important;
        }
        .stFileUploader label span p {
             font-size: 1.1em !important;
        }
        .file-uploader-info-text {
            color: #6c757d;
            font-style: italic;
            margin-top: 10px;
        }
    </style>
    """