'use strict';

const switcher = document.querySelector('.btn');

function setTheme(theme) {
    const isDark = theme === 'dark-theme';
    document.body.classList.toggle('dark-theme', isDark);
    document.body.classList.toggle('light-theme', !isDark);
    switcher.textContent = isDark ? 'Light' : 'Dark';
}

switcher.addEventListener('click', function() {
    const nextTheme = document.body.classList.contains('dark-theme')
        ? 'light-theme'
        : 'dark-theme';

    setTheme(nextTheme);
});

setTheme(document.body.classList.contains('dark-theme') ? 'dark-theme' : 'light-theme');