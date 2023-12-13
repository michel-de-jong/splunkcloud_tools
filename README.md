# splunkcloud tools
**SavedSearches**
- Use **disabling_savedsearches.py** to disable all savedsearches before ACS or SSAI install in SplunkCloud. The script will create a new directory with a copy of each app where the savedsearches will be disabled. The app from this directory should be installed in SplunkCloud.
- Syntax: python3 disabling_savedsearches.py
- optional: -debug (Enable debug mode)
>> Verify the results
  
- Use **rest_bulk_update_savedsearches.py** to enable the savedsearches per SearchHead(Cluster). Use the original app directory where not all savedsearches are disabled as input.
- Syntax: python3 rest_bulk_update_savedsearches.py
- optional: -h (Help)
- optional: -debug (Enable debug mode, create an extra logfile with all debug logs)
- optional: -dummy (Run in dummy mode, bypasses the actual API calls)
>> Verify the results

**Sanitize App Package**
- Use **sanitize_package.py** to clean up .tgz app packages before installation. This will clean up any unwanted hidden files, pax headers and set the correct permissions.
