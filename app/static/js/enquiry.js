// Enquiry & Customisation Add-on Interactive Calculator

document.addEventListener('DOMContentLoaded', function () {
  const packageSelect = document.getElementById('enquiryPackageSelect');
  const addonCheckboxes = document.querySelectorAll('.addon-checkbox');
  const estimateTotalElement = document.getElementById('liveEstimatedTotal');
  const packageCostElement = document.getElementById('livePackageCost');
  const addonsCostElement = document.getElementById('liveAddonsCost');

  function calculateEstimate() {
    let packageCost = 0;
    let addonsCost = 0;
    let isCustom = false;

    // Package cost
    if (packageSelect) {
      const selectedOption = packageSelect.options[packageSelect.selectedIndex];
      const priceAttr = selectedOption.getAttribute('data-price');
      if (priceAttr && priceAttr !== 'null' && !isNaN(parseFloat(priceAttr))) {
        packageCost = parseFloat(priceAttr);
      } else if (selectedOption.value) {
        isCustom = true;
      }
    }

    // Addons cost
    addonCheckboxes.forEach(cb => {
      const parentCard = cb.closest('.addon-selection-card');
      if (cb.checked) {
        if (parentCard) parentCard.classList.add('selected');
        const price = parseFloat(cb.getAttribute('data-price') || 0);
        if (!isNaN(price)) {
          addonsCost += price;
        }
      } else {
        if (parentCard) parentCard.classList.remove('selected');
      }
    });

    const grandTotal = packageCost + addonsCost;

    if (packageCostElement) {
      packageCostElement.textContent = packageCost > 0 
        ? '₦' + packageCost.toLocaleString() 
        : (isCustom ? 'Custom Quote' : '₦0');
    }

    if (addonsCostElement) {
      addonsCostElement.textContent = '₦' + addonsCost.toLocaleString();
    }

    if (estimateTotalElement) {
      if (grandTotal > 0) {
        estimateTotalElement.textContent = '₦' + grandTotal.toLocaleString();
      } else if (isCustom) {
        estimateTotalElement.textContent = 'Custom Quotation';
      } else {
        estimateTotalElement.textContent = 'Select Package to Calculate';
      }
    }
  }

  if (packageSelect) {
    packageSelect.addEventListener('change', calculateEstimate);
  }

  addonCheckboxes.forEach(cb => {
    cb.addEventListener('change', calculateEstimate);
    const parentCard = cb.closest('.addon-selection-card');
    if (parentCard) {
      parentCard.addEventListener('click', function (e) {
        if (e.target !== cb) {
          cb.checked = !cb.checked;
          cb.dispatchEvent(new Event('change'));
        }
      });
    }
  });

  // Initial calculation on page load
  calculateEstimate();
});
