(function () {
  const input = document.querySelector("#people-search");
  if (!input) return;
  const groups = document.querySelectorAll("[data-letter-group]");
  const favorites = document.querySelector("[data-favorites]");
  const empty = document.querySelector("#empty-search");

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    groups.forEach((group) => {
      let visible = 0;
      group.querySelectorAll("[data-person]").forEach((row) => {
        const haystack = row.dataset.person || "";
        const show = !query || haystack.includes(query);
        row.hidden = !show;
        if (show) visible += 1;
      });
      group.hidden = visible === 0;
    });
    if (favorites) {
      const visibleFavorites = favorites.querySelectorAll("[data-person]:not([hidden])");
      favorites.hidden = query.length > 0 || visibleFavorites.length === 0;
    }
    if (empty) {
      const anyGroup = document.querySelector("[data-letter-group]:not([hidden])");
      empty.hidden = Boolean(anyGroup) || !query;
    }
  });
})();
