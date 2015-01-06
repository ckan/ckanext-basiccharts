ckanext-basiccharts
===================

This extension adds Line, Bar and Pie charts to CKAN, using the new Resource
View that are still being developed on the master branch (currently
unreleased).

It uses [Flot Charts](http://www.flotcharts.org), which is compatible with all
major browsers (including IE6+).

Installation
------------

Clone this repository and run ```python setup.py install```. Then add which
charts you'd like to your ```ckan.plugins``` in your CKAN config file.

You can then enable any (or all) of:

* linechart
* barchart
* piechart
* basicgrid

Finally, restart your webserver. You should see the new chart types as options
in the view type's list on any resource that's in the DataStore.

Usage
-----

There are 3 kind of attributes that define what the chart will be: filters,
axes, and groups. We'll create charts in the next sections to define them all
using the following data:

| State      | Date       | Population   |
|------------|------------|--------------|
| California | 01-01-1990 | 29,760,021   |
| California | 01-01-2000 | 33,871,648   |
| California | 01-01-2010 | 37,253,956   |
| New York   | 01-01-1990 | 17,990,455   |
| New York   | 01-01-2000 | 18,976,457   |
| New York   | 01-01-2010 | 19,378,102   |

### Filters

If you don't want all data to be plotted in the chart, you can add filters.
Here, you define what to **include**.

For example, with the sample data, if you want to display just for California,
you'd create the filter:

```
State: California
```

Multiple filters on the same column work as ```OR```. For example, to plot just
the data for 01-01-2000 and 01-01-2010, you'd do:

```
Date: 01-01-2000
Date: 01-01-2010
```

Multiple filters on different columns work as ```AND```. If we'd add all
filters defined in the last paragraphs, we would plot data only for California
in 01-01-2000 or 01-01-2010. In techie terms, it'll be ```State == "California"
AND (Date == "01-01-2000" OR Date == "01-01-2010")```

Currently you can't exclude data, only include. There's no way to negate a
filter (to all states that are not California, for example).

To learn more about filters, check
[ckanext-viewhelpers](//github.com/ckan/ckanext-viewhelpers).

### Axes

This defines what column will be plotted in each axis. Line and bar charts have
two axes, Y and X; pie charts only have one, Y.

As long as the DataStore interpreted the column types correctly, the charts
will work with any kind of data (numeric, text, or date). To check if this is
the case, check the ```Upload log``` in the ```Manage resource```'s
```DataStore``` tab. You should see something like:

```
Determined headers and types: [{'type': u'text', 'id': u'State'}, {'type':
u'timestamp', 'id': u'Date'}, {'type': u'numeric', 'id': u'Population'}]
```

Just confirm that the types defined are correct. If not, try to understand why
and fix it, as the charts created might behave incorrectly. The DataStore's
documentation might help you.

### Groups

This allows you to group the data being plotted, based on a certain column.
It's optional for bar and line charts, but required for pie charts.

For example, say that you want to create a line chart that shows California and
New York's population growth. You define ```Date``` to be your X axis, and
```Population``` to be your Y axis. Then, when you preview the chart, it'll be
like:

![Timeline of population growth without groups](doc/img/linechart-date-population-no-groups.png)

Not what you'd want. The problem is that when there's no group, all data is
groupped together. You'd like to separate the population from California from
the New York's. To do that, you need to group by ```State```.

![Timeline of population growth groupped by state](doc/img/linechart-date-population-with-groups.png)

Much better. Notice that there's a group's legend as well. To enable it, you
need to check ```Show groups' legend```.

The bar chart works similarly. The pie charts are a bit different. To define
them, you're required to set up a column to group by. With the same data, if
you'd want to create a chart for, given the sum of California and New York's
population, which percentage belongs to one and which to the other, you'd set
up group by as ```State```, and Y axis as ```Population```. That'll create:

![Timeline of population growth groupped by state](doc/img/piechart-population-by-state.png)

Beware that as we have multiple rows for the same group, what's being plotted
on the pie chart is the sum of all values. In this case, the sum of the
population in 1990, 2000, and 2010. If you want a single year, add a filter.

As the legends are always embedded in the chart, there's no ```Show groups'
legend``` option.

Common problems
---------------

### There are no side-by-side bars

If you'd tried plotting a timeline of the population growth in California and
New York as a bar chart, as we did in the last section using a line chart,
you'd end up with something like this:

![Timeline of population growth groupped by state as bars](doc/img/barchart-date-population-with-groups-problem.png)

Don't let this fool you. It looks like a stacked bar chart, but it's not
(there's no stacked bars chart as well). The bars aren't stacked, they're
drawn over each other. This almost always isn't what you want. To fix it, we
need to support side-by-side bars, but we don't yet. If you'd like to help,
check issue [#8](https://github.com/ckan/ckanext-basiccharts/issues/8).

License
-------

Copyright (C) 2014 Open Knowledge Foundation

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
