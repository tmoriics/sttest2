mkdir -p ~/.streamlit

echo "[server]
headless = true
port = $PORT
enableCORS = false
[theme]
primaryColor="#F63366"
backgroundColor="#88FF88"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif
" > ~/.streamlit/config.toml


