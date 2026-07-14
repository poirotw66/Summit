(function () {
  function init() {
    const search = document.getElementById("search");
    const filterBtns = document.querySelectorAll(".filter-btn");
    const resultCount = document.getElementById("result-count");
    const emptyState = document.getElementById("empty-state");
    const featuredSection = document.getElementById("featured-section");
    const featuredGroups = Array.from(document.querySelectorAll(".featured-group"));
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

      // Featured section: filter cards per summit group, hide a group (or the
      // whole section) when nothing in it matches.
      let featuredVisible = 0;
      featuredGroups.forEach((group) => {
        let groupVisible = 0;
        group.querySelectorAll(".card").forEach((card) => {
          const show = cardMatches(card, q);
          card.style.display = show ? "" : "none";
          if (show) groupVisible++;
        });
        group.hidden = groupVisible === 0;
        featuredVisible += groupVisible;
      });
      if (featuredSection) {
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

    // ScrollSpy for TOC links
    const tocLinks = document.querySelectorAll(".toc-link");
    const sections = Array.from(document.querySelectorAll("section[id]"));

    if (tocLinks.length > 0 && sections.length > 0) {
      function activeTOC() {
        let index = sections.length;
        while (--index && window.scrollY + 100 < sections[index].offsetTop) {}
        tocLinks.forEach((link) => link.classList.remove("active"));
        if (sections[index]) {
          const activeId = sections[index].getAttribute("id");
          const activeLink = document.querySelector(`.toc-link[href="#${activeId}"]`);
          if (activeLink) activeLink.classList.add("active");
        }
      }
      window.addEventListener("scroll", activeTOC);
      activeTOC();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
