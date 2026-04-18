document.addEventListener('DOMContentLoaded', () => {
  const updateTopbarState = () => {
    document.body.classList.toggle('topbar-scrolled', window.scrollY > 8);
  };

  updateTopbarState();
  window.addEventListener('scroll', updateTopbarState, { passive: true });
});
