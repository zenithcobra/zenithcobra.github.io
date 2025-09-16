(function (window, document) {
  'use strict';

  const THEME_KEY = 'theme'; // Key for localStorage
  const DARK_MODE_CLASS = 'dark-mode'; // Class to apply for dark mode
  const LIGHT_MODE_CLASS = 'light-mode'; // Class to apply for light mode
  const LOGO_SELECTOR = '.logo img'; // Selector for the logo image
  const LIGHT_LOGO_SRC = 'images/logo.svg'; // Path to the light mode logo
  const DARK_LOGO_SRC = 'images/logo-dark.svg'; // Path to the dark mode logo

  // Apply the saved theme on page load
  function applySavedTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme === 'dark') {
      document.body.classList.add(DARK_MODE_CLASS);
      document.body.classList.remove(LIGHT_MODE_CLASS);
      updateLogo(DARK_LOGO_SRC);
    } else {
      document.body.classList.add(LIGHT_MODE_CLASS);
      document.body.classList.remove(DARK_MODE_CLASS);
      updateLogo(LIGHT_LOGO_SRC);
    }
  }

  // Toggle between dark and light mode
  function toggleTheme() {
    if (document.body.classList.contains(DARK_MODE_CLASS)) {
      document.body.classList.remove(DARK_MODE_CLASS);
      document.body.classList.add(LIGHT_MODE_CLASS);
      localStorage.setItem(THEME_KEY, 'light');
      updateLogo(LIGHT_LOGO_SRC);
    } else {
      document.body.classList.remove(LIGHT_MODE_CLASS);
      document.body.classList.add(DARK_MODE_CLASS);
      localStorage.setItem(THEME_KEY, 'dark');
      updateLogo(DARK_LOGO_SRC);
    }
  }

  // Update the logo based on the theme
  function updateLogo(src) {
    const logo = document.querySelector(LOGO_SELECTOR);
    if (logo) {
      logo.src = src;
    }
  }

  // Initialize the theme toggle functionality
  function initThemeToggle() {
    // Select all elements with the id or class for toggling
    const themeToggleButtons = document.querySelectorAll('#theme-toggle, .theme-toggle');
    themeToggleButtons.forEach((button) => {
      button.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent default link behavior
        toggleTheme();
      });
    });

    applySavedTheme();
  }

  // Run the initialization on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeToggle);
  } else {
    initThemeToggle();
  }
})(window, document);