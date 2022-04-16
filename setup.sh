mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = $PORT\n\
headless = true\n\
maxUploadSize = 1028\n\
[global]\n\
dataFrameSerialization="legacy"\n\
[theme]\n\
primaryColor="#074A98"\n\
backgroundColor="#FFFFFF"\n\
secondaryBackgroundColor="#DFE3EA"\n\
textColor="#000000"\n\
font="sans serif"\n\
\n\
" > ~/.streamlit/config.toml




