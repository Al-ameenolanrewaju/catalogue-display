// Main UI Interactions

document.addEventListener('DOMContentLoaded', function () {
  // 1. Device Preview Switcher (Desktop / Tablet / Mobile)
  const deviceButtons = document.querySelectorAll('[data-device-target]');
  const frameContainer = document.getElementById('deviceFrameTarget');

  if (deviceButtons.length && frameContainer) {
    const chromeHeader = document.getElementById('mockBrowserChrome');
    const mobileNotch = document.getElementById('mockMobileNotch');

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
          if (chromeHeader) chromeHeader.classList.remove('d-none');
          if (mobileNotch) mobileNotch.classList.add('d-none');
        } else if (mode === 'tablet') {
          frameContainer.classList.add('device-frame-tablet');
          if (chromeHeader) chromeHeader.classList.remove('d-none');
          if (mobileNotch) mobileNotch.classList.add('d-none');
        } else if (mode === 'mobile') {
          frameContainer.classList.add('device-frame-mobile');
          if (chromeHeader) chromeHeader.classList.add('d-none');
          if (mobileNotch) mobileNotch.classList.remove('d-none');
        }
      });
    });

    // Toggle live demo iframe inside frame if URL exists
    const btnToggleLiveDemo = document.getElementById('btnToggleLiveDemo');
    const liveIframe = document.getElementById('liveDemoIframe');
    const mainShowcaseImg = document.getElementById('mainShowcaseImage');
    const liveDemoBtnText = document.getElementById('liveDemoBtnText');

    if (btnToggleLiveDemo && liveIframe && mainShowcaseImg) {
      let isLiveActive = false;
      const demoUrl = "{{ project.live_demo_url if project is defined else '' }}";

      btnToggleLiveDemo.addEventListener('click', function () {
        isLiveActive = !isLiveActive;
        if (isLiveActive) {
          if (!liveIframe.getAttribute('src') && window.location.pathname) {
            // fetch data from current page's target link if present
            const extLink = document.querySelector('a[title*="external live demo"]');
            if (extLink && extLink.href) {
              liveIframe.src = extLink.href;
            }
          }
          liveIframe.classList.remove('d-none');
          mainShowcaseImg.classList.add('d-none');
          if (liveDemoBtnText) liveDemoBtnText.textContent = 'View Screenshot';
          btnToggleLiveDemo.classList.add('btn-warning');
          btnToggleLiveDemo.classList.remove('btn-outline-warning');
        } else {
          liveIframe.classList.add('d-none');
          mainShowcaseImg.classList.remove('d-none');
          if (liveDemoBtnText) liveDemoBtnText.textContent = 'Live Interactive View';
          btnToggleLiveDemo.classList.remove('btn-warning');
          btnToggleLiveDemo.classList.add('btn-outline-warning');
        }
      });
    }
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
