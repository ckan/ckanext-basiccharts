ckan.module("basiccharts_view", function (jQuery) {
  "use strict";

  function setupParams(defaultParams, chartType) {
    var routeParams = window.location.search.queryStringToJSON(),
        params = {
          chart_type: chartType,
          filters: setupFilters(defaultParams.filters)
        };

    return $.extend({}, defaultParams, routeParams, params);
  }

  function setupFilters(defaultFilters) {
    var routeFilters = ckan.views.filters.get();

    return $.extend({}, defaultFilters, routeFilters);
  }

  function initialize() {
    var self = this,
        endpoint = self.options.endpoint || self.sandbox.client.endpoint + "/api",
        chartType = self.options.chartType,
        resourceView = self.options.resourceView,
        params = setupParams(resourceView, chartType),
        elementId = "#"+self.el.context.id,
        resource = {
          id: self.options.resourceId,
          endpoint: endpoint
        };

    function sortData(data) {
      var result = data,
          filtersKeys = Object.keys(params.filters).sort(),
          filtersKeysLength = filtersKeys.length;

      data.sort(function (a, b) {
        // Sort by params' filters
        for (var i = 0; i < filtersKeysLength; i++) {
          var filtersValues = params.filters[filtersKeys[i]],
              aFilterIndex = filtersValues.indexOf(a[filtersKeys[i]]),
              bFilterIndex = filtersValues.indexOf(b[filtersKeys[i]]),
              result = aFilterIndex - bFilterIndex;

          if (result !== 0) {
            return result;
          }
        }

        // Sort by groupBy
        if (params.group_by && params.chart_type != "pie") {
          var aGroupBy = a[params.group_by],
              bGroupBy = b[params.group_by],
              result = aGroupBy.localeCompare(bGroupBy);

          if (result !== 0) {
            return result;
          }
        }

        // Sort by xAxis or yAxis (depending if it's horizontal or vertical)
        var axis = (params.horizontal) ? params.x_axis : params.y_axis;
        var aValue = parseFloat(a[axis]),
            bValue = parseFloat(b[axis]);
        if (isNaN(aValue) || isNaN(bValue)) {
          // We need to keep all NaN values at one end of the sorted array
          if (isNaN(aValue)) {
            return -1;
          } else if (isNaN(bValue)) {
            return 1;
          }
          return 0;
        } else {
          return aValue - bValue;
        }
      });

      return result;
    }

    ckan.views.basiccharts.init(elementId, resource, params, sortData);
  }

  return {
    initialize: initialize
  };
});
