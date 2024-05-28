// PROFILE DROPDOWN
const profile = document.querySelector(".profile");
const imgProfile = profile.querySelector("img");
const dropdownProfile = profile.querySelector(".profile-link");

imgProfile.addEventListener("click", function () {
  dropdownProfile.classList.toggle("show");
});



