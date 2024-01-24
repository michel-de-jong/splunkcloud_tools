# Splunk Cloud Tools
- Run splunkcloud_tools.py.
    - The option "Disable Savedsearches (pre-deployment)" is to disable all savedsearches before ACS or SSAI install in SplunkCloud. The script will create a new directory called apps_ss_disabled with a copy of each app where the savedsearches will be disabled. The original app will remain original. The apps from the apps_ss_disabled directory should be installed in SplunkCloud.
    - The option "Enable scheduled searches (post-deployment)" is to enable the savedsearches per SearchHead(Cluster). Use the original app directory where not all savedsearches are disabled as input.
        - Make sure that you have created a Splunk JWT Authentication Token and the user account has sufficient permissions for the API calls.
<br/><br/>
- Syntax: python3 splunkcloud_tools.py
- Optional: -h (help)
- Optional: -debug (Enable debug mode, create an extra logfile with all debug logs)
- Optional: -debug (Run in dummy mode, bypasses the actual API calls when running the enable scheduled searches script)
<br/><br/>
- Always verify the results
