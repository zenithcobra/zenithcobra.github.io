(function (window, document) {
  'use strict';

  const THEME_KEY = 'theme'; // Key for localStorage
  const DARK_MODE_CLASS = 'dark-mode'; // Class to apply for dark mode
  const LIGHT_MODE_CLASS = 'light-mode'; // Class to apply for light mode

  // Apply the saved theme on page load
  function applySavedTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme === 'dark') {
      document.body.classList.add(DARK_MODE_CLASS);
      document.body.classList.remove(LIGHT_MODE_CLASS);
    } else {
      document.body.classList.add(LIGHT_MODE_CLASS);
      document.body.classList.remove(DARK_MODE_CLASS);
    }
  }

  // Toggle between dark and light mode
  function toggleTheme() {
    if (document.body.classList.contains(DARK_MODE_CLASS)) {
      document.body.classList.remove(DARK_MODE_CLASS);
      document.body.classList.add(LIGHT_MODE_CLASS);
      localStorage.setItem(THEME_KEY, 'light');
    } else {
      document.body.classList.remove(LIGHT_MODE_CLASS);
      document.body.classList.add(DARK_MODE_CLASS);
      localStorage.setItem(THEME_KEY, 'dark');
    }
  }

  // Initialize the theme toggle functionality
  function initThemeToggle() {
    const themeToggleButton = document.getElementById('theme-toggle');
    if (themeToggleButton) {
      themeToggleButton.addEventListener('click', toggleTheme);
    }
    applySavedTheme();
  }

  // Run the initialization on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeToggle);
  } else {
    initThemeToggle();
  }
})(window, document);