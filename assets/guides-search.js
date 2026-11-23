/* SolutionHub — guides index search/filter.
   Plain client-side filter, no backend, no third-party code.
   Matches each guide on its title + description, hides empty groups,
   and keeps a "Showing X of 12 guides" count. Works with JS off too:
   without this file every guide simply stays visible. */
(function () {
  var input = document.getElementById("guide-search");
  var count = document.getElementById("guide-count");
  var empty = document.getElementById("guide-empty");
  if (!input || !count || !empty) return;

  var entries = Array.prototype.slice.call(
    document.querySelectorAll(".contents .entry"),
  );
  var total = entries.length;

  function apply() {
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    entries.forEach(function (el) {
      var hit = !q || el.textContent.toLowerCase().indexOf(q) !== -1;
      el.hidden = !hit;
      if (hit) shown++;
    });
    // Hide a group heading (and its list) when none of its guides match.
    Array.prototype.forEach.call(
      document.querySelectorAll(".group-head"),
      function (head) {
        var list = head.nextElementSibling;
        var any = false;
        if (list) {
          Array.prototype.forEach.call(
            list.querySelectorAll(".entry"),
            function (el) {
              if (!el.hidden) any = true;
            },
          );
          list.hidden = !any;
        }
        head.hidden = !any;
      },
    );
    count.textContent = "Showing " + shown + " of " + total + " guides";
    empty.hidden = shown !== 0;
  }

  input.addEventListener("input", apply);
  apply();
})();
