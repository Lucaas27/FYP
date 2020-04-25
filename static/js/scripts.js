"use strict";

// Responsive nav bar
(function () {
	const navLinks = document.querySelector(".navbar-links");
	const navbar = document.querySelector("nav");
	const brand = document.querySelector(".brand-name");

	// Closes navbar after choosing a section link
	navbar.addEventListener("click", (event) => {
		if (event.target !== navbar && event.target !== brand) {
			// console.log(event.target);
			navLinks.classList.toggle("active");
		}
	});
})();
