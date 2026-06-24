(function () {
  var noteStyles = new Set(["tucked", "gutter", "stacked", "proof", "whisper"]);
  var noteAliases = { wispr: "whisper" };
  var params = new URLSearchParams(window.location.search);
  var requestedNotes = (params.get("notes") || "whisper").toLowerCase();
  var notes = noteAliases[requestedNotes] || requestedNotes;
  notes = noteStyles.has(notes) ? notes : "whisper";
  document.body.dataset.notes = notes;

  var tools = document.querySelector("[data-tools]");
  var trigger = document.querySelector(".tool-trigger");
  var searchButton = document.querySelector('[data-tool="search"]');
  var copyButton = document.querySelector('[data-tool="copy"]');
  var searchPanel = document.querySelector("[data-search-panel]");
  var searchInput = document.querySelector("[data-search-input]");
  var searchClose = document.querySelector("[data-search-close]");
  var searchStatus = document.querySelector("[data-search-status]");
  var toast = document.querySelector("[data-toast]");
  var posts = Array.prototype.slice.call(document.querySelectorAll("[data-post-list] li"));
  var toastTimer;

  function setMenuExpanded(expanded) {
    if (!tools || !trigger) return;
    tools.dataset.expanded = expanded ? "true" : "false";
    trigger.setAttribute("aria-expanded", expanded ? "true" : "false");
  }

  function showSearch() {
    if (!searchPanel || !searchInput) return;
    searchPanel.hidden = false;
    window.requestAnimationFrame(function () {
      searchPanel.classList.add("is-open");
      searchInput.focus();
      searchInput.select();
    });
    setMenuExpanded(false);
  }

  function hideSearch() {
    if (!searchPanel || !searchInput) return;
    searchInput.value = "";
    filterPosts("");
    searchPanel.classList.remove("is-open");
    window.setTimeout(function () {
      searchPanel.hidden = true;
    }, 140);
  }

  function filterPosts(query) {
    var needle = query.trim().toLowerCase();
    var visible = 0;
    if (needle) {
      document.body.dataset.searching = "true";
    } else {
      delete document.body.dataset.searching;
    }

    posts.forEach(function (post) {
      var title = post.querySelector(".post-title");
      var haystack = ((title && title.textContent) || "").toLowerCase();
      var match = !needle || haystack.indexOf(needle) !== -1;
      post.hidden = !match;
      if (match) visible += 1;
    });

    if (searchStatus) {
      searchStatus.textContent = needle ? visible + " of " + posts.length : "";
    }
  }

  async function copyAllPosts() {
    try {
      var response = await fetch("/all.txt", { cache: "no-store" });
      if (!response.ok) throw new Error("Could not fetch all.txt");
      var text = await response.text();
      await navigator.clipboard.writeText(text);
      showToast("Copied all posts");
    } catch (error) {
      showToast("Opened all.txt");
      window.open("/all.txt", "_blank", "noopener");
    } finally {
      setMenuExpanded(false);
    }
  }

  function showToast(message) {
    if (!toast) return;
    window.clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add("is-visible");
    toastTimer = window.setTimeout(function () {
      toast.classList.remove("is-visible");
    }, 1800);
  }

  if (trigger) {
    trigger.addEventListener("click", function () {
      setMenuExpanded(tools && tools.dataset.expanded !== "true");
    });
  }

  if (searchButton) searchButton.addEventListener("click", showSearch);
  if (copyButton) copyButton.addEventListener("click", copyAllPosts);
  if (searchClose) searchClose.addEventListener("click", hideSearch);
  if (searchInput) searchInput.addEventListener("input", function () {
    filterPosts(searchInput.value);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && searchPanel && !searchPanel.hidden) {
      hideSearch();
    }
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      showSearch();
    }
  });

  document.addEventListener("click", function (event) {
    if (tools && !tools.contains(event.target)) {
      setMenuExpanded(false);
    }
  });
})();
