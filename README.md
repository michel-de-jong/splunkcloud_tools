# Splunk Cloud Tools
- Run splunkcloud_tools.py.
    - "**Disable Savedsearches (pre-deployment)**" is to disable all savedsearches before ACS or SSAI install in SplunkCloud. The script will create a new directory called apps_ss_disabled with a copy of each app where the savedsearches will be disabled. The original app will remain original. The apps from the apps_ss_disabled directory should be installed in SplunkCloud.
    - "**Enable scheduled searches (post-searches-deployment)**" is to enable the savedsearches per Search Head (Cluster). Use the original app directory where not all savedsearches are disabled as input.
        - Ensure that you have created a Splunk JWT Authentication Token and that the user account has sufficient permissions for the API calls.
     - "**Create scheduled searches (post-app-deployment) (BETA)**" is to create the savedsearches per Search Head (Cluster) with all evailable parameters from the original savedsearches.conf. Be aware that everything will be created in app/local and has app-level sharing.
        - Ensure that you have created a Splunk JWT Authentication Token and that the user account has sufficient permissions for the API calls.
        - The searches created are currently owned by the Nobody user. This might be enhanced in the future.
<br/><br/>
- Syntax: python3 splunkcloud_tools.py
- Optional: -h (help)
- Optional: -debug (Enable debug mode, create an extra log file with all debug logs)
- Optional: -dummy (Run in dummy mode, bypasses the actual API calls when running the enable scheduled searches script)
<br/><br/>
- Always verify the results
