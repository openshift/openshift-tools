// Since the CSP prevents use of onload, this gives us the same functionality
// without a violation of the CSP
document.addEventListener('DOMContentLoaded', function () {
  document.getElementsByTagName('input')[0].click();
});
