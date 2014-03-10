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

Usage
-----

There are 3 kind of attributes that define what the chart will be: filters,
groups, and axes.

### Filters

If you don't want all data to be plotted in the chart, you can add filters.
Here, you define what to **include**. For example, consider the following data:

| State      | Year | Population   |
|------------|------|--------------|
| California | 1990 | 29,760,021   |
| California | 2000 | 33,871,648   |
| California | 2010 | 37,253,956   |
| New York   | 1990 | 17,990,455   |
| New York   | 2000 | 18,976,457   |
| New York   | 2010 | 19,378,102   |

If you want to display just data for California, you'd create a filter:

```
State: California
```

When adding multiple filters on the same column, they work as ```OR```. For
example, to plot just the data for 2000 and 2010, you'd do:

```
Year: 2000
Year: 2010
```

Multiple filters on different columns work as ```AND```. If we'd add all
filters defined in the last paragraphs, we would plot data only for California
in 2000 or 2010. In techie terms, it'll be ```State == "California" AND (Year
== 2000 OR Year == 2010)```

Currently you can't exclude data, only include. There's no way to negate a
filter (to all states that are not California, for example).
