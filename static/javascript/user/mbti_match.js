document.addEventListener("DOMContentLoaded", function () {
  const filterTags = document.querySelectorAll(".filter-tag");

  filterTags.forEach((tag) => {
    tag.addEventListener("click", function () {
      // Remove active class from all tags
      filterTags.forEach((tag) => tag.classList.remove("active"));
      // Add active class to the clicked tag
      this.classList.add("active");
    });
  });
});
