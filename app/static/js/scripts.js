"use strict";

// Responsive nav bar
(function () {
	const navbarLinks = document.querySelector(".navbar .navbar-links");
	const toggleButton = document.querySelector("ion-icon");
	const navBarContainer = document.querySelector(".navbar");
	// Open and closes menu nav
	const menu = () => {
		navbarLinks.classList.toggle("active");
	};

	// listens fot clicks on the hamburguer menu and calls the menu function
	toggleButton.addEventListener("click", menu);

	// Closes menu if the menu or navlinks are clicked
	navBarContainer.addEventListener("click", (event) => {
		//   console.log(event.target);
		if (event.target !== navbarLinks && event.target !== toggleButton) {
			menu();
		}
	});
})();

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

// Number spinner
$(document).on("click", ".number-spinner button", function () {
	var btn = $(this),
		oldValue = btn.closest(".number-spinner").find("input").val().trim(),
		newVal = 0;

	if (btn.attr("data-dir") == "up") {
		newVal = parseInt(oldValue) + 1;
	} else {
		if (oldValue > 1) {
			newVal = parseInt(oldValue) - 1;
		} else {
			newVal = 1;
		}
	}
	btn.closest(".number-spinner").find("input").val(newVal);
});
