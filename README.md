# collectd-logins
collectd python plugin for tracking user sessions and logins

Requires the following python2 modules: 
 - psutil
 - enum34

Example configuration:
```
LoadPlugin python
TypesDB "/opt/collectd_logins/logins_types.db"
<Plugin python>
  ModulePath "/opt/collectd_logins"
  Import "logins"
  <Module logins>
    Interval 5
    Window 3600
  </Module>
</Plugin>
```
