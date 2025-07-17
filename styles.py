# styles.py

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
            background-color: #EAEAEA;
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

        /* Channel contribution title */
        .channel-main-title {
            color: #0056b3;
            text-align: center;
            font-size: 26px;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 20px;
        }

        /* Channel header box */
        .channel-header-box {
            background-color: #FFFBEA;
            padding: 12px;
            border-radius: 8px 8px 0 0;
            text-align: center;
            border: 1px solid #E0E0E0;
            border-bottom: none;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .channel-header-box h5 {
            margin-bottom: 4px;
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }
        .channel-header-box p {
            margin-bottom: 0;
            font-size: 1.2em;
            font-weight: bold;
            color: #007bff;
        }

        /* --- MODIFIED: Enforce fixed height and internal scrolling for alignment --- */
        .channel-detail-box {
            padding: 15px;
            border-radius: 0 0 8px 8px; /* Rounded bottom corners */
            height: 200px; /* Use fixed height instead of min-height */
            border: 1px solid #E0E0E0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 15px; /* Space below detail box */
            font-size: 0.95em;
            overflow-y: auto; /* Add vertical scrollbar if content overflows */
            display: block; /* Ensure it behaves as a block-level element */
        }
        .channel-detail-box-white {
            background-color: #FFFFFF;
        }
        .channel-detail-box-gray {
            background-color: #F7F7F7; /* Lighter gray */
        }
        .channel-detail-box ul {
            padding-left: 20px;
            margin-bottom: 0;
            list-style-type: none;
        }
        .channel-detail-box li {
            margin-bottom: 5px;
            position: relative;
            padding-left: 15px;
        }
        .channel-detail-box li::before {
            content: "-";
            position: absolute;
            left: 0;
            color: #007bff;
            font-weight: bold;
        }

        /* Pie chart container */
        .pie-chart-container { text-align: center; min-height: 0px; display: flex; align-items: center; justify-content: center; margin-top: 0px; margin-bottom: 15px; }
        .pie-chart-title { text-align: center; font-weight: bold; color: #495057; margin-bottom: 0px; font-size: 1.1em; }

        /* File Uploader */
        .stFileUploader { border: 2px dashed #007bff; border-radius: 8px; padding: 20px; background-color: #F8F9FA; text-align: center; }
        .stFileUploader label { font-weight: bold !important; color: #007bff !important; }
        .stFileUploader label span p { font-size: 1.1em !important; }
    </style>
    """