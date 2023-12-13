# splunkcloud tools
**SavedSearches**
- Use **disabling_savedsearches.py** to disable all savedsearches before ACS or SSAI install in SplunkCloud.
The script will create a new directory with a copy of each app where the savedsearches will be disabled. The app from this directory should be installed in SplunkCloud.
>> Verify the results
  
- Use **rest_bulk_update_savedsearches.py** to enable the savedsearches per SearchHead(Cluster). Use the original app directory where not all savedsearches are disabled as input.
>> Verify the results

**Sanitize App Package**
- Use **sanitize_package.py** to clean up .tgz app packages before installation. This will clean up any unwanted hidden files, pax headers and set the correct permissions.
