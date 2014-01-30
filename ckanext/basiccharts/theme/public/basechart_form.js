$('.formFilters-addFilter').click(function (evt) {
  evt.preventDefault();
  $(".formFilters").append($(templateFilterInputs));
});

$(document).on('click', '.formFilters-removeFilter', function (evt) {
  evt.preventDefault();
  $(this).parent().remove();
});
