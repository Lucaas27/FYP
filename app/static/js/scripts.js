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

  const activeTab = localStorage.getItem("activeTab");
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

// Attach modal-body from different template using ajax calls and data-remote url
// $(document).ready(function () {
//   $(".btn-action").click(function () {
//     var url = $(this).data("remote");
//     $.ajax({
//       type: "GET",
//       url: url,
//       dataType: "json",
//       success: function (res) {
//         // get the ajax response data
//         var data = res.body;
//         // update modal content
//         $(".modal-body").text(data.someval);
//         // show modal
//         $("#myModal").modal("show");
//       },
//       error: function (request, status, error) {
//         console.log("ajax call went wrong:" + request.responseText);
//       },
//     });
//   });
// });

// Gallery on Item details page
$(document).ready(function () {
  $(".thumbnails img").click(function () {
    const attr = $(this).attr("src");
    const src = $("#largeImage").attr("src");
    $("#largeImage").attr("src", attr);
    $(this).attr("src", src);
  });
});
