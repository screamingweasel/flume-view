#### Flume Monitor Ambari view
Simple Ambari View webpage to read agents.json file produced by check_flume.py

Author: [James Barnet](https://www.linkedin.com/in/jmbarnett)

-----------------
		
##### Setup

This should be done on the host running Ambari server
- Use git clone or other to pull this repo into a local directory (ex. git clone https://github.com/screamingweasel/flume-view.git)
- cd flume-view
- cp target/*.jar /var/lib/ambari-server/resources/views
- run ambari-server restart

This page uses client-side javascript to read a json file in its' own root folder, so you will need to create a link to it.
- By default check_flume.py creates an output file in /tmp/agents.json.
- Each time that a new version of a view is installed it created a new folder. Assuming this version (1.0.1) do the following
-   ln /tmp/agents.json /var/lib/ambari-server/resources/views/work/FLUME_VIEW{1.0.1}/agents.json

- Many thanks to Ali Bajwa for a great tutorial on views at https://github.com/abajwa-hw/iframe-view.git

