const stars = document.querySelectorAll(".star-rating .star");
stars.forEach((star) => {
  star.addEventListener("mouseover", () => {
    const siblings = [...star.parentElement.children];
    siblings.forEach((sib) => {
      if (sib.nodeName === "LABEL") {
        sib.style.color = "#ddd";
      }
    });
    star.style.color = "#ffcc00";
    let prev = star.previousElementSibling;
    while (prev) {
      if (prev.nodeName === "LABEL") {
        prev.style.color = "#ffcc00";
      }
      prev = prev.previousElementSibling;
    }
  });

  star.addEventListener("mouseout", () => {
    const checkedStar = star.parentElement.querySelector("input:checked + label");
    if (checkedStar) {
      const siblings = [...checkedStar.parentElement.children];
      siblings.forEach((sib) => {
        if (sib.nodeName === "LABEL") {
          sib.style.color = "#ddd";
        }
      });
      checkedStar.style.color = "#ffcc00";
      let prev = checkedStar.previousElementSibling;
      while (prev) {
        if (prev.nodeName === "LABEL") {
          prev.style.color = "#ffcc00";
        }
        prev = prev.previousElementSibling;
      }
    } else {
      const siblings = [...star.parentElement.children];
      siblings.forEach((sib) => {
        if (sib.nodeName === "LABEL") {
          sib.style.color = "#ddd";
        }
      });
    }
  });
});
