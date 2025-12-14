module.exports = {
  content: ["_site/**/*.html", "_site/**/*.js"],
  css: ["_site/assets/css/*.css"],
  output: "_site/assets/css/",
  skippedContentGlobs: ["_site/assets/**/*.html"],
  safelist: [
    // Author highlight classes (dynamically added via Liquid)
    "first-author",
    "corresponding-author",
    // Filter classes (added via JavaScript)
    "filter-first-author",
    "filter-corresponding-author",
    "active",
    // Selected papers section
    "selected-papers",
  ],
};
