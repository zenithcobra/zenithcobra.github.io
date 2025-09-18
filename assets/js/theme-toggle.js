(function (window, document) {
  'use strict';

  const THEME_KEY = 'theme'; // Key for localStorage
  const DARK_MODE_CLASS = 'dark-mode'; // Class to apply for dark mode
  const LIGHT_MODE_CLASS = 'light-mode'; // Class to apply for light mode
  const LIGHT_BG_IMAGE = 'images/9.jpg'; // Background image for light mode
  const DARK_BG_IMAGE = 'images/9gimp.jpg'; // Background image for dark mode

  // Apply the saved theme on page load
  function applySavedTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme === 'dark') {
      document.body.classList.add(DARK_MODE_CLASS);
      document.body.classList.remove(LIGHT_MODE_CLASS);
      updateBackgroundImage(DARK_BG_IMAGE);
    } else {
      document.body.classList.add(LIGHT_MODE_CLASS);
      document.body.classList.remove(DARK_MODE_CLASS);
      updateBackgroundImage(LIGHT_BG_IMAGE);
    }
  }

  // Toggle between dark and light mode
  function toggleTheme() {
    if (document.body.classList.contains(DARK_MODE_CLASS)) {
      document.body.classList.remove(DARK_MODE_CLASS);
      document.body.classList.add(LIGHT_MODE_CLASS);
      localStorage.setItem(THEME_KEY, 'light');
      updateBackgroundImage(LIGHT_BG_IMAGE);
    } else {
      document.body.classList.remove(LIGHT_MODE_CLASS);
      document.body.classList.add(DARK_MODE_CLASS);
      localStorage.setItem(THEME_KEY, 'dark');
      updateBackgroundImage(DARK_BG_IMAGE);
    }
  }

  // Update the background image
  function updateBackgroundImage(imagePath) {
    document.body.style.backgroundImage = `url('${imagePath}')`;
  }

  // Initialize the theme toggle functionality
  function initThemeToggle() {
    // Select all elements with the class "theme-toggle"
    const themeToggleButtons = document.querySelectorAll('.theme-toggle');
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