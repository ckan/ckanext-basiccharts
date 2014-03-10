ckanext-basiccharts
===================

This extension adds Line, Bar and Pie charts to CKAN, using the new Resource
View being developed in https://github.com/ckan/ckan/tree/1251-resource-view.

It uses [Flot Charts](http://www.flotcharts.org), which is compatible with all
major browsers (including IE6+).

Installation
------------

To use it, simply clone this repository and run ```python setup.py install```.
Then add which charts you'd like to your ```ckan.plugins``` in your CKAN config
file.

You have to enable ```basiccharts``` before any of the other charts. Only then,
you can enable any (or all) of:

* linechart
* barchart
* piechart

Finally, restart your webserver. You should see the new chart types as options
in the view type's list on any resource that's in the DataStore.
