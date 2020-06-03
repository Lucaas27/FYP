// Close alerts
$(document).ready(function () {
  window.setTimeout(function () {
    $(".alert")
      .fadeTo(1000, 0)
      .slideUp(500, function () {
        $(this).remove();
      });
  }, 2500);
});

// Different views in the index page(grid and list)
$(document).ready(function () {
  $("#list").click(function (event) {
    event.preventDefault();
    $("#products .item").addClass("list-group-item");
  });
  $("#grid").click(function (event) {
    event.preventDefault();
    $("#products .item").removeClass("list-group-item");
    $("#products .item").addClass("grid-group-item");
  });
});

// Slider text effect
$(document).ready(function () {
  wow = new WOW({
    animateClass: "animated",
    offset: 100,
  });
  wow.init();
});

// keep the same tab after refreshing the page, using local storage
$(document).ready(function () {
  $('a[data-toggle="tab"]').on("shown.bs.tab", function (e) {
    localStorage.setItem("activeTab", $(e.target).attr("href"));
  });

  var activeTab = localStorage.getItem("activeTab");
  if (activeTab) {
    $('.nav-tabs a[href="' + activeTab + '"]').tab("show");
  }
});


// Attach modal-body from different template using data-remote url
// $(document).ready(function () {
//   $("body").on("click", '[data-toggle="modal"][data-remote]', function () {
//     $($(this).data("target") + " .modal-body").load($(this).data("remote"));
//   });
// });
