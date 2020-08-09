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
$(document).ready(function () {
  $("body").on("click", '[data-toggle="modal"][data-remote]', function () {
    $($(this).data("target") + " .modal-body").load($(this).data("remote"));
  });
});

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

// Ajax call to delete items in the cart
$(document).ready(function () {
  $("a[itemId]").each(function () {
    $(this).click(function () {
      let itemId = $(this).attr("itemId");
      url = `${window.origin}/delete_cart`;
      data = { item_id: itemId };
      $.ajax({
        type: "POST",
        url: url,
        dataType: "json",
        data: JSON.stringify(data),
        contentType: "application/json; charset=UTF-8",
        success: function (data) {
          $(`#cartItem${itemId}`).fadeOut(1000, function () {
            $(this).remove();
          });
          $("#total").text(`${data.total}`);
          console.log(data);
        },
        error: function (data) {
          if (data.status !== 200) {
            console.log(`Response status was not successful: ${data.status}`);
            return;
          }
        },
      });
    });
  });
});
// Fetch API to update quantity in the shopping cart
//  It sends a Post req to the view that will update
//  the subtotal and total according to what quantity the user chooses

(function () {
  // get all number inputs with itemId attribute where the value is not None
  let qtInput = document.querySelectorAll(
    'input[value][type="number"][itemId]:not([value=""])'
  );

  qtInput.forEach(function (el) {
    el.addEventListener("input", function () {
      let itemId = this.getAttribute("itemId");

      // check if value is not empty
      if (this.value) {
        // get number from total
        let total = parseFloat(
          document.querySelector("#total").textContent.trim(),
          10
        );

        entry = { quantity: this.value, item_id: itemId, total: total };
        fetch(`${window.origin}/update_cart`, {
          method: "POST",
          credentials: "include",
          body: JSON.stringify(entry),
          headers: new Headers({
            "content-type": "application/json",
          }),
        }).then(function (response) {
          // if response fail
          if (response.status !== 200) {
            console.log(
              `Response status was not successful: ${response.status}`
            );
            return;
          }
          // if response is successfull
          response.json().then(function (data) {
            $(`#subtotal${itemId}`).each(function () {
              $(this).text(`Subtotal: £ ${data.new_subtotal}`);
            });
            $("#total").text(`${data.new_total}`);
            // console.log(data);
            qtInput.forEach(function (el) {
              if (el.value > data.qt_available) {
                $(`#cartMessage${itemId}`).text(`Not enough units`);
              }
            });
          });
        });
      }
    });
  });
})();

(function () {
  
})();
