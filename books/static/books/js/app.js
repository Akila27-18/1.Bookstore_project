// Simple helper to preserve query params on selects
(function(){
const selects = document.querySelectorAll('[data-submit-on-change]');
selects.forEach(sel => sel.addEventListener('change', () => sel.form.submit()));
})();