// Main UI Interactions

document.addEventListener('DOMContentLoaded', function () {
  // 1. Device Preview Switcher (Desktop / Tablet / Mobile)
  const deviceButtons = document.querySelectorAll('[data-device-target]');
  const frameContainer = document.getElementById('deviceFrameTarget');

  if (deviceButtons.length && frameContainer) {
    deviceButtons.forEach(btn => {
      btn.addEventListener('click', function () {
        deviceButtons.forEach(b => b.classList.remove('active', 'btn-charcoal'));
        deviceButtons.forEach(b => b.classList.add('btn-outline-secondary'));

        this.classList.remove('btn-outline-secondary');
        this.classList.add('active', 'btn-charcoal');

        const mode = this.getAttribute('data-device-target');
        frameContainer.classList.remove('device-frame-desktop', 'device-frame-tablet', 'device-frame-mobile');

        if (mode === 'desktop') {
          frameContainer.classList.add('device-frame-desktop');
        } else if (mode === 'tablet') {
          frameContainer.classList.add('device-frame-tablet');
        } else if (mode === 'mobile') {
          frameContainer.classList.add('device-frame-mobile');
        }
      });
    });
  }

  // 2. Thumbnail Switcher for Showcase Detail Gallery
  const thumbnails = document.querySelectorAll('.gallery-thumb-btn');
  const mainImage = document.getElementById('mainShowcaseImage');

  if (thumbnails.length && mainImage) {
    thumbnails.forEach(thumb => {
      thumb.addEventListener('click', function () {
        thumbnails.forEach(t => t.classList.remove('border-primary', 'border-2'));
        this.classList.add('border-primary', 'border-2');
        const newSrc = this.getAttribute('data-full-img');
        if (newSrc) {
          mainImage.src = newSrc;
        }
      });
    });
  }

  // 3. Share URL Clipboard Copy
  const copyButtons = document.querySelectorAll('.btn-copy-link');
  copyButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const url = window.location.href;
      navigator.clipboard.writeText(url).then(() => {
        const originalText = this.innerHTML;
        this.innerHTML = '<i class="bi bi-check2"></i> Copied!';
        setTimeout(() => {
          this.innerHTML = originalText;
        }, 2000);
      });
    });
  });

  // 4. Auto-dismiss alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 6000);
  });
});
