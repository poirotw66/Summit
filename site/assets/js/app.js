(function () {
  const search = document.getElementById("search");
  const filterBtns = document.querySelectorAll(".filter-btn");
  const resultCount = document.getElementById("result-count");
  const emptyState = document.getElementById("empty-state");
  const featuredSection = document.getElementById("featured-section");
  const categorySections = Array.from(document.querySelectorAll(".category-section"));

  let activeFilter = "all";

  function cardMatches(card, q) {
    const summit = card.dataset.summit || "";
    const haystack = (
      (card.dataset.title || "") + " " +
      (card.dataset.speaker || "") + " " +
      (card.dataset.tags || "")
    ).toLowerCase();

    const matchesFilter = activeFilter === "all" || summit === activeFilter;
    const matchesSearch = q === "" || haystack.includes(q);
    return matchesFilter && matchesSearch;
  }

  function applyFilters() {
    const q = (search && search.value ? search.value : "").trim().toLowerCase();

    // Featured section: filter its own cards, hide whole section if nothing matches.
    let featuredVisible = 0;
    if (featuredSection) {
      featuredSection.querySelectorAll(".card").forEach((card) => {
        const show = cardMatches(card, q);
        card.style.display = show ? "" : "none";
        if (show) featuredVisible++;
      });
      featuredSection.hidden = featuredVisible === 0;
    }

    // Category sections contain every talk exactly once; used for the result count.
    let visible = 0;
    categorySections.forEach((section) => {
      let sectionVisible = 0;
      section.querySelectorAll(".card").forEach((card) => {
        const show = cardMatches(card, q);
        card.style.display = show ? "" : "none";
        if (show) sectionVisible++;
      });
      section.hidden = sectionVisible === 0;
      visible += sectionVisible;
    });

    const total = categorySections.reduce(
      (sum, section) => sum + section.querySelectorAll(".card").length,
      0
    );

    if (resultCount) {
      resultCount.textContent = `顯示 ${visible} / ${total} 場議程`;
    }
    if (emptyState) {
      emptyState.hidden = visible !== 0;
    }
  }

  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeFilter = btn.dataset.filter;
      applyFilters();
    });
  });

  if (search) {
    search.addEventListener("input", applyFilters);
  }

  applyFilters();
})();
