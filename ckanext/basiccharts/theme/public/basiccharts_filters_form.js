ckan.module("basiccharts_filters_form", function (jQuery) {
  "use strict";

  function applyDropdown(selectField, filterValues) {
    var inputField = selectField.parent().find('input'),
        inputValue = inputField.val(),
        valueList = filterValues[selectField.val()];

    if (valueList) {
      inputField.select2({
          data: valueList,
          width: '220px'
      });
    }
  }

  function initialize() {
    var self = this,
        templateFilterInputs = self.options.templateFilterInputs,
        inputFieldTemplateEl = $(templateFilterInputs).find('input[type="text"][name]'),
        filtersDiv = self.el.find(self.options.filtersSelector),
        addFilterEl = self.el.find(self.options.addFilterSelector),
        removeFilterSelector = self.options.removeFilterSelector,
        filterValues = self.options.filterValues || {};

    var selects = filtersDiv.find('select');
    selects.each(function (i, select) {
       applyDropdown($(select), filterValues);
    });

    addFilterEl.click(function (evt) {
      var selectField;
      evt.preventDefault();
      filtersDiv.append(templateFilterInputs);
      selectField = filtersDiv.children().last().find('select');
      applyDropdown(selectField, filterValues);
    });

    filtersDiv.on('click', removeFilterSelector, function (evt) {
      evt.preventDefault();
      $(this).parent().remove();
    });

    filtersDiv.on('change', 'select', function (evt) {
      var el = $(this),
          parentEl = el.parent(),
          inputField = parentEl.find('input'),
          select2Container = parentEl.find('.select2-container');
      evt.preventDefault();
      select2Container.remove();
      inputField.replaceWith(inputFieldTemplateEl.clone());
      applyDropdown(el, filterValues);
    });
  }

  return {
    initialize: initialize
  };
});
