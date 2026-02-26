<script>
(function () {
  var lang = (navigator.language || navigator.userLanguage || "en")
               .substring(0, 2).toLowerCase();
  window.location.replace(
    lang === "de"
      ? "/BadWeatherMountTester/de/"
      : "/BadWeatherMountTester/en/"
  );
})();
</script>

<noscript>
  <p>Please choose your language / Bitte wähle deine Sprache:</p>
  <ul>
    <li><a href="/BadWeatherMountTester/en/">English</a></li>
    <li><a href="/BadWeatherMountTester/de/">Deutsch</a></li>
  </ul>
</noscript>
