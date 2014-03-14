ckan.module("basiccharts_filters_form", function (jQuery) {
  "use strict";

  function applyDropdown(selectField, filterValues) {
    var self = this,
        inputField = selectField.parent().find('input'),
        input_value = inputField.val(),
        valueList;

    valueList = filterValues[selectField.val()];
    if (valueList) {
      inputField.replaceWith('<input type="hidden" value="" name="filter_values">');
      inputField = selectField.parent().find('input'),
      inputField.val(input_value);
      inputField.select2({
          data: valueList,
          width: '220px'
      })
    }
  }

  function initialize() {
    var self = this,
        templateFilterInputs = self.options.templateFilterInputs,
        filtersDiv = self.el.find(self.options.filtersSelector),
        addFilterEl = self.el.find(self.options.addFilterSelector),
        removeFilterSelector = self.options.removeFilterSelector,
        filterValues = self.options.filterValues;

    var selects = filtersDiv.find('select');
    selects.each(function (i, select) {
       applyDropdown($(select), filterValues);
    })

    addFilterEl.click(function (evt) {
      var inputField, selectField, valueList, input_value
      evt.preventDefault();
      filtersDiv.append(templateFilterInputs);
      selectField = filtersDiv.children().last().find('select');
      applyDropdown(selectField, filterValues)
    });


    filtersDiv.on("click", removeFilterSelector, function (evt) {
      evt.preventDefault();
      $(this).parent().remove();
    });

    filtersDiv.on("change", 'select', function (evt) {
      var inputField = $(this).parent().find('input');
      var select2Contianer = $(this).parent().find('.select2-container');
      evt.preventDefault();
      select2Contianer.remove();
      inputField.replaceWith('<input type="text" value="" name="filter_values">');
      inputField = $(this).parent().find('input');
      applyDropdown($(this), filterValues);
    });
  }

  return {
    initialize: initialize
  };
});
