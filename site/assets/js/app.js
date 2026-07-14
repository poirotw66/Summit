(function () {
  const grid = document.getElementById("grid");
  const cards = grid ? Array.from(grid.querySelectorAll(".card")) : [];
  const search = document.getElementById("search");
  const filterBtns = document.querySelectorAll(".filter-btn");
  const resultCount = document.getElementById("result-count");
  const emptyState = document.getElementById("empty-state");

  let activeFilter = "all";

  function applyFilters() {
    const q = (search && search.value ? search.value : "").trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const summit = card.dataset.summit || "";
      const haystack = (
        (card.dataset.title || "") + " " +
        (card.dataset.speaker || "") + " " +
        (card.dataset.tags || "")
      ).toLowerCase();

      const matchesFilter = activeFilter === "all" || summit === activeFilter;
      const matchesSearch = q === "" || haystack.includes(q);
      const show = matchesFilter && matchesSearch;

      card.style.display = show ? "" : "none";
      if (show) visible++;
    });

    if (resultCount) {
      resultCount.textContent = `顯示 ${visible} / ${cards.length} 場議程`;
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
