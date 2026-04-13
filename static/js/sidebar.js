document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarClose = document.getElementById('sidebarClose');
  const mainContent = document.getElementById('mainContent');

  let hideTimer;
  const HIDE_DELAY = 2000; // Time in ms before hiding (2 seconds)

  // Function to show the toggle button
  function showToggle() {
    if (window.innerWidth < 768 && !sidebar.classList.contains('show')) {
      sidebarToggle.classList.add('visible');
      resetHideTimer();
    }
  }

  // Function to hide the toggle button
  function hideToggle() {
    sidebarToggle.classList.remove('visible');
  }

  // Reset the timer
  function resetHideTimer() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(hideToggle, HIDE_DELAY);
  }

  // Initialize: Show button immediately on load
  showToggle();

  // Event Listeners for Activity Detection
  const activityEvents = ['mousemove', 'mousedown', 'touchstart', 'scroll', 'keydown'];

  activityEvents.forEach(event => {
    document.addEventListener(event, () => {
      // Only show if sidebar is closed
      if (!sidebar.classList.contains('show')) {
        showToggle();
      }
    }, true); // Use capture phase to catch events early
  });

  // Toggle sidebar logic
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function(e) {
      e.stopPropagation(); // Prevent triggering the document click listener immediately
      const isOpen = sidebar.classList.contains('show');

      if (isOpen) {
        sidebar.classList.remove('show');
        document.body.classList.remove('sidebar-open');
        // Show button again immediately after closing
        showToggle();
      } else {
        sidebar.classList.add('show');
        document.body.classList.add('sidebar-open');
        // Hide button immediately when opening sidebar
        hideToggle();
      }
    });
  }

  // Close sidebar when clicking close button
  if (sidebarClose) {
    sidebarClose.addEventListener('click', function(e) {
      e.stopPropagation();
      sidebar.classList.remove('show');
      document.body.classList.remove('sidebar-open');
      showToggle(); // Show button again
    });
  }

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', function(event) {
    if (window.innerWidth < 768 && sidebar.classList.contains('show')) {
      if (!sidebar.contains(event.target) && event.target !== sidebarToggle) {
        sidebar.classList.remove('show');
        document.body.classList.remove('sidebar-open');
        showToggle(); // Show button again
      }
    }
  });

  // Handle window resize
  window.addEventListener('resize', function() {
    clearTimeout(hideTimer);
    if (window.innerWidth >= 768) {
      sidebar.classList.remove('show');
      document.body.classList.remove('sidebar-open');
      sidebarToggle.classList.remove('visible');
    } else {
      sidebar.classList.remove('show');
      document.body.classList.remove('sidebar-open');
      showToggle();
    }
  });
});