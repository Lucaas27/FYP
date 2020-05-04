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

// Index page different views
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

